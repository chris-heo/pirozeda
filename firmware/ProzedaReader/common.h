/*
 * common.h
 *
 * Created: 08.02.2017 21:59:25
 *  Author: Chris
 */ 


#ifndef COMMON_H_
#define COMMON_H_

#define DECIMALPOINT '.'


#include "simpleio.h"
#include "avr/pgmspace.h"
#include <stdbool.h>

#define DBG0 IOPIN(B, 0)
#define DBG1 IOPIN(D, 7)
#define DBG2 IOPIN(D, 6)


#define arraySize(arr) (sizeof(arr) / sizeof(typeof(*arr)))

#define arrcmp(s1, s2, len) arrcmp_P(s1, PSTR(s2), len)
// compare an array from ram (s1) to a string in progmem (s2) with given length (len)
bool arrcmp_P(const char *s1, const char *s2, uint8_t len);
void itoa_fixed(int16_t val, char* Buffer, uint8_t decimalplaces);
#endif /* COMMON_H_ */
