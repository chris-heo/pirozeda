/*
 * main.c
 *
 * Created: 30.01.2017 21:58:39
 * Author : Chris
 */ 

#include <avr/io.h>
#include "debug.h"
#include <avr/interrupt.h>
#include "simpleio.h"
#include "mx8p.h"
#include "prozeda.h"
#include "prozeda_print.h"
#include "common.h"
#include <avr/wdt.h>

#define SPI_MISO IOPIN(B, 4)
#define SPI_CS IOPIN(B, 2)

uint8_t proz_logdata[PROZEDA_MSGLEN_LOGDATA];
uint8_t proz_displaydata[PROZEDA_MSGLEN_DISPLAY];
uint8_t proz_headerdata[PROZEDA_MSGLEN_HEADER];

ISR(SPI_STC_vect)
{
	prozeda_rxData(SPDR);
}

ISR(TIMER0_COMPA_vect)
{
	prozeda_tick();
}

void rawprint(uint8_t * data, uint16_t length)
{
	for(uint16_t i = 0; i < length; i++)
	{
		uart_debug_write("%2x", data[i]);
	}
}

int main(void)
{
	wdt_enable(WDTO_2S);
	uart_debug_init();
	
	IOPIN_O(SPI_MISO);
	IOPIN_I(SPI_CS);
	IOPIN_H(SPI_CS); //enable pull-up for chip select
	
	// enable SPI slave
	SPCR = (1<<SPIE) | (1<<SPE) | (0<<DORD) | (0<<MSTR) | (0<<CPOL) | (0<<CPHA);
	
	// setup timer
	TCCR0A = timer0a_wgm_ctc;
	TCCR0B = timer0b_wgm_ctc | timer0_prescaler_8;
	
	// ticks
	// OCR0A = (time * F_CPU) / prescaler
	// pre 8 | 100 탎 => 150
	// pre 8 |  75 탎 => 112.5
	// pre 8 |  50 탎 =>  75
	// 150 => approx. 100 탎 @ 12 MHz
	OCR0A = 112; 
	TIMSK0 = 1<<OCIE0A;
	
	//init debug pins
	//IOPIN_O(DBG0);
	//IOPIN_L(DBG0);
	//IOPIN_O(DBG1);
	//IOPIN_L(DBG1);
	//IOPIN_O(DBG2);
	//IOPIN_L(DBG2);

	prozeda_logdata_ptr = (uint8_t *)&proz_logdata;
	prozeda_displaydata_ptr = (uint8_t *)&proz_displaydata;
	prozeda_headerdata_ptr = (uint8_t *)&proz_headerdata;
		
	sei();
	//maximum count of header lines to be output
	uint8_t headercnt = 200;
	
	uart_debug_writeln("Built on: " __DATE__ " " __TIME__);
	
    while (1) 
    {
		prozeda_taskstatus_t status = prozeda_task();
		
		if(status == prozeda_taskstatus_rxLogdata)
		{
			uart_debug_write("Logdata:");
			rawprint((uint8_t*)&proz_logdata, PROZEDA_MSGLEN_LOGDATA);
			uart_debug_write("\r\n");
			wdt_reset();
		}
		else if(status == prozeda_taskstatus_rxDisplaydata)
		{
			uart_debug_write("Display:");
			rawprint(proz_displaydata, PROZEDA_MSGLEN_DISPLAY);
			uart_debug_write("\r\n");
			wdt_reset();
		}
		else if(status == prozeda_taskstatus_rxHeaderdata)
		{
			if(headercnt > 0)
			{
				uart_debug_write("Header:");
				rawprint(proz_headerdata, PROZEDA_MSGLEN_HEADER);
				uart_debug_write("\r\n");
				wdt_reset();	
				headercnt--;
			}
		}
		else if(status == prozeda_taskstatus_rxError)
		{
			uart_debug_writeln("rxErr");
		}
		else if(status == prozeda_taskstatus_rxMsgtype)
		{
			//uart_debug_write("MsgType:%4x", prozeda_msgmode);
			//uart_debug_write("\r\n");
				
		}
    }
}

