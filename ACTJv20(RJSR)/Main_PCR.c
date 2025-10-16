/********************************************************************
 FileName:		main.c
 Dependencies:	See INCLUDES section
 Processor:		PIC18 or PIC24 USB Microcontrollers
 Hardware:		
 Complier:  	Microchip C18 (for PIC18) or C30 (for PIC24)
 ********************************************************************
 File Description:

 Change History:
  Rev   Date         Description

********************************************************************/

/** INCLUDES *******************************************************/
#include<p18cxxx.h>
#include "Functions.h"
#include "i2c_lcd.h"
#include "SBC_Rpi.h"
#include "service.h"

#define	PICDEM_FS_USB
#define Stop_Command 'Z'
#define offset 0x046		//resolution= 0.0283 degree celsius. so 70x0.0283=1.981 degree celsius


/** CONFIGURATION **************************************************/

        #pragma config PLLDIV   = 5         // (20 MHz crystal)
        #pragma config CPUDIV   = OSC1_PLL2   
        #pragma config USBDIV   = 2         // Clock source from 96MHz PLL/2
        #pragma config FOSC     = HSPLL_HS
        #pragma config FCMEN    = OFF
        #pragma config IESO     = OFF
        #pragma config PWRT     = ON
        #pragma config BOR      = ON
        #pragma config BORV     = 0   //prev. 3
        #pragma config VREGEN   = OFF      //USB Voltage Regulator //prev ON
        #pragma config WDT      = OFF
        #pragma config WDTPS    = 32768
        #pragma config MCLRE    = ON
        #pragma config LPT1OSC  = OFF
        #pragma config PBADEN   = OFF
//      #pragma config CCP2MX   = ON
        #pragma config STVREN   = ON
        #pragma config LVP      = OFF
//      #pragma config ICPRT    = OFF       // Dedicated In-Circuit Debug/Programming
        #pragma config XINST    = OFF       // Extended Instruction Set
        #pragma config CP0      = ON
        #pragma config CP1      = ON
    	#pragma config CP2      = ON
	    #pragma config CP3      = ON
        #pragma config CPB      = OFF
//      #pragma config CPD      = OFF
        #pragma config WRT0     = OFF
        #pragma config WRT1     = OFF
//      #pragma config WRT2     = OFF
//      #pragma config WRT3     = OFF
        #pragma config WRTB     = OFF       // Boot Block Write Protection
        #pragma config WRTC     = OFF
//      #pragma config WRTD     = OFF
        #pragma config EBTR0    = OFF
        #pragma config EBTR1    = OFF
//      #pragma config EBTR2    = OFF
//      #pragma config EBTR3    = OFF
        #pragma config EBTRB    = OFF



#pragma romdata dataEEPROM=0xF00000
rom unsigned char FirstByte[3]={0,20,0};	//EEPROM

void YourHighPriorityISRCode(void);
void YourLowPriorityISRCode(void);
void delay_test(void);//113mS

unsigned int TM=0,C_BaseValue=0,BaseValue=0;
unsigned long count=0, pass_count=0;
unsigned char RtryValve_HF,error_type,testing=0;


void delaysec(unsigned int , unsigned int, unsigned int, unsigned int );
void delaysec50(unsigned int , unsigned int, unsigned int, unsigned int );
void delaysecLEDOFF(unsigned int, unsigned int, unsigned int, unsigned int);
void OffsetCorrection(unsigned int,unsigned int,unsigned int);
void Status_Reaction_Run(void);
void Status_Reaction_End(void);
char VacuumTest(void);
char ValveTest(void);
void main(void);
void port_init(void);
void reset_mechanism(void);
char cat_test(void);
void check_key_intrpt(void);
void check_stack(void);
void mech_plate_down(void);
void mechUp_catFB_Back(void);
void catFB_forward(void);
void reject_off(void);
void reject_on(void);
void mech_error_loop(void);

	#define REMAPPED_RESET_VECTOR_ADDRESS			0x800
	#define REMAPPED_HIGH_INTERRUPT_VECTOR_ADDRESS	0x808
	#define REMAPPED_LOW_INTERRUPT_VECTOR_ADDRESS	0x818
	
	
	extern void _startup (void);        // See c018i.c in your C18 compiler dir
	#pragma code REMAPPED_RESET_VECTOR = REMAPPED_RESET_VECTOR_ADDRESS
	void _reset (void)
	{
	    _asm goto _startup _endasm
	}

	#pragma code REMAPPED_HIGH_INTERRUPT_VECTOR = REMAPPED_HIGH_INTERRUPT_VECTOR_ADDRESS
	void Remapped_High_ISR (void)
	{
	     _asm goto YourHighPriorityISRCode _endasm
	}
	#pragma code REMAPPED_LOW_INTERRUPT_VECTOR = REMAPPED_LOW_INTERRUPT_VECTOR_ADDRESS
	void Remapped_Low_ISR (void)
	{
	     _asm goto YourLowPriorityISRCode _endasm
	}
	
	
	#pragma code HIGH_INTERRUPT_VECTOR = 0x08
	void High_ISR (void)
	{
	     _asm goto REMAPPED_HIGH_INTERRUPT_VECTOR_ADDRESS _endasm
	}
	#pragma code LOW_INTERRUPT_VECTOR = 0x18
	void Low_ISR (void)
	{
	     _asm goto REMAPPED_LOW_INTERRUPT_VECTOR_ADDRESS _endasm
	}
	
	#pragma code
	
	//These are your actual interrupt handling routines.
	#pragma interrupt YourHighPriorityISRCode
	void YourHighPriorityISRCode()
	{
	    if (INTCON3bits.INT2IF) {
		    char temp=0;
	        DELAY_50mS();
	        if(!(SW_1)) {
	            DELAY_50mS();
	            if(!(SW_1)) {
	                DELAY_100mS();
	                        if(!(SW_1)) {
		                        reset_mechanism();
	                            INTCONbits.GIE = 0;
	                            ENB_2=1;
	                            // EJ_MOTOR=0;	
	                            ValveM1_R=0;
								ValveM2_R=0;
								ValveM1_F=0;
								ValveM2_F=0;
								
								if(testing){
									
									Reset();
								}
	                            DELAY_50mS();
	                            write_rom_rpi(0);
							    LCD_Begin(0b01001110);
							   
							    LCD_Cmd(LCD_CLEAR);
								LCD_Cmd(LCD_FIRST_ROW );
								LCD_Print("TURNING OFF");
								
	                            DELAY_250mS();
	                            RASP_IN_PIC_P=1;
	                            while(RASP_IN_PIC==0) {
	                                temp++;
	                                DELAY_1S();
	                                if(temp==40){
		                                
		                                break;
		                             } 
	                            }
	                            DELAY_1S();
	                            write_rom_rpi(0);
	                            INT_PIC_P=0;
	                            INT_PIC=0;
	                            SHD_PIC_P=1;
	                            temp=0;
	                            while (SHD_PIC) {
	                                DELAY_1S();
	                                temp++;
	                                INT_PIC=~INT_PIC;
	                                if(temp==100){
		                                
		                                KILL=0;
		                            }  
	                            }
	                            KILL=0;
	                }
	            }
	        }
	        INTCON3bits.INT2IF=0;
	    }
	    /*if(INTCONbits.TMR0IF){
			INTCONbits.TMR0IF=0;
			BUZZER=~BUZZER;
			if(STACK_SNS==1){
				T0CONbits.TMR0ON = 0;
				BUZZER=0;
			}
		}*/	
	}	//This return will be a "retfie fast", since this is in a #pragma interrupt section 
	#pragma interruptlow YourLowPriorityISRCode
	void YourLowPriorityISRCode()
	{
		//Check which interrupt flag caused the interrupt.
		//Service the interrupt
		//Clear the interrupt flag
		//Etc.
	
	}	//This return will be a "retfie", since this is in a #pragma interruptlow section 


/** DECLARATIONS ***************************************************/
#pragma code


#define STACK_END_SKIP 0
#define PLATE_STUCK_RETRY 5
#define ERROR_TTHRSLD1 4
#define ERROR_TTHRSLD2 9

const char* cont_err_string="CONT. ERROR";
const char* press_sm_string="PRESS MENU/START";

void cont_error_check(void){
/*	if(cont.v1_cw_error>ERROR_TTHRSLD1||
		cont.v1_acw_error>ERROR_TTHRSLD1||
		cont.v2_cw_error>ERROR_TTHRSLD1||
		cont.v2_acw_error>ERROR_TTHRSLD1||
		cont.v1ft_cw_error>ERROR_TTHRSLD1||
 		cont.v2ft_cw_error>ERROR_TTHRSLD1||
		cont.v1ft_acw_error>ERROR_TTHRSLD1||
		cont.v2ft_acw_error>ERROR_TTHRSLD1
		){
		testing=0;
		display(0,cont_err_string,0,1);
		POWER_INT_ENABLE;
		reset_mechanism();
		TOWER_ON;
		while (SW_3&&SW_2){
			BUZZER=~BUZZER;
			DELAY_500mS();
		}
		TOWER_OFF;
		BUZZER=0;	
		display(1,press_sm_string,"TO CHECK V.MOTOR",1);
		while (SW_3&&SW_2);
		post(160);
		Reset();
	}*/
	if(cont.qr_error>ERROR_TTHRSLD1){
		testing=0;
		display(0,cont_err_string,0,1);
		POWER_INT_ENABLE;
		reset_mechanism();
		TOWER_ON;
		while (SW_3&&SW_2){
			BUZZER=~BUZZER;
			DELAY_500mS();
		}
		TOWER_OFF;
		BUZZER=0;	
		Reset();
	}
	/*if(cont.leak1_error_RT>ERROR_TTHRSLD1||
		cont.leak1_error_LT>ERROR_TTHRSLD1||
		cont.leak1_error_LT1>ERROR_TTHRSLD1||
		cont.leak2_error_RT>ERROR_TTHRSLD1||
		cont.leak2_error_LT>ERROR_TTHRSLD1||
		cont.leak2_error_LT1>ERROR_TTHRSLD1||
		cont.clog_error_RT>ERROR_TTHRSLD1||
		cont.clog_error_LT>ERROR_TTHRSLD1||
		cont.clog_error_LT1>ERROR_TTHRSLD1||
		cont.leak3_error_RT>ERROR_TTHRSLD2||
		cont.leak3_error_LT>ERROR_TTHRSLD2||
		cont.leak3_error_LT1>ERROR_TTHRSLD2
		){	
		testing=0;
		display(0,cont_err_string,0,1);
		POWER_INT_ENABLE;
		reset_mechanism();
		TOWER_ON;
		while (SW_3&&SW_2){
			BUZZER=~BUZZER;
			DELAY_500mS();
		}
		TOWER_OFF;
		BUZZER=0;	
		display(1,press_sm_string,"TO CHECK VACUUM",1);
		while (SW_3&&SW_2);
		
		POWER_INT_DISABLE;
		vacuum_test();
		Reset();
	}*/
	
}




/******************************************************************************
 * Function:        void main(void)
 * PreCondition:    None
 * Side Effects:    None
 * Overview:        Main program entry point.
 * Note:            None
 *******************************************************************/
	char reject_flag=1;  //reject if cartridge is present at testing spot during startup
#if defined(__18CXX)
void main(void)
#else
int main(void)
#endif
{   


	KILL_P=0;
	KILL=1;
	P_ENB_2=0;
	ENB_2=1;
	#ifndef BOARD_VER2
		P_Valve_1_R=0;
		P_Valve_1_L=0;
		Valve_1_L=0;
		Valve_1_R=0;
	#endif

	port_init();
	I2C_Init1();
    
	ADC_Init();
    LCD_Begin(0b01001110);
	#ifdef BOARD_VER2
		display(1,"CARTRIDGE QR","SCANNER JIG v2.3",1);
	#else
		display(1,"CARTRIDGE QR","SCANNER JIG v1.3",1);
	#endif
	

	testing=0;
	  cont.leak3_error_RT=0;
	   cont.leak3_error_LT=0; 
	   cont.leak3_error_LT1=0; 
	 
	   cont.v1_cw_error=0;
	   cont.v1_acw_error=0;
	 
	   cont.v2_cw_error=0;
	   cont.v2_acw_error=0;
	 
	   cont.v1ft_cw_error=0;
	   cont.v1ft_acw_error=0;
	 
	   cont.v2ft_cw_error=0;
	   cont.v2ft_acw_error=0;
	 
	   cont.clog_error_RT=0;
	   cont.clog_error_LT=0;
	   cont.clog_error_LT1=0;
	 
	   cont.qr_error=0;
	 
	   cont.leak1_error_RT=0;
	   cont.leak1_error_LT=0;
	   cont.leak1_error_LT1=0;
	 
	   cont.leak2_error_RT=0;
	   cont.leak2_error_LT=0;
	   cont.leak2_error_LT1=0;
    
    TOWER_OFF;
	RtryValve_HF=read_eeprom(1);
	DELAY_250mS();
	sbc_disabled=read_eeprom(0);
	DELAY_250mS();
	qr_disabled=read_eeprom(2);

	Init_PowerInt();
	
	
	
	//board_test_protocol();
	SBC_UARTInit();
 // write_rom_rpi(0);
  INTCONbits.TMR0IE = 1; 
  INTCONbits.TMR0IF = 0; 
 /* T0CONbits.T08BIT = 0; 
  T0CONbits.T0CS = 0; 
  T0CONbits.PSA = 0; 
  T0CONbits.T0PS2 = 1; 
  T0CONbits.T0PS1 = 1;
  T0CONbits.T0PS0 = 1; 
  TMR0L = 0;
  TMR0H = 0;
	//1/(48000000/(4*256*((2^16)-1)))=1.39808 seconds
  T0CONbits.TMR0ON = 0; // stops Timer1*/



  if(RCONbits.RI){
 //	post(70);
  }
	if(sbc_disabled==1){
		sbc_ready=0;
	}
	else {
		wait_ready_rpi();
	}
	display(1,"PRESS START",0,0);
//	sbc_ready=1; 
	while(SW_3){
		if(!SW_2){
			service_menu();
			
		}
	}
	while(!SW_3);
	testing=1;	
	while(1){
		//LCD_Begin(0b01001110);
		check_stack();
		display_counts();
		
	
	
			//POWER_INT_DISABLE;
		ELECT_SOL=1; //solenoid stopper down
		catFB_forward();
		ELECT_SOL=0; //solenoid stopper up
		DELAY_500mS();
		if(reject_flag){
			reject_on();
		}	
		else {
			reject_off();
		}
		//mech_plate_down();
		DELAY_500mS();		
		//LCD_Cmd(LCD_CLEAR);
		//display_counts();
		flush_uart();
		if(cat_test()){			
			reject_flag=1;
		}
		else {
			reject_flag=0;
			reject_off();
			
		}
		if(sbc_ready==1){
			write_rom_rpi(0); //stop rec
			//DELAY_100mS();
			//write_rom_rpi(23);
			//write_ram_rpi(error_type+'0');			
		}	
		mechUp_catFB_Back();	
		//check_key_intrpt();	
	//	cont_error_check();	
	}
}

void mech_plate_down(void){
	unsigned int i=0;
	PLATE_UD=1;//plate down
	while(MECH_UP_SNS){
		i++;
		DELAY_1mS();
		if(i==6000){
			POWER_INT_ENABLE;
			display(1,0,"MCH PLT D STUCK",5);
			mech_error_loop();
		}
	}
}

void reject_on(void){
	unsigned int i=0;
	REJECT_SV=1; //plate down
	#ifdef BOARD_VER2
	while(RJT_SNS){
		i++;
		DELAY_1mS();
		if(i==6000){
			POWER_INT_ENABLE;
			display(1,0,"REJECT PLT STUCK",2);
			mech_error_loop();
		}
	}
	#endif
}

void reject_off(void){
	unsigned int i=0;
	REJECT_SV=0; 
	#ifdef BOARD_VER2
	while(!RJT_SNS){
		i++;
		DELAY_1mS();
		if(i==6000){
			POWER_INT_ENABLE;
			display(1,0,"PASS PLT STUCK",2);
			mech_error_loop();
		}
	}
	#endif
}



void catFB_forward(void){
	unsigned int i=0,plate_stuck_retry=PLATE_STUCK_RETRY;
	CAT_FB=1; //cartride forward
		while(!FW_SNS){
			i++;
			DELAY_1mS();
			if(i==5000){
				if(plate_stuck_retry--){
					CAT_FB=0;//Move cartridge plate backward
					i=0;
					while(!BW_SNS){
						i++;
						DELAY_1mS();
						if(i==6000){
							display(1,0,"CAT PLT BK STUCK",0);
							POWER_INT_ENABLE;
							ELECT_SOL=0; 
							mech_error_loop();
						
						}
					}
				
					
					i=0;
					ELECT_SOL=1; //solenoid stopper down
					CAT_FB=1; //cartride forward
					continue;
				}
				else {
					display(1,0,"CAT PLT FW STUCK",0);
					POWER_INT_ENABLE;
					ELECT_SOL=0; 
					reset_mechanism();
					mech_error_botton();
					DELAY_100mS();
					LCD_Begin(0b01001110);
					display_counts();
					
					i=0;
					plate_stuck_retry=PLATE_STUCK_RETRY;
					ELECT_SOL=1; //solenoid stopper down
					CAT_FB=1; //cartride forward
					continue;
				}
			}	
		}
}
void mechUp_catFB_Back(void){
	unsigned int i=0;
	PLATE_UD=0;//raise up the plate
		CAT_FB=0;//Move cartridge plate backward
		i=0;
		while(!BW_SNS){
			i++;
			DELAY_1mS();
			if(i==10000){
				
				POWER_INT_ENABLE;
				display(1,0,"CAT PLT BK STUCK",5);
				mech_error_loop();
				
			}
		}
		i=0;
		while(!MECH_UP_SNS){ //check mech plate is up
			i++;
			DELAY_1mS();
			if(i==6000){
				
				POWER_INT_ENABLE;
				display(1,0,"MCH PLT U STUCK",5);
				mech_error_loop();
				
			}
		}				
}

void check_stack(void){
	 static unsigned char stack_skip=STACK_END_SKIP;
	if(STACK_SNS==0){
			//if(!T0CONbits.TMR0ON)T0CONbits.TMR0ON = 1;
			if(!stack_skip){
				POWER_INT_ENABLE;
				reset_mechanism();
				
			//	T0CONbits.TMR0ON = 0;
				TOWER_ON;	
				DisplayStackEmpty();
				
				BUZZER=0;
				TOWER_OFF;
				while(!SW_3 );	
				stack_skip=STACK_END_SKIP;
				LCD_Begin(0b01001110);				
			}
			else {
				stack_skip--;
			}	
		}else {
			//T0CONbits.TMR0ON = 0;
			BUZZER=0;
			stack_skip=STACK_END_SKIP;
		}
}

void check_key_intrpt(void){
/*	unsigned int wait_time=400;
	if(INTCON3bits.INT2IF){
		display(1,"SHUTDOWN?","START->PAUSE",0);
		DELAY_500mS();
		POWER_INT_ENABLE;
		while(SW_3){
			wait_time--;
			DELAY_50mS();
			if(!wait_time){	
				POWER_INT_DISABLE;
				return;
			}
		}
	
		while(!SW_3);
		display(1,"SHUTDOWN?","START?",1);
		while(SW_3);
		while(!SW_3);
		POWER_INT_DISABLE;
	}*/
}

void reset_mechanism(void){
//	T0CONbits.TMR0ON = 0;
	//INTCONbits.TMR0IE = 0; 
	BUZZER=0;
	valve_right_idle();	
	PLATE_UD=0;//raise up the plate
	CAT_FB=0;//Move cartridge plate backward
	REJECT_SV=0;//Move reject plate forward
	ELECT_SOL=0;//stoper up	
	TOWER_OFF;
}

const char* PASSs="PASS";
const char* FAILs="FAIL";
char cat_test(void){
	char qr_result=0, retry=3;
	//	if(!CAT_SNS){
	//		DELAY_250mS();
	//		if(!CAT_SNS){
		
				count++;
				while(retry--){	
				if(sbc_ready==1){
					if(!qr_disabled){
						if(retry)
							write_rom_rpi(20);
						else 
							write_rom_rpi(19);
						if(wait_busy_rpi()){
							if(retry)
								write_rom_rpi(20);
							else 
								write_rom_rpi(19);
								if(wait_busy_rpi()){
									if(retry)
										write_rom_rpi(20);
									else 
										write_rom_rpi(19);
										if(wait_busy_rpi()){
											display(0,0,"SBC Er-2",0);
											mech_error_loop();
										}
								}
						}
						//DELAY_100mS();
						flush_uart();
						qr_result=wait_for_qr();
						if(qr_result==0){
							display(1,0,PASSs,0);
				
							pass_count++;
							display_counts();
							return 0; 	
						}
						else if(qr_result==1){
							return 1;
						}
						else if(qr_result==2){
							return reject_flag;
						}
						else if(qr_result==3){
							//return 1;
							display(0,"RETRYING",0,0);
							DELAY_500mS();
						}	
						
						else {
							return 1;
						}
						
						
						
					}	
				//	DELAY_500mS();
				//	write_rom_rpi(21);
					
					

					}	
				}
				
			
							
						display(1,"QR NOT READABLE ",press_sm_string,1);
								
								while (SW_3&&SW_2){
									BUZZER=~BUZZER;
									DELAY_500mS();
								}
							
								BUZZER=0;
					
				return 1;
				
	//		}
	//	}
		/*	POWER_INT_ENABLE;
			reset_mechanism();
			DisplayCatNotDet();
			while(!SW_3);
			LCD_Begin(0b01001110);	
			//POWER_INT_DISABLE;
			return 3; */
}

char ValveTest(void)
{
  
}


void vacuum_leak_error(char errortype){
	
}

char VacuumTest(void)
{

}


void port_init(void){

	BUZZER_P=0;
	BUZZER=0;
	#ifdef BOARD_VER2
		RJT_SNS_P=1;
		VAC_VLV_P=0;
		VAC_VLV=0;
	#else
		P_Valve_1_R=0;
		P_Valve_1_L=0;
		Valve_1_L=0;
		Valve_1_R=1;
	#endif

	P_ValveM1_R=0;
	P_ValveM1_F=0;
	ValveM1_R=0;
	ValveM1_F=0;
	P_ValveM2_R=0;
	P_ValveM2_F=0;
	ValveM2_R=0;
	ValveM2_F=0;
	PORTEbits.RDPU=0;
	//LATE=0x06;
	P_ENB_2=0;
	P_CLK_2=0;

	TRISAbits.TRISA0=1;
	TRISAbits.TRISA1=1;
	TRISAbits.TRISA2=1;	
	TRISAbits.TRISA3=1;
	SW_1_P=1;
	SW_2_P=1;
	SW_3_P=1;
	
	LM_SW_DET_PORT=1;
	INT_PIC_P=0;
	RASP_IN_PIC_P=1;
	SHD_PIC_P=1;
	INT_PIC=0;
	
	CAT_FB_P=0;
	PLATE_UD_P=0;
	REJECT_SV_P=0;
	ELECT_SOL_P =0;
	
	CAT_FB=0;
	PLATE_UD=0;
	REJECT_SV=0;
	ELECT_SOL =0;
	
	BW_SNS_P=1;
	FW_SNS_P=1;
	MECH_UP_SNS_P=1;

	
	UCONbits.USBEN = 0; //disable usb module and transceiver to use RC4 and RC5
	UCFGbits.UTRDIS = 1; 

}




/******************************************************/





