/*
 * common.c
 *
 * Created: 18.02.2017 23:29:41
 *  Author: Chris
 */ 

#include "common.h"

bool arrcmp_P(const char *s1, const char *s2, uint8_t len)
{
	//s2 is a pointer to progmem
	while(len--)
	{
		if(*s1++ != pgm_read_byte(s2++))
		{
			return false;
		}
		
	}
	return true;
}

void itoa_fixed(int16_t val, char* Buffer, uint8_t decimalplaces)
{
	uint8_t i = 0;
	uint8_t j;
	char tmp;
	uint16_t u;

	if( val < 0 ) {
		Buffer[0] = '-';
		Buffer++;
		
		u = (uint16_t)(val * -1);
	}
	else {
		u = (uint16_t)val;
	}
	
	//gimme a break, why would you even use this function if there was no decimal place?
	if(decimalplaces > 0)
	{
		while(decimalplaces--)
		{
			Buffer[i++] = '0' + u % 10;
			u /= 10;
		}
	
		Buffer[i++] = DECIMALPOINT;
	}
	
	do {
		Buffer[i++] = '0' + u % 10;
		u /= 10;
	} while(u > 0);

	Buffer[i] = '\0';
	// reverse the string
	for(j = 0; j < i / 2; ++j ) {
		tmp = Buffer[j];
		Buffer[j] = Buffer[i-j-1];
		Buffer[i-j-1] = tmp;
	}
	
}