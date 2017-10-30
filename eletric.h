#ifndef __ELETRIC_H
#define __ELETRIC_H
#include "vector.h"
#define COUL 1e6
#define TOTAL 4
typedef struct {
	vector pos;
	vector vel;
	double qt;
	double mass;
	vector a;
	vector force;
	int radius;
	char name[3];
} charge;

vector coulomb(charge c1,charge c2);
vector eletric(charge *q);
#endif
