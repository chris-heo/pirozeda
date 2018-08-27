#include "debug.h"
#include "fifo.h"
#include "simpleio.h"
#include <stdbool.h>

volatile FIFO64_t uart_debug_fifo;
volatile bool uart_debug_running = false;

ISR(USART_TX_vect)
{
	if(FIFO_available(uart_debug_fifo))
	{
		UDR0 = FIFO64_read(uart_debug_fifo);
	}
	else
	{
		uart_debug_running = false;
	}
}

void uart_debug_init() {
	FIFO_init(uart_debug_fifo);
	//FIFO64_write(uart_debug_fifo, 0x00);
	//FIFO64_read(uart_debug_fifo);
	UBRR0 = 12; //115200 Bd @ 12 MHz
	UCSR0A |= (1<<U2X0);
	UCSR0B = (1<<TXCIE0) | (1<<TXEN0) | (0<<UCSZ02);
	//UCSR0B = (0<<TXCIE0) | (1<<TXEN0) | (0<<UCSZ02);
	UCSR0C = (0<<UMSEL01) | (0<<UMSEL00) | (0<<UPM01) | (0<<UPM00) | (0<<USBS0) | (1<<UCSZ01) | (1<<UCSZ00);
}

#define DBGO IOPIN(B, 0)

inline void uart_debug_putc(uint8_t c) {
	while(!FIFO64_free(uart_debug_fifo));
	
	FIFO64_write(uart_debug_fifo, c)
	
	if(uart_debug_running == false)
	{
		uart_debug_running = true;
		UDR0 = FIFO64_read(uart_debug_fifo);
	}
}

void uart_debug_puts(char *s) {
	while(*s)
	{
		uart_debug_putc(*s++);
	}
}

void uart_debug_write_P (const char *Buffer,...)
{
	va_list ap;
	va_start (ap, Buffer);	
	
	int format_flag;
	char str_buffer[10];
	char str_null_buffer[10];
	char move = 0;
	char Base = 0;
	char isSigned = 0;
	int tmp = 0;
	char by;
	char *ptr;
		
	//Ausgabe der Zeichen
    for(;;)
	{
		by = pgm_read_byte(Buffer++);
		if(by==0) break; // end of format string
		if (by == '%')
		{
			by = pgm_read_byte(Buffer++);
			if (isdigit(by)>0)
			{
				str_null_buffer[0] = by;
				str_null_buffer[1] = '\0';
				move = atoi(str_null_buffer);
				by = pgm_read_byte(Buffer++);
			}
			
			switch (by)
			{
				case 's':
					ptr = va_arg(ap,char *);
					while(*ptr) { uart_debug_putc(*ptr++); }
					break;
				case '%':
					uart_debug_putc('%');
					break;
				case 'b':
					Base = 2;
					goto ConversionLoop;
				case 'c':
					//Int to char
					format_flag = va_arg(ap,int);
					uart_debug_putc (format_flag++);
					break;
				case 'i':
					isSigned = 1;
					Base = 10;
					goto ConversionLoop;
				case 'u':
					Base = 10;
					goto ConversionLoop;
				case 'o':
					Base = 8;
					goto ConversionLoop;
				case 'x':
					Base = 16;
					//****************************
					ConversionLoop:
					//****************************
					if(isSigned == 1) {
						itoa(va_arg(ap,int),str_buffer,Base);
					} else {
						utoa(va_arg(ap,unsigned int),str_buffer,Base);
					}
					int b=0;
					while (str_buffer[b++] != 0){};
					b--;
					if (b<move)
						{
						move -=b;
						for (tmp = 0;tmp<move;tmp++)
							{
							str_null_buffer[tmp] = '0';
							}
						//tmp ++;
						str_null_buffer[tmp] = '\0';
						strcat(str_null_buffer,str_buffer);
						strcpy(str_buffer,str_null_buffer);
						}
					uart_debug_puts (str_buffer);
					move = 0;
					break;
			}
		}
		else
		{
			uart_debug_putc ( by );
		}
	}
	va_end(ap);
}
