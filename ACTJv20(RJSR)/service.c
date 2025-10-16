#include "service.h"

static unsigned int current_adc_offset=0;
rom char string[17]="OK      >      <";
typedef void (*item_callback_type)(void);
extern unsigned int TM;
extern unsigned int BaseValue,C_BaseValue;



#define Product_Pasword 4751
#define Pasword_Pos 5
void DelayCal(unsigned int k)
{
    unsigned int i,j;
    for(j=0; j<k; j++)
        for (i = 0; i < 8812; i++);
}


void Password_set(void)
{
    unsigned char  Initialization_Flag,digit_position;
    unsigned int paswrd_digit_1,paswrd_digit_2,paswrd_digit_3,paswrd_digit_4;
    unsigned char paswrd_string[5];
    unsigned int paswrd_Code;
    char digit_value;
    unsigned char St_Table;

	digit_value=paswrd_digit_1=paswrd_digit_2=paswrd_digit_3=paswrd_digit_4=0;
    paswrd_Code=0;
    LL:digit_position=1;
	paswrd_string[0]=paswrd_digit_1+'0';
    paswrd_string[1]=paswrd_digit_2+'0';
	paswrd_string[2]=paswrd_digit_3+'0';
	paswrd_string[3]=paswrd_digit_4+'0';
	paswrd_string[4]=0;
    Initialization_Flag=0;
	LCD_Cmd(LCD_CLEAR);
	LCD_Goto(6,1);
	LCD_Print("PIN?");
	LCD_Goto(Pasword_Pos+1,2);
    LCD_Print_rammem(paswrd_string);

    /*XLCDInit();
    XLCDCommand(CursorOff);
    XLCDL1home();
    XLCDPutRomString("   ENTER PIN:   ");
    XLCDL2home();

    XLCD2CursorPoint(Pasword_Pos+1);
    XLCDPutRamString(paswrd_string);*/
	
	LCD_Goto(Pasword_Pos+digit_position,2);
	LCD_Cmd(LCD_BLINK_CURSOR_ON);

    //XLCD2CursorPoint(Pasword_Pos+digit_position);
    //XLCDCommand(CursorOn);
    do 	{
        St_Table	=	(PORTB & 0x1C);
		DELAY_100mS();
        if(St_Table == 0b00011000)
        {
            digit_position++;
            //XLCD2CursorPoint(Pasword_Pos+digit_position);
			LCD_Goto(Pasword_Pos+digit_position,2);
			LCD_Cmd(LCD_BLINK_CURSOR_ON);

            do {
                St_Table	=	(PORTB & 0x1C);
            }
            while(St_Table == 0b00011000);

            if(digit_position>4)
            {
                //XLCDCommand(CursorOff);
				LCD_Cmd(LCD_CURSOR_OFF);
                paswrd_Code=paswrd_digit_1*1000+paswrd_digit_2*100+paswrd_digit_3*10+paswrd_digit_4;
                digit_position=1;
                if(paswrd_Code==Product_Pasword)
                {
                    Initialization_Flag=1;
                }
                else
                {
                    //XLCDL2home();
                    ///XLCDPutRomString("INCORRECT PIN ! ");
					LCD_Cmd(LCD_CLEAR);
					LCD_Cmd(LCD_FIRST_ROW);
					LCD_Print_space("FAIL");
                    DELAY_1S();
                    DELAY_1S();

                   // paswrd_string[0]=paswrd_string[1]=paswrd_string[2]=paswrd_string[3] =0x30;
                   // paswrd_string[4] = '\0';
//                    XLCDL2home();
//                    XLCDL2home();
//                    XLCDPutRomString("                ");
//                    //	XLCDPutRomString(password);
//                    XLCD2CursorPoint(Pasword_Pos+1);
//                    XLCDPutRamString(paswrd_string);
//
//                    XLCD2CursorPoint(Pasword_Pos+digit_position);
//                    XLCDCommand(CursorOn);
					/*	LCD_Cmd(LCD_CLEAR);
						LCD_Print_rammem(paswrd_string);
						LCD_Goto(Pasword_Pos+digit_position,2);
						LCD_Cmd(LCD_BLINK_CURSOR_ON);*/\
						goto LL;

                }
            }
            digit_value=0;
            DelayCal(1);
        }
        else if(St_Table == 0b00001100)
        {
            digit_value++;
            if(digit_value>9)digit_value=0;
            do {
                St_Table	=	(PORTB & 0x1C);
            }
            while(St_Table == 0b00001100);

            switch(digit_position)
            {
            case 1:
                paswrd_digit_1 = digit_value;
                paswrd_string[0] = digit_value+0x30;
                break;
            case 2:
                paswrd_digit_2 = digit_value;
                paswrd_string[1] = digit_value+0x30;
                break;
            case 3:
                paswrd_digit_3 = digit_value;
                paswrd_string[2] = digit_value+0x30;
                break;
            case 4:
                paswrd_digit_4 = digit_value;
                paswrd_string[3] = digit_value+0x30;
                break;
            default:
                digit_position=1;
                

                paswrd_string[4] = '\0';
				break;
            }
//            XLCDCommand(CursorOff);
//            XLCDL2home();
//            XLCD2CursorPoint(Pasword_Pos+1);
//            XLCDPutRamString(paswrd_string);
//            XLCD2CursorPoint(Pasword_Pos+digit_position);
//            XLCDCommand(CursorOn);

				LCD_Cmd(LCD_CURSOR_OFF);
				LCD_Cmd(LCD_SECOND_ROW);
				LCD_Goto(Pasword_Pos+1,2);
		    	LCD_Print_rammem(paswrd_string);
				//LCD_Cmd(LCD_CLEAR);
				LCD_Goto(Pasword_Pos+digit_position,2);
				LCD_Cmd(LCD_BLINK_CURSOR_ON);

			

            DelayCal(1);;
        }

        else if(St_Table == 0b00010100)
        {
            digit_value--;
            if(digit_value<0)digit_value=9;
            do {
                St_Table	=(PORTB & 0x1C);
            }
            while(St_Table == 0b00010100);

            switch(digit_position)
            {
            case 1:
                paswrd_digit_1 = digit_value;
                paswrd_string[0] = digit_value+0x30;
                break;
            case 2:
                paswrd_digit_2 = digit_value;
                paswrd_string[1] = digit_value+0x30;
                break;
            case 3:
                paswrd_digit_3 = digit_value;
                paswrd_string[2] = digit_value+0x30;
                break;
            case 4:
                paswrd_digit_4 = digit_value;
                paswrd_string[3] = digit_value+0x30;
                break;
            default:
                digit_position=1;
                break;

                paswrd_string[4] = '\0';
            }
//            XLCDCommand(CursorOff);
//            XLCDL2home();
//            XLCD2CursorPoint(Pasword_Pos+1);
//            XLCDPutRamString(paswrd_string);
//            XLCD2CursorPoint(Pasword_Pos+digit_position);
//            XLCDCommand(CursorOn);

				LCD_Cmd(LCD_CURSOR_OFF);
				LCD_Cmd(LCD_SECOND_ROW);
				LCD_Goto(Pasword_Pos+1,2);
		    	LCD_Print_rammem(paswrd_string);
				//LCD_Cmd(LCD_CLEAR);
				LCD_Goto(Pasword_Pos+digit_position,2);
				LCD_Cmd(LCD_BLINK_CURSOR_ON);


			
            DelayCal(1);;
        }
        else if(St_Table == 0b00000100)
        {
            digit_position++;
			LCD_Goto(Pasword_Pos+digit_position,2);
			LCD_Cmd(LCD_BLINK_CURSOR_ON);
            //XLCD2CursorPoint(Pasword_Pos+digit_position);

            do {
                St_Table	=	(PORTB & 0x1C);
            }
            while(St_Table == 0x18);

            Reset();
        }

    } while(Initialization_Flag==0);
    return;
}


void menu(unsigned char items, char** menu_string, item_callback_type* function) {
    unsigned char item=0;
    display(1,menu_string[item],string,0);
    while(!SW_1);
    while(1) {
        if(!SW_3) {
            item++;
            if(item==items) item=0;   
            display(1,menu_string[item],string,0);
            while(!SW_3);
        }
        else if(!SW_2) {
            if(item) item--;
            else item=items-1;
            display(1,menu_string[item],string,0);
            while(!SW_2);
        }
        else if(!SW_1) {
            while(!SW_1);
            if(item==(items-1))return;
            else function[item]();
            display(1,menu_string[item],string,0);
            while(!SW_1);
        }
        DELAY_100mS();
    }
}


/*
void read_current(unsigned char adc) {
    char c;
    unsigned char first_digit,second_digit, third_digit, fourth_digit;
    unsigned int current_adc=0,current_adc_avg=0,current_v=0, current_c=0,current_adc_min=1023 ,current_adc_max=0;
    char string[17];
    
    while(SW_1) {
        current_adc_avg=0;
        for(c=0; c<10; c++) {
            current_adc=ADC_Read(adc);
            current_adc_avg+=current_adc;

            
        }
        current_adc_avg=current_adc_avg/10;
        if(current_adc_avg>current_adc_max) {
               current_adc_max=current_adc_avg;
         }

         if(current_adc_avg<current_adc_min) {
               current_adc_min=current_adc_avg;
         }
        if(current_adc_offset>current_adc_avg) {
            current_c = (((unsigned long int)current_adc_offset) - current_adc_avg);

            current_c =((unsigned long int)current_c*((unsigned long int)1000))/((unsigned long int)1023);

            string[0] =' ';
            string[1] = ((int) current_c / 100) + '0';
            string[2] = (((current_c) % 100) / 10) + '0';
            string[3] = ((current_c) % 10) + '0';
            string[4] = ' ';
            string[5] = '|';
            string[6] = ' ';

            current_c = (int)( current_adc_offset-current_adc_max);
            current_c =((unsigned long int)current_c*((unsigned long int)1000))/((unsigned long int)1023);
            
            string[7] = ((int) current_c / 100) + '0';
            string[8] = (((current_c) % 100) / 10) + '0';
            string[9] = ((current_c) % 10) + '0';
            string[10] = ' ';
			string[11] = '~';
            current_c = (int)(current_adc_offset-current_adc_min);
            current_c =((unsigned long int)current_c*((unsigned long int)1000))/((unsigned long int)1023);
            string[12] =' ';
            string[13] = ((int) current_c / 100) + '0';
            string[14] = (((current_c) % 100) / 10) + '0';
            string[15] = ((current_c) % 10) + '0';
            string[16] = 0;

            LCD_Cmd(LCD_SECOND_ROW);
           LCD_Print_rammem(string);
        }
        else if(current_adc_avg>current_adc_offset) {
            current_c = (((unsigned long int)current_adc_avg) - current_adc_offset);
            //	current_c = (current_c * 65.178*CURRENT_CALIB_VALUE) / 100;

            current_c =((unsigned long int)current_c*((unsigned long int)1000))/((unsigned long int)1023);

            string[0] =' ';
            string[1] = ((int) current_c / 100) + '0';
            string[2] = (((current_c) % 100) / 10) + '0';
            string[3] = ((current_c) % 10) + '0';
            string[4] = ' ';
            string[5] = '|';
            string[6] = ' ';

			current_c = (int)(((long int)current_adc_min) - current_adc_offset);
            current_c =((unsigned long int)current_c*((unsigned long int)1000))/((unsigned long int)1023);
            string[7] = ((int) current_c / 100) + '0';
            string[8] = (((current_c) % 100) / 10) + '0';
            string[9] = ((current_c) % 10) + '0';
            string[10] = ' ';
			string[11] ='~';
            current_c = (int)(((long int)current_adc_max) - current_adc_offset);
            current_c =((unsigned long int)current_c*((unsigned long int)1000))/((unsigned long int)1023);
            string[12] =' ';
            string[13] = ((int) current_c / 100) + '0';
            string[14] = (((current_c) % 100) / 10) + '0';
            string[15] = ((current_c) % 10) + '0';
            string[16] = 0;
            
            LCD_Cmd(LCD_SECOND_ROW);
           LCD_Print_rammem(string);

        }
        else {

            current_c = 0;
            string[0] =  '0';
            string[1] = '0';
            string[2] = '0';
            string[3] = 'm';
            string[4] = 'A';
            string[5] = 0;
            LCD_Cmd(LCD_SECOND_ROW);
           LCD_Print_rammem(string);
        }
       
    }
    while(!SW_1);
}*/

#define MAX_CURRENT 50
#define MIN_CURRENT 10
char read_current(unsigned char adc,char auto_flag,unsigned char time) {
    char c;
    unsigned char first_digit,second_digit, third_digit, fourth_digit;
    unsigned int current_adc=0,current_adc_avg=0,current_v=0, current_c=0,current_adc_min=1023 ,current_adc_max=0;
    char string[17];
 
    while(SW_1) {
        current_adc_avg=0;
        for(c=0; c<10; c++) {
            current_adc=ADC_Read(adc);
            current_adc_avg+=current_adc;    
        }
        current_adc_avg=current_adc_avg/10;
        if(current_adc_avg>current_adc_max) {
               current_adc_max=current_adc_avg;
         }

         if(current_adc_avg<current_adc_min) {
               current_adc_min=current_adc_avg;
         }
        if(current_adc_offset>current_adc_avg) {
            current_c = (((unsigned long int)current_adc_offset) - current_adc_avg);

            current_c =((unsigned long int)current_c*((unsigned long int)1000))/((unsigned long int)1023);

            string[0] =' ';
            string[1] = ((int) current_c / 100) + '0';
            string[2] = (((current_c) % 100) / 10) + '0';
            string[3] = ((current_c) % 10) + '0';
            string[4] = ' ';
            string[5] = '|';
            string[6] = ' ';

            current_c = (int)( current_adc_offset-current_adc_max);
            current_c =((unsigned long int)current_c*((unsigned long int)1000))/((unsigned long int)1023);
            
            string[7] = ((int) current_c / 100) + '0';
            string[8] = (((current_c) % 100) / 10) + '0';
            string[9] = ((current_c) % 10) + '0';
            string[10] = ' ';
			string[11] = '~';
            current_c = (int)(current_adc_offset-current_adc_min);
            current_c =((unsigned long int)current_c*((unsigned long int)1000))/((unsigned long int)1023);
            string[12] =' ';
            string[13] = ((int) current_c / 100) + '0';
            string[14] = (((current_c) % 100) / 10) + '0';
            string[15] = ((current_c) % 10) + '0';
            string[16] = 0;

            LCD_Cmd(LCD_SECOND_ROW);
           LCD_Print_rammem(string);
        }
        else if(current_adc_avg>current_adc_offset) {
            current_c = (((unsigned long int)current_adc_avg) - current_adc_offset);
            //current_c = (current_c * 65.178*CURRENT_CALIB_VALUE) / 100;

            current_c =((unsigned long int)current_c*((unsigned long int)1000))/((unsigned long int)1023);

            string[0] =' ';
            string[1] = ((int) current_c / 100) + '0';
            string[2] = (((current_c) % 100) / 10) + '0';
            string[3] = ((current_c) % 10) + '0';
            string[4] = ' ';
            string[5] = '|';
            string[6] = ' ';

			current_c = (int)(((long int)current_adc_min) - current_adc_offset);
            current_c =((unsigned long int)current_c*((unsigned long int)1000))/((unsigned long int)1023);
            string[7] = ((int) current_c / 100) + '0';
            string[8] = (((current_c) % 100) / 10) + '0';
            string[9] = ((current_c) % 10) + '0';
            string[10] = ' ';
			string[11] ='~';
            current_c = (int)(((long int)current_adc_max) - current_adc_offset);
            current_c =((unsigned long int)current_c*((unsigned long int)1000))/((unsigned long int)1023);
            string[12] =' ';
            string[13] = ((int) current_c / 100) + '0';
            string[14] = (((current_c) % 100) / 10) + '0';
            string[15] = ((current_c) % 10) + '0';
            string[16] = 0;
            
            LCD_Cmd(LCD_SECOND_ROW);
           LCD_Print_rammem(string);

        }
        else {

            current_c = 0;
            string[0] =  '0';
            string[1] = '0';
            string[2] = '0';
            string[3] = 'm';
            string[4] = 'A';
            string[5] = 0;
            LCD_Cmd(LCD_SECOND_ROW);
           LCD_Print_rammem(string);
        }
        if(auto_flag){
	        if(current_c>MAX_CURRENT||current_c<MIN_CURRENT){
		        ValveM1_R=0;
	        	ValveM1_F=0;
		        ValveM2_R=0;
	        	ValveM2_F=0;
	        	return 1;
	        }
	        if(time) time--;
	        else return 0;
        }
       
    }
    while(!SW_1);
    return 0;
}

void mech_error_botton(void){
	while (SW_3&&SW_2){
		TOWER_OFF;
		BUZZER=1;
		DELAY_500mS();
		TOWER_ON;
		BUZZER=0;
		DELAY_500mS();
	}
	TOWER_OFF;
}


void mech_error_loop(void){
	reset_mechanism();
	while(1){
				TOWER_OFF;
				BUZZER=1;
				DELAY_500mS();
				TOWER_ON;
				BUZZER=0;
				DELAY_500mS();
	}
}


rom char clogerror[11]="CLOG ERROR";
void post(unsigned char time){
	unsigned int pressureRT,pressureLT;
	if(MECH_UP_SNS){
		pressureRT=ADC_Read(2);
		valve_left();
		DELAY_500mS();
		pressureLT=ADC_Read(2);
		valve_right_idle();
		if(pressureRT<921||pressureLT<921)
		{
			display(1,"POST FAILED",clogerror,0);
			reset_mechanism();
			mech_error_botton();
			service_menu();
			Reset();	
		}
		if(rtry_vlv_test(1,time)){
		 		LCD_Goto(10,0);
		 		LCD_Print("P.ERROR");
		 		reset_mechanism();
				mech_error_botton();	
				service_menu();
				Reset();
		 		
		}
	}
}

char rtry_vlv_test(char auto_test,unsigned char time){
		char string[16]="S.VM ACW POST", fail=0;
		if(!auto_test) string[8]=0;
        display_ram(1,string,0,0);

        P_ValveM1_R=0;
        P_ValveM1_F=0;

        ValveM1_R=0;
        ValveM1_F=0;

        DELAY_1S();

        current_adc_offset=ADC_Read(0);

        ValveM1_R=1;
        ValveM1_F=0;
        DELAY_1S();
  
        if(read_current(0,auto_test,time)){
        	return 1;
        }

        ValveM1_R=0;
        ValveM1_F=0;

        DELAY_1S();
        
        string[5]=' ';
        display_ram(1,string,0,0);

        current_adc_offset=ADC_Read(0);

        ValveM1_R=0;
        ValveM1_F=1;
        DELAY_1S();
       

        if(read_current(0,auto_test,time)){
        	return 1;
        }

        ValveM1_R=0;
        ValveM1_F=0;
        DELAY_1S();

        current_adc_offset=ADC_Read(1);

        P_ValveM2_R=0;
        P_ValveM2_F=0;

        ValveM2_R=1;
        ValveM2_F=0;
        
        string[0]='E';
        string[5]='A';
        display_ram(1,string,0,0);

        //display(1,"VM2 ACW",0,0);
        DELAY_1S();
      

        if(read_current(1,auto_test,time)){
        	return 1;
        }

        ValveM2_R=0;
        ValveM2_F=0;
        DELAY_1S();

        current_adc_offset=ADC_Read(1);
        
		string[5]=' ';
        display_ram(1,string,0,0);
        //display(1,"VM2 CW",0,0);

        ValveM2_R=0;
        ValveM2_F=1;
        DELAY_1S();
  
        if(read_current(1,auto_test,time)){
        	return 1;
        }
        ValveM2_R=0;
        ValveM2_F=0 ;     
        return 0;
}

void mechanism_test(void)
{
    while(1) {
	    display(1,"CAT.SNS CHK",0,0);
        if(!CAT_SNS) {
            display(0,0,"SNS ERR",0);
            while(!CAT_SNS);
        }
        while(CAT_SNS);
        DELAY_250mS();
        display(0,0,"SNS PRSD",0);
        while(!CAT_SNS);
        display(0,0,"SNS RLSD",0);
        DELAY_1S();DELAY_1S();
        while(SW_1);
        while(!SW_1);

        rtry_vlv_test(0,0);

        return;
    }
}


void bluetooth(void) {
    char in=0;
    write_rom_rpi(0);
    wait_ready_rpi();
    if(sbc_ready)
    {
        display(1,"PAIR",0,0);
        write_rom_rpi(24);

        while(SW_3 || SW_2) {
            if (PIR1bits.RCIF == 1) {
                PIR1bits.RCIF = 0;
                in = RCREG;
                if(in=='R'){
	                display(1,"OK",0,2);
	                break;
	             }
	             if(in=='T'){
	                display(1,"T-OUT",0,2);
	                break;
	             }
            }
        }
        
    }
    else {
        display(1,"ER",0,0);
    }

    DELAY_1S();
}

rom char RtNzlFail[12]="S.Nzl Fail";
rom char LtNzlFail[12]="E.Nzl Fail";
void vacuum_test(void) {
	unsigned int i=0, BaseVacuum=0;
	valve_right_idle();
	display(1,"Cls S.Nzl",0,0);
	TM=25;
    ENB_2=0;
	for(i=0; i<25; i++)	//180
    {
        Step_1Sec_Clk2();
        TM--;
        DisplayPressure(ADC_Read(2));
		if(C_BaseValue<=716)
		break;
	}
    ENB_2=1;
	if(i==25)
	{
		display(1,RtNzlFail,0,0);
		while(SW_1)DisplayPressure(ADC_Read(2));			
	}
	else
	{	
		
		DELAY_1S();
		BaseVacuum=ADC_Read(2);
		BaseVacuum=ADC_Read(2);
		if(BaseVacuum>767)
		{
			display(1,RtNzlFail,0,0);
			while(SW_1) DisplayPressure(ADC_Read(2));	
		}
		else
		{
			TM=5;
			for (i = 0; i < 5; i++)
			{
				
				DELAY_1S();	
		        DisplayPressure(ADC_Read(2));
				TM--;
			}
			C_BaseValue=ADC_Read(2);
			C_BaseValue=ADC_Read(2);
			if(C_BaseValue>(BaseVacuum+3))
			{
			display(1,RtNzlFail,0,0);
				while(SW_1)	DisplayPressure(ADC_Read(2));	
			}
			else
			{
				display(1,"S.Nzl Pass",0,0);
				while(SW_1)	DisplayPressure(ADC_Read(2));
			}
	
		}
		
	}
	C_BaseValue=ADC_Read(2);
	if(C_BaseValue<921)
	{	
		BUZZER=1;
		display(1,RtNzlFail,clogerror,2);
		BUZZER=0;	
		while(SW_1);	
	}
	display(1,"Cls E.Nzl",0,0);
	TM=25;
    valve_left();
    ENB_2=0;
	for(i=0; i<25; i++)	//180
    {
        Step_1Sec_Clk2();
        TM--;
        DisplayPressure(ADC_Read(2));
		if(C_BaseValue<=716)
		break;
	}
    ENB_2=1;
	if(i==25)
	{
		display(1,LtNzlFail,0,0);
		while(SW_1)DisplayPressure(ADC_Read(2));			
	}
	else
	{	
		
		DELAY_1S();
		BaseVacuum=ADC_Read(2);
		BaseVacuum=ADC_Read(2);
		if(BaseVacuum>767)
		{
			display(1,LtNzlFail,0,0);
			while(SW_1) DisplayPressure(ADC_Read(2));	
		}
		else
		{
			TM=5;
			for (i = 0; i < 5; i++)
			{
				
				DELAY_1S();	
		        DisplayPressure(ADC_Read(2));
				TM--;
			}
			C_BaseValue=ADC_Read(2);
			C_BaseValue=ADC_Read(2);
			if(C_BaseValue>(BaseVacuum+3))
			{
				display(1,LtNzlFail,0,0);
				while(SW_1)	DisplayPressure(ADC_Read(2));	
			}
			else
			{
				 display(1,"E.Nzl Pass",0,0);
				while(SW_1)	DisplayPressure(ADC_Read(2));
			}
	
		}
		
	}
    ENB_2=1;
    C_BaseValue=ADC_Read(2);
	if(C_BaseValue<921)
	{	
		BUZZER=1;
		display(1,LtNzlFail,clogerror,2);
		BUZZER=0;	
		while(SW_1);	
	}
    valve_right_idle();
	//if(i==20)
}

void data_menu(void) {
	Password_set();
	if(sbc_disabled==1) {
		
		enable_sbc();
	}else {
		
		disable_sbc();
	}
}


void qr_menu(void) {
	Password_set();
	if(qr_disabled==1) {
	
		enable_qr();
	}else {
		
		disable_qr();
	}
}

void set_valve_half_value(void){
	unsigned char RtryValve_HF_temp;
	char string1[16]="VALUE=    ";
	display(1,"SET VLV HF VAL ",0,0);
	RtryValve_HF=read_eeprom(1);
	RtryValve_HF_temp=RtryValve_HF;
	string1[7] =RtryValve_HF_temp/10+0x30;
   	string1[8] =RtryValve_HF_temp%10+0x30;
    display_ram(0,0,string1,0);
	while(!SW_1);
    DELAY_500mS();
    do
    {
        while(!SW_3)
        {
            if(RtryValve_HF_temp>0)
                RtryValve_HF_temp-=1;
            string1[7] =RtryValve_HF_temp/10+0x30;
            string1[8] =RtryValve_HF_temp%10+0x30;
            display_ram(0,0,string1,0);
            DELAY_100mS();
            DELAY_250mS();
        }
        while(!SW_2)
        {
            if(RtryValve_HF_temp<40)
                RtryValve_HF_temp+=1;
            string1[7] =RtryValve_HF_temp/10+0x30;
            string1[8] =RtryValve_HF_temp%10+0x30;
            display_ram(0,0,string1,0);
            DELAY_100mS();
            DELAY_250mS();
        }
    } while(SW_1);
    display(0,"SAVE?",0,0);
    while(!SW_1);
    DELAY_500mS(); 
    do
    {
        if(!SW_3 && !SW_2)
        {
            display(1,"OK",0,0);
            write_eeprom(RtryValve_HF_temp, 1);
            RtryValve_HF=RtryValve_HF_temp;
            DELAY_1S();
            break;

        }
    } while(SW_1);


}

void service_menu(void) {
    char main_menu_items=7;
    char* main_menu_string[7]= {"VAC TST","MECH TST","RTRY VLV HALF", "QR", "DATA","BT PAIR","EXIT"};
    item_callback_type item_callback[6]= {vacuum_test, mechanism_test, set_valve_half_value, qr_menu, data_menu, bluetooth};
    
    POWER_INT_DISABLE;
	
    display(1,"MENU",0,0);
    DELAY_1S();
   	while(!SW_2);

    menu(main_menu_items,main_menu_string,item_callback);
    Reset();
    
}