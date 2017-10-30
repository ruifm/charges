#include <math.h>
#include "vector.h"
#include "eletric.h"
vector coulomb(charge c1,charge c2){
	if(sqrt(norma(sub(c1.pos,c2.pos)))>c2.radius)
		return factor((double)COUL*(c2.qt)/norma(sub(c1.pos,c2.pos)),unit(sub(c1.pos,c2.pos)));
	else {
		return factor(0,c1.pos);
	}
}
vector eletric(charge *q){
	int i;
	vector e=factor(0,q[0].pos);
	for(i=1;i<TOTAL;i++){
		e=add(e,coulomb(q[0],q[i]));
	}
	return e;
}
