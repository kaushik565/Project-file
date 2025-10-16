#ifndef PROTOCOL_H
#define PROTOCOL_H

// UART protocol bytes from PIC -> Pi to request a scan
#define CMD_RETRY   0x14  // 20
#define CMD_FINAL   0x13  // 19

// Pi -> PIC ASCII result codes
#define RES_ACCEPT  'A'
#define RES_REJECT  'R'
#define RES_DUPL    'D'
#define RES_SKIP    'S'

// Pi -> PIC control commands
#define CMD_START_SCANNING  'B'  // Pi tells PIC: batch setup complete, enter scanning mode

// Timing (ms)
#define T_BUSY_SETTLE_MS     20
#define T_BEFORE_RESULT_MS   10
#define T_AFTER_RESULT_MS    10
#define T_CMD_PERIOD_MS      20     // PIC poll/emit cadence
#define T_CMD_MAX_WAIT_MS    12000  // End-to-end timeout

#endif // PROTOCOL_H
