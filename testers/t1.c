#include <stdio.h>
#include <unistd.h>

void main() {
	int i;
	for (i=0; i<10; i++) {
		printf("Waiting for %d\n", i);
		fprintf(stderr, "Waiting on stderr for %d\n", i);
		usleep(1000000);
	}
	return;
}
