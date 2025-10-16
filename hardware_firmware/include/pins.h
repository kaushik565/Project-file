// Pin mapping compatible with legacy ACTJ controller (PIC18F4550 family)
// Mirrors names used in ACTJv20(RJSR)/Pin_Definitions.h for wiring continuity.

#ifndef PINS_H
#define PINS_H

#include <p18cxxx.h>

// UART lines to Raspberry Pi
#define RX_PIC_P        TRISCbits.TRISC7
#define TX_PIC_P        TRISCbits.TRISC6
#define RX_PIC          LATCbits.LATC7
#define TX_PIC          LATCbits.LATC6

// Handshake lines
// RASP_IN_PIC is the Pi->PIC BUSY/READY input observed by the PIC on RB6
// Convention: HIGH = ready/idle, LOW = busy/acknowledge
#define RASP_IN_PIC_P   TRISBbits.TRISB6
#define RASP_IN_PIC     PORTBbits.RB6

// Optional: Shutdown/interrupt lines (kept for completeness)
#define INT_PIC_P       TRISBbits.TRISB5
#define INT_PIC         LATBbits.LATB5
#define SHD_PIC_P       TRISBbits.TRISB7
#define SHD_PIC         PORTBbits.RB7

// Sensors (subset; extend as needed)
#define STACK_SNS_P     TRISCbits.TRISC4
#define STACK_SNS       PORTCbits.RC4
#define CAT_SNS_P       TRISCbits.TRISC5
#define CAT_SNS         PORTCbits.RC5
#define RJT_SNS_P       TRISEbits.TRISE2  // Rejection plate position sensor (legacy ACTJ)
#define RJT_SNS         PORTEbits.RE2

// Actuators (subset; extend as needed)
#define REJECT_SV_P     TRISAbits.TRISA4
#define REJECT_SV       LATAbits.LATA4
#define CAT_FB_P        TRISEbits.TRISE0
#define CAT_FB          LATEbits.LATE0

#endif // PINS_H
