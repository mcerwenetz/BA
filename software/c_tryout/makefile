CC=gcc
CFLAGS=-g -Wall -fsanitize=address

all: clib

clib : clib.c
	$(CC) $(CFLAGS) tryout.c -o tryout.exe -lws2_32

tryout.exe : tryout.c
	$(CC) $(CFLAGS) tryout.c -o tryout.exe -lws2_32

cJSON.exe : cJSONTryOut.c
	$(CC) $(CFLAGS) cJsonConfigRead.c cJSON.c -o cJsonConfigRead.exe -lm

.PHONY: clean

clean:
	del -f tryout.exe cJSON.exe
