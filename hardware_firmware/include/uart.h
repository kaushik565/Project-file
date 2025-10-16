#ifndef UART_H
#define UART_H

#include <p18cxxx.h>

void uart_init_115200(void);
unsigned char uart_read_byte_nonblock(unsigned char* out);
void uart_write_byte(unsigned char b);

#endif // UART_H