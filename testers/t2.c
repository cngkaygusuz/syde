#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>

void main() {
	while (1) {
	    int i;
	    for (i=0; i<1; i++) {
            void *d1 = malloc(10);
            void *d2 = malloc(10);
            void *d3 = malloc(10);
            void *d4 = malloc(10);
            void *d5 = malloc(10);

            free(d1);
            free(d2);
            free(d3);
            free(d4);
            free(d5);
        }
        printf("Sleeping now\n");
        usleep(250000);
	}

	return;
}
