/*
 * prozeda_cfg.h
 *
 * Created: 08.02.2017 21:17:24
 *  Author: Chris
 */ 


#ifndef PROZEDA_CFG_H_
#define PROZEDA_CFG_H_

#define PROZEDA_USE_COLUMN_NAMES 

// turn support for those long sysinfo-message on (not tested)
#define PROZEDA_SUPPORT_SYSDATA

#define PROZEDA_SUPPORT_DISPLAY
#define PROZEDA_SUPPORT_HEADER

// this should be equal to around 300 ... 400 µs
#define PROZEDA_MSG_MAXTICKS 3

// define the function for debug messages, comment out if not used.
#define prozeda_debug uart_debug_write
#define prozeda_debugln uart_debug_writeln

// was too lazy to do a better abstraction than this 
#define prozeda_spi_disable() SPCR &= ~(1<<SPE)
#define prozeda_spi_enable() SPCR |= (1<<SPE)


#endif /* PROZEDA_CFG_H_ */