#ifndef CONFIG_BITS_H
#define CONFIG_BITS_H

// Device: PIC18F4550 (adjust if different)
#include <p18f4550.h>

// Primary config (typical USB/HSPLL clock @48MHz). Adjust for your board.
#pragma config PLLDIV = 5       // 20MHz crystal -> /5 = 4MHz input to PLL
#pragma config CPUDIV = OSC1_PLL2
#pragma config USBDIV = 2
#pragma config FOSC = HSPLL_HS  // HS with PLL enabled
#pragma config FCMEN = OFF
#pragma config IESO = OFF

// Power/Reset
#pragma config PWRT = ON
#pragma config BOR = OFF
#pragma config VREGEN = ON
#pragma config WDT = OFF

// IO & Debug
#pragma config MCLRE = ON
#pragma config LPT1OSC = OFF
#pragma config PBADEN = OFF
#pragma config CCP2MX = ON
#pragma config STVREN = ON
#pragma config LVP = OFF
#pragma config ICPRT = OFF
#pragma config XINST = OFF
#pragma config DEBUG = OFF

// Code protection (all off)
#pragma config CP0 = OFF, CP1 = OFF, CP2 = OFF, CP3 = OFF
#pragma config CPB = OFF, CPD = OFF
#pragma config WRT0 = OFF, WRT1 = OFF, WRT2 = OFF, WRT3 = OFF
#pragma config WRTB = OFF, WRTC = OFF, WRTD = OFF
#pragma config EBTR0 = OFF, EBTR1 = OFF, EBTR2 = OFF, EBTR3 = OFF
#pragma config EBTRB = OFF

#endif // CONFIG_BITS_H