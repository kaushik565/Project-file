#ifndef DELAY_H
#define DELAY_H

#include <p18cxxx.h>

// Assume 48MHz instruction clock (12 MIPS). Adjust macros as needed.
// C18 provides Delay1KTCYx and Delay10TCYx; wrap ms/us helpers.

static void delay_us(unsigned int us) {
    while (us--) {
        _delay(12); // approx 1us at 12 MIPS (C18 intrinsic)
    }
}

static void delay_ms(unsigned int ms) {
    while (ms--) {
        // 1 ms -> 12000 cycles at 12 MIPS
        Delay1KTCYx(12);
    }
}

#endif // DELAY_H