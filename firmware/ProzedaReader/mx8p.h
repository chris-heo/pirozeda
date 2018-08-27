/*
 * m328p.h
 *
 * Created: 12.01.2017 20:27:12
 *  Author: Chris
 */ 


#ifndef M328P_H_
#define M328P_H_


typedef enum
{
	timer0_prescaler_off    = (0<<CS02) | (0<<CS01) | (0<<CS00),
	timer0_prescaler_1      = (0<<CS02) | (0<<CS01) | (1<<CS00),
	timer0_prescaler_8      = (0<<CS02) | (1<<CS01) | (0<<CS00),
	timer0_prescaler_64     = (0<<CS02) | (1<<CS01) | (1<<CS00),
	timer0_prescaler_256    = (1<<CS02) | (0<<CS01) | (0<<CS00),
	timer0_prescaler_1024   = (1<<CS02) | (0<<CS01) | (1<<CS00),
	timer0_prescaler_T0fall = (1<<CS02) | (1<<CS01) | (0<<CS00),
	timer0_prescaler_T0rise = (1<<CS02) | (1<<CS01) | (1<<CS00),
}	timer0_prescaler_t;

typedef enum
{
	timer0a_wgm_normal    = (0<<WGM01) | (0<<WGM00), //< Normal
	timer0a_wgm_pwmPc0    = (0<<WGM01) | (1<<WGM00), //< PWM, Phase correct, Top: 0xFF, Update: Top
	timer0a_wgm_ctc       = (1<<WGM01) | (0<<WGM00), //< CTC, Top: OCRA, Update: Immediate
	timer0a_wgm_pwmFast0  = (1<<WGM01) | (1<<WGM00), //< Fast PWM, Top: 0xFF, Update: Bottom
	timer0a_wgm_reserved0 = (0<<WGM01) | (0<<WGM00),
	timer0a_wgm_pwmPc1    = (0<<WGM01) | (1<<WGM00), //< PWM, Phase correct, Top: PCRA, Update: Top
	timer0a_wgm_reserved1 = (1<<WGM01) | (0<<WGM00),
	timer0a_wgm_pwmFast1  = (1<<WGM01) | (1<<WGM00), //< Fast PWM, Top: OCRA, Update: Bottom
}	timer0a_wgm_t;


typedef enum
{
	timer0b_wgm_normal    = (0<<WGM02), //< Normal
	timer0b_wgm_pwmPc0    = (0<<WGM02), //< PWM, Phase correct, Top: 0xFF, Update: Top
	timer0b_wgm_ctc       = (0<<WGM02), //< CTC, Top: OCRA, Update: Immediate
	timer0b_wgm_pwmFast0  = (0<<WGM02), //< Fast PWM, Top: 0xFF, Update: Bottom
	timer0b_wgm_reserved0 = (1<<WGM02),
	timer0b_wgm_pwmPc1    = (1<<WGM02), //< PWM, Phase correct, Top: PCRA, Update: Top
	timer0b_wgm_reserved1 = (1<<WGM02),
	timer0b_wgm_pwmFast1  = (1<<WGM02), //< Fast PWM, Top: OCRA, Update: Bottom
}	timer0b_wgm_t;


#endif /* M328P_H_ */