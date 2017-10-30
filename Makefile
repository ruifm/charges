DB_FLAGS	= -Wall -g -ggdb -O3


CFLAGS_GTK	= `pkg-config --cflags glib-2.0` `pkg-config --cflags gtk+-2.0`

LINK_GTK	= `pkg-config --libs glib-2.0` `pkg-config --libs gtk+-2.0`
LINK_LIBS	= $(LINK_GTK) -lm


CFLAGS		= $(INC_FLAGS) $(CFLAGS_GTK) $(DB_FLAGS)
LFLAGS		= $(LINK_FLAGS) $(LINK_GTK)

CC		= gcc
CP		= cp
RM		= rm
LS		= ls

PROGS		= cargas eletric vector
OUT     = cargas.o eletric.o vector.o

all: comp link

link: 

comp: comp1

comp1: 
	for fname in $(PROGS); do $(CC) $(CFLAGS) -c $$fname.c ; done

link: link1

link1: 
	$(CC) $(LFLAGS) -o cargas $(OUT) $(LINK_LIBS)

clean:
	$(RM) -f *~ *.o $(PROGS)
