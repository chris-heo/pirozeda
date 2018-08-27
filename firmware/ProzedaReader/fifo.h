//https://www.mikrocontroller.net/articles/FIFO

#ifndef FIFO_H_
#define FIFO_H_

#include <stdint.h>

typedef struct {
	volatile uint8_t _read;
	volatile uint8_t _write;
	volatile uint8_t _buffer[64];
} FIFO64_t;

typedef struct {
	volatile uint8_t _read;
	volatile uint8_t _write;
	volatile uint8_t _buffer[128];
} FIFO128_t;

#define FIFO_init(fifo)         { fifo._read = 0; fifo._write = 0; }

#define FIFO_available(fifo)    ( fifo._read != fifo._write )

#define FIFO_read(fifo, size) (                                         \
(FIFO_available(fifo)) ?                                        \
fifo._buffer[fifo._read = (fifo._read + 1) & (size-1)] : 0      \
)

#define FIFO_free(fifo, size) ((( fifo._write + 1 ) & (size-1)) != fifo._read)


#define FIFO_write(fifo, data, size) {                                                          \
	uint8_t tmphead = ( fifo._write + 1 ) & (size-1);       /* calculate buffer index */    \
	if(tmphead != fifo._read) {                             /* if buffer is not full */     \
		fifo._buffer[tmphead] = data;                   /* store data in buffer */      \
		fifo._write = tmphead;                          /* store new index */           \
	}                                                                                       \
}

#define FIFO64_read(fifo)			FIFO_read(fifo, 64)
#define FIFO64_write(fifo, data)		FIFO_write(fifo, data, 64)
#define FIFO64_free(fifo)		FIFO_free(fifo, 64)

#define FIFO128_read(fifo)			FIFO_read(fifo, 128)
#define FIFO128_write(fifo, data)		FIFO_write(fifo, data, 128)
#define FIFO128_free(fifo)		FIFO_free(fifo, 128)

#endif /*FIFO_H_*/