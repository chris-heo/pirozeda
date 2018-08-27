/*
 * prozeda.c
 *
 * Created: 05.02.2017 21:18:31
 *  Author: Chris
 */ 

#include <avr/pgmspace.h>
#include "prozeda.h"
#include "debug.h"

#ifdef PROZEDA_SUPPORT_SYSINFO
	volatile uint16_t prozeda_bytepos = 0;
#else
	volatile uint8_t prozeda_bytepos = 0;
#endif

prozeda_msgmode_t prozeda_msgmode = prozeda_msgmode_unknown;
volatile uint8_t prozeda_ticks = 0;
volatile uint8_t prozeda_buff[PROZEDA_BUFF_LEN];
volatile bool prozeda_process = false;

uint8_t* prozeda_logdata_ptr = NULL;
#ifdef PROZEDA_SUPPORT_DISPLAY
uint8_t* prozeda_displaydata_ptr = NULL;
#endif
#ifdef PROZEDA_SUPPORT_HEADER
uint8_t* prozeda_headerdata_ptr = NULL;
#endif

bool prozeda_checkMessage(uint8_t length, uint8_t expLength)
{
	//messages with length less 2 bytes are invalid
	if(expLength < 2 || expLength != length)
	{
		return false;
	}
	
	uint8_t sum = 0;
	expLength--;
	uint8_t checksum = prozeda_buff[expLength];
	while(expLength--)
	{
		sum += prozeda_buff[expLength];
	}
	
	if(sum == checksum)
	{
		return true;
	}
	return false;
}

prozeda_taskstatus_t prozeda_task(void)
{
	if(prozeda_process == false)
	{
		return prozeda_taskstatus_none;
	}
	//IOPIN_H(DBG2);
	prozeda_process = false;
	
	uint8_t len = prozeda_bytepos;
	prozeda_bytepos = 0;
	
	// disable and enable the SPI interface to flush it
	// with this, data corruption due to missed/double clocks
	// "kitty packet" is avoided
	prozeda_spi_disable();
	prozeda_spi_enable();
	
	prozeda_taskstatus_t status = prozeda_taskstatus_none;
	
	if(len == PROZEDA_MSGLEN_MSGTYPE)
	{
		//everything ok, now parse the data
		//check if it's a message type switcher
		if(arrcmp((const char*)prozeda_buff, "\xAA\x55\x55\xAA", 4))
		{
			prozeda_msgmode = (prozeda_buff[4] << 8) | prozeda_buff[5];
			status = prozeda_taskstatus_rxMsgtype;
		}
	}
	else if(prozeda_msgmode == prozeda_msgmode_logdata)
	{
		if(prozeda_checkMessage(len, PROZEDA_MSGLEN_LOGDATA))
		{
			if(prozeda_logdata_ptr != NULL)
			{
				memcpy(prozeda_logdata_ptr, (const void*)prozeda_buff, PROZEDA_MSGLEN_LOGDATA);
				status = prozeda_taskstatus_rxLogdata;
			}
			// return another status if ptr is NULL?
		}
		else
		{
			status = prozeda_taskstatus_rxError;
		}
	}
#ifdef PROZEDA_SUPPORT_DISPLAY
	else if(prozeda_msgmode == prozeda_msgmode_display)
	{
		if(len == PROZEDA_MSGLEN_DISPLAY)
		{
			if(prozeda_displaydata_ptr != NULL)
			{
				memcpy(prozeda_displaydata_ptr, (const void*)prozeda_buff, PROZEDA_MSGLEN_DISPLAY);
				status = prozeda_taskstatus_rxDisplaydata;
			}
		}
		else
		{
			status = prozeda_taskstatus_rxError;
		}
	}
#endif
#ifdef PROZEDA_SUPPORT_HEADER
	else if(prozeda_msgmode == prozeda_msgmode_header)
	{
		if(prozeda_checkMessage(len, PROZEDA_MSGLEN_HEADER))
		{
			if(prozeda_headerdata_ptr != NULL)
			{
				memcpy(prozeda_headerdata_ptr, (const void*)prozeda_buff, PROZEDA_MSGLEN_HEADER);
				status = prozeda_taskstatus_rxHeaderdata;
			}
		}
		
	}
#endif

/*#ifdef PROZEDA_SUPPORT_SYSDATA
	else if(prozeda_msgmode == prozeda_msgmode_sysdata)
	{
		if(prozeda_checkMessage(len, PROZEDA_MSGLEN_SYSDATA))
		{
			if(prozeda_displaydata_ptr != NULL)
			{
				memcpy(prozeda_displaydata_ptr, (const void*)prozeda_buff, PROZEDA_MSGLEN_SYSDATA);
				status = prozeda_taskstatus_rxSysdata;
			}
		}
	}
#endif*/

	else
	{
		status = prozeda_taskstatus_rxNotImplemented;
	}
	//IOPIN_L(DBG2);
	return status;
}