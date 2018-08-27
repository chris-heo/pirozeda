/*
 * debug.h
 *
 * Created: 25.09.2012 16:05:24
 *  Author: Chris
 */ 

#include <avr/interrupt.h>
#include <avr/pgmspace.h>
#include <stdlib.h>
#include <stdarg.h>
#include <ctype.h>
#include <string.h>

#ifndef DEBUG_H_
#define DEBUG_H_

void uart_debug_putc(uint8_t c);
void uart_debug_puts(char *s);
void uart_debug_init();


void uart_debug_write_P (const char *Buffer,...);
#define uart_debug_write(format, args...)   uart_debug_write_P(PSTR(format) , ## args)
#define uart_debug_writeln(format, args...)   uart_debug_write_P(PSTR(format "\r\n") , ## args)


#endif /* DEBUG_H_ */



