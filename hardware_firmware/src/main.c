// C18 baseline, PIC18F4550
#include <p18cxxx.h>
#include <p18f4550.h>
#include <stdint.h>
#include <stdbool.h>
#include "config_bits.h"
#include "protocol.h"
#include "pins.h"
#include "uart.h"
#include "delay.h"
#include "lcd_i2c.h"

typedef enum {
    PLC_STATE_SETUP = 0,
    PLC_STATE_SCANNING = 1
} PLC_STATE;

static PLC_STATE plc_state = PLC_STATE_SETUP;
static unsigned long count = 0;
static unsigned long pass_count = 0;

// Additional pin definitions matching old firmware
#define SW_2_P TRISBbits.TRISB3
#define SW_3_P TRISBbits.TRISB4
#define SW_2 PORTBbits.RB3
#define SW_3 PORTBbits.RB4

#define BW_SNS_P TRISCbits.TRISC0
#define BW_SNS PORTCbits.RC0
#define FW_SNS_P TRISCbits.TRISC1
#define FW_SNS PORTCbits.RC1
#define MECH_UP_SNS_P TRISCbits.TRISC2
#define MECH_UP_SNS PORTCbits.RC2

#define ELECT_SOL_P TRISAbits.TRISA3
#define ELECT_SOL LATAbits.LATA3

#define PLATE_UD_P TRISAbits.TRISA2
#define PLATE_UD LATAbits.LATA2

// Error handler: display error and wait for operator START
static void error_loop(const char* line1, const char* line2) {
    lcd_print_lines(line1, line2);
    while (1) {
        // Wait for operator to press START (SW_3)
        if (!SW_3) {
            while (!SW_3) { delay_ms(50); } // Wait for release
            break;
        }
        delay_ms(100);
    }
    lcd_clear();
}

static void init_hw(void) {
    // IO directions - matching old firmware port_init()
    RASP_IN_PIC_P = 1; // RB6 as input from Pi
    
    // Buttons (inputs)
    SW_2_P = 1;
    SW_3_P = 1;
    
    // Sensors (inputs)
    STACK_SNS_P = 1;
    CAT_SNS_P = 1;
    BW_SNS_P = 1;
    FW_SNS_P = 1;
    MECH_UP_SNS_P = 1;
    RJT_SNS_P = 1;  // Rejection plate sensor
    
    // Actuators (outputs)
    REJECT_SV_P = 0;
    CAT_FB_P = 0;
    PLATE_UD_P = 0;
    ELECT_SOL_P = 0;

    // Default states
    REJECT_SV = 0;  // Pass position (RJT_SNS should be 0)
    CAT_FB = 0;
    PLATE_UD = 0;
    ELECT_SOL = 0;

    // UART
    uart_init_115200();
}

int main(void) {
    init_hw();
    lcd_init();
    lcd_clear();
    lcd_print_lines("WELCOME", "");
    delay_ms(1200); // Show welcome for 1.2s

    // Enter batch setup state
    plc_state = PLC_STATE_SETUP;
    lcd_print_lines("Setup Batch", "");

    // Wait for Pi to send CMD_START_SCANNING when user clicks "Start Scanning" in UI
    unsigned char rx_cmd;
    while (plc_state == PLC_STATE_SETUP) {
        if (uart_read_byte_nonblock(&rx_cmd)) {
            if (rx_cmd == CMD_START_SCANNING) {
                plc_state = PLC_STATE_SCANNING;
                break;
            }
        }
        delay_ms(50);
    }

    // Enter scanning state
    lcd_print_lines("Press Start", "");

    // Main loop: require START only after stack empty/refill, otherwise auto-cycle
    for(;;) {
        if (plc_state != PLC_STATE_SCANNING) {
            continue;
        }

        // Wait for stack to be filled and START pressed (only after empty)
        if (STACK_SNS == 0) {
            lcd_print_lines("Stack Empty", "Fill Stack &");
            delay_ms(500);
            lcd_print_lines("Press Start", "");
            while (STACK_SNS == 0) {
                delay_ms(100);
            }
            // Wait for START button
            while (SW_3) { delay_ms(50); }
            while (!SW_3) { delay_ms(50); }
        }

        // Now, as long as stack is not empty, auto-cycle
        unsigned char prev_result = 0; // 0=pass, 1=reject
        unsigned char first_cycle = 1;
        while (STACK_SNS != 0) {

            // Before moving previous cartridge out, set diverter for previous result
            if (!first_cycle) {
                if (prev_result == 0) {
                    REJECT_SV = 0; // Pass
                    unsigned int tmo = 0;
                    while (RJT_SNS && tmo < 6000) { delay_ms(1); tmo++; }
                    if (tmo >= 6000) error_loop("PASS PLT STUCK", "Press START");
                } else {
                    REJECT_SV = 1; // Reject
                    unsigned int tmo = 0;
                    while (!RJT_SNS && tmo < 6000) { delay_ms(1); tmo++; }
                    if (tmo >= 6000) error_loop("REJECT PLT STUCK", "Press START");
                }
            }

            // Move previous cartridge out (if not first cycle)
            if (!first_cycle) {
                PLATE_UD = 0;
                CAT_FB = 0;
                unsigned int timeout = 0;
                while (!BW_SNS && timeout < 10000) { delay_ms(1); timeout++; }
                if (timeout >= 10000) error_loop("CAT PLT BK STUCK", "Press START");
                timeout = 0;
                while (!MECH_UP_SNS && timeout < 6000) { delay_ms(1); timeout++; }
                if (timeout >= 6000) error_loop("MCH PLT U STUCK", "Press START");
                REJECT_SV = 0;
                delay_ms(250);
                if (STACK_SNS == 0) break;
            }

            // STEP: Stopper down and cartridge forward (bring new cartridge to scan position)
            ELECT_SOL = 1;
            CAT_FB = 1;
            delay_ms(500);
            unsigned int timeout = 0;
            while (!FW_SNS && timeout < 5000) { delay_ms(1); timeout++; }
            if (timeout >= 5000) error_loop("CAT PLT FW STUCK", "Press START");
            ELECT_SOL = 0;
            delay_ms(500);

            // QR scan with retry logic (scan new cartridge)
            unsigned char retry = 3;
            unsigned char qr_result = 255;
            count++;
            while (retry > 0) {
                if (retry > 1) {
                    uart_write_byte(CMD_RETRY);
                } else {
                    uart_write_byte(CMD_FINAL);
                }
                lcd_print_lines("Reading QR", "Hold steady...");
                unsigned int waited = 0;
                unsigned char rx;
                unsigned char got = 0;
                delay_ms(T_BUSY_SETTLE_MS);
                while (waited < T_CMD_MAX_WAIT_MS) {
                    if (uart_read_byte_nonblock(&rx)) {
                        switch (rx) {
                            case RES_ACCEPT:
                                qr_result = 0;
                                got = 1;
                                break;
                            case RES_REJECT:
                            case RES_DUPL:
                                qr_result = 1;
                                got = 1;
                                break;
                            case RES_SKIP:
                                qr_result = 2;
                                got = 1;
                                break;
                        }
                        if (got) break;
                    }
                    delay_ms(T_CMD_PERIOD_MS);
                    waited += T_CMD_PERIOD_MS;
                }
                if (got && qr_result != 2) break;
                retry--;
                if (retry > 0) {
                    lcd_print_lines("Retrying", "");
                    delay_ms(500);
                }
            }
            if (retry == 0 && qr_result == 255) {
                error_loop("QR TIMEOUT", "Press START");
            }
            if (qr_result == 0) {
                lcd_print_lines("PASS", "");
                pass_count++;
                prev_result = 0;
            } else if (qr_result == 1) {
                lcd_print_lines("REJECT", "");
                prev_result = 1;
            } else {
                error_loop("QR ERROR", "Press START");
            }
            first_cycle = 0;
            delay_ms(500);
        }
    }
}
