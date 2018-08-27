/*
 * prozeda_print.h
 *
 * Created: 29.10.2017 21:49:52
 *  Author: Chris
 */ 


#ifndef PROZEDA_PRINT_H_
#define PROZEDA_PRINT_H_

#include "prozeda.h"
#include "debug.h"

#define prozeda_println uart_debug_writeln
#define prozeda_print uart_debug_write
#define prozeda_putc uart_debug_putc

void print_logdata(prozeda_logdata_t* data);
void print_logdata_json(prozeda_logdata_t* data);

#endif /* PROZEDA_PRINT_H_ */
