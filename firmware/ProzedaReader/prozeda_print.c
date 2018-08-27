/*
 * prozeda_print.c
 *
 * Created: 29.10.2017 21:47:43
 *  Author: Chris
 */ 

#include "prozeda_print.h"

void print_logdata(prozeda_logdata_t* data)
{
	char buff[10];
	
	prozeda_println("%2u.%2u. %2u:%2u:%2u",
	data->timestamp_date % 100, data->timestamp_date / 100,
	data->timestamp_time / 60, data->timestamp_time % 60, data->timestamp_seconds
	);
	
	for(uint8_t i = 0; i < 11; i++)
	{
		itoa_fixed(data->temperature[i], buff, 1);
		prozeda_println(" T[%u]: %s °C", i, buff);
	}
	
	for(uint8_t i = 0; i < 8; i++)
	{
		prozeda_println(" out[%u]: %u", i, data->output[i]);
	}
	
	for(uint8_t i = 0; i < 4; i++)
	{
		prozeda_println(" error[%u]: %u", i, data->error[i]);
	}
	
	
	prozeda_println(" storage[0]: %u", data->storage0);
	prozeda_println(" storage[1]: %u", data->storage1);
	
	
	for(uint8_t i = 0; i < 4; i++)
	{
		prozeda_println(" func[%u]: %u", i, data->functionActive[i]);
	}
	
	itoa_fixed(data->flowRate, buff, 1);
	prozeda_println(" flowRate: %s", buff);
	
	itoa_fixed(data->tapping, buff, 1);
	prozeda_println(" tapping: %s", buff);
}

void print_logdata_json(prozeda_logdata_t* data)
{
	char buff[10];
	
	prozeda_print("{ \"time\" : \"%2u.%2u. %2u:%2u:%2u\", ",
		data->timestamp_date % 100, data->timestamp_date / 100,
		data->timestamp_time / 60, data->timestamp_time % 60, data->timestamp_seconds
		);
		
		prozeda_print("\"temps\" : [");
		
		for(uint8_t i = 0; i < 11; i++)
		{
			itoa_fixed(data->temperature[i], buff, 1);
			prozeda_print(" %s", buff);
			if(i < 10)
			{
				prozeda_putc(',');
			}
		}
		
		prozeda_print(" ], \"out\" : [");
		for(uint8_t i = 0; i < 8; i++)
		{
			prozeda_print(" %u", data->output[i]);
			if(i < 7)
			{
				prozeda_putc(',');
			}
		}
		
		prozeda_print(" ], \"error\" : [");
		for(uint8_t i = 0; i < 4; i++)
		{
			prozeda_print(" %u", data->error[i]);
			if(i < 3)
			{
				prozeda_putc(',');
			}
		}
		
		prozeda_print(" ], \"storage\" : [ %u, %u], \"func\" : [", data->storage0, data->storage1);
		for(uint8_t i = 0; i < 4; i++)
		{
			prozeda_print(" %u", data->functionActive[i]);
			if(i < 3)
			{
				prozeda_putc(',');
			}
		}
		
		itoa_fixed(data->flowRate, buff, 1);
		prozeda_print("], \"flowRate\" : %s", buff);
		
		itoa_fixed(data->tapping, buff, 1);
		prozeda_print(", \"tapping\" : %s", buff);
		
		prozeda_print(", \"dummy\" : [ 0x%4x, 0x%4x, 0x%4x ]", data->dummy0, data->dummy1, data->dummy2);
		prozeda_print(", \"unknown\" : 0x%2x }", data->unknown0);
		
		
	
}