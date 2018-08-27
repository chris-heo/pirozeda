/*
 * prozeda.h
 *
 * Created: 05.02.2017 21:19:33
 *  Author: Chris
 */ 

#include <avr/io.h>
#include <stdbool.h>
#include "prozeda_cfg.h"
#include "common.h"

#ifndef PROZEDA_H_
#define PROZEDA_H_


//remove debug if not used
#ifndef prozeda_debug
	#define prozeda_debug(format, args...) /* there is no debug enabled */
#endif

#define PROZEDA_MSGLEN_MSGTYPE   6
#define PROZEDA_MSGLEN_REQUEST  33

//#define PROZEDA_MSGLEN_DISPLAY  64

//
#define PROZEDA_MSGLEN_DISPLAY  64
#define PROZEDA_MSGLEN_LOGDATA  68
#define PROZEDA_MSGLEN_HEADER   70
#define PROZEDA_MSGLEN_SYSDATA 260


#ifdef PROZEDA_SUPPORT_SYSDATA
#define PROZEDA_BUFF_LEN PROZEDA_MSGLEN_SYSDATA
#else
#define PROZEDA_BUFF_LEN PROZEDA_MSGLEN_HEADER
#endif

typedef enum
{
	prozeda_msgmode_unknown = 0,
	prozeda_msgmode_display = 0x0100,
	prozeda_msgmode_request = 0x0200,
	prozeda_msgmode_logdata = 0x0300,
	prozeda_msgmode_header  = 0x0301,
}	prozeda_msgmode_t;

typedef enum
{
	prozeda_taskstatus_none      = 0,
	prozeda_taskstatus_rxMsgtype = 1,
	prozeda_taskstatus_rxLogdata = 2,
	prozeda_taskstatus_rxDisplaydata = 3,
	prozeda_taskstatus_rxHeaderdata = 4,
	
	prozeda_taskstatus_rxNotImplemented = 0xFE,
	prozeda_taskstatus_rxError = 0xFF,
}	prozeda_taskstatus_t;

#define PROZEDA_COLUMNNAME_LEN 14

typedef enum
{
	prozeda_columntype_dummy       = 0x00,
	prozeda_columntype_temperature = 0x01,
	prozeda_columntype_date        = 0x08,
	prozeda_columntype_time        = 0x09,
	prozeda_columntype_output      = 0x0A,
	prozeda_columntype_error1      = 0x0E,
	prozeda_columntype_error2      = 0x0F,
	prozeda_columntype_seconds     = 0x10,
	prozeda_columntype_throughput  = 0x13,
	prozeda_columntype_tapping     = 0x1B,
}	prozeda_columntype_t;

typedef struct
{
	#ifdef PROZEDA_USE_COLUMN_NAMES
	char name[PROZEDA_COLUMNNAME_LEN + 1]; //don't forget the terminator
	#endif
	prozeda_columntype_t type;
	uint8_t index;
}	prozeda_column_t;

typedef struct
{
	uint16_t sof;
	uint16_t timestamp_date;
	uint16_t timestamp_time;
	uint16_t timestamp_seconds;
	int16_t  temperature[11];
	uint8_t  output[8];
	uint8_t  error[4]; // not sure about this
	uint32_t storage0; // not sure about this
	uint16_t dummy0; // not sure about this
	uint16_t storage1;
	uint16_t dummy1;
	uint16_t functionActive[4];
	uint16_t flowRate;
	int16_t tapping;
	uint16_t dummy2;
	uint8_t unknown0;
	uint8_t checksum;
}	prozeda_logdata_t;


#ifdef PROZEDA_SUPPORT_SYSINFO
extern volatile uint16_t prozeda_bytepos;
#else
extern volatile uint8_t prozeda_bytepos;
#endif

extern prozeda_msgmode_t prozeda_msgmode;
extern volatile uint8_t prozeda_buff[];
extern uint8_t* prozeda_logdata_ptr;

#ifdef PROZEDA_SUPPORT_DISPLAY
extern uint8_t* prozeda_displaydata_ptr;
#endif
#ifdef PROZEDA_SUPPORT_HEADER
extern uint8_t* prozeda_headerdata_ptr;
#endif

extern prozeda_msgmode_t prozeda_msgmode;
extern volatile uint8_t prozeda_ticks;
extern volatile bool prozeda_process;

prozeda_taskstatus_t prozeda_task(void);

inline void prozeda_tick(void)
{
	//IOPIN_H(DBG1);
	if(prozeda_ticks < 255)
	{
		prozeda_ticks++;
		if((prozeda_ticks >= PROZEDA_MSG_MAXTICKS) && (prozeda_bytepos > 0))
		{
			prozeda_process = true;
		}
	}
	//IOPIN_L(DBG1);
}

inline void prozeda_rxData(uint8_t data)
{
	//IOPIN_H(DBG0);
	uint8_t p = prozeda_bytepos;
	prozeda_ticks = 0;
	
	if(p < PROZEDA_BUFF_LEN)
	{
		prozeda_buff[p] = data;
		p++;
	}

	prozeda_bytepos = p;
	//IOPIN_L(DBG0);
}

#endif /* PROZEDA_H_ */