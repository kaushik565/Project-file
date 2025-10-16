#include <p18cxxx.h>
#include "uart.h"

// 48MHz Fosc -> 12 MIPS. For BRGH=1, SPBRG = (Fosc/(16*baud))-1
// 48e6/(16*115200) - 1 ≈ 25

void uart_init_115200(void) {
    // Configure pins
    TRISCbits.TRISC6 = 0; // TX as output
    TRISCbits.TRISC7 = 1; // RX as input

    // Reset serial
    TXSTA = 0x00;  // async, BRGH set later
    RCSTA = 0x00;
    BAUDCON = 0x00; // default

    SPBRG = 25;     // 115200 @ 48MHz with BRGH=1
    SPBRGH = 0;

    TXSTAbits.BRGH = 1; // high speed
    RCSTAbits.SPEN = 1;  // enable serial port
    TXSTAbits.TXEN = 1;  // enable transmitter
    RCSTAbits.CREN = 1;  // enable continuous receive
}

unsigned char uart_read_byte_nonblock(unsigned char* out) {
    if (!PIR1bits.RCIF) return 0; // no data
    if (RCSTAbits.OERR) {         // overrun error, reset
        RCSTAbits.CREN = 0;
        RCSTAbits.CREN = 1;
    }
    *out = RCREG;
    return 1;
}

void uart_write_byte(unsigned char b) {
    while (!TXSTAbits.TRMT) {
        ;
    }
    TXREG = b;
}
