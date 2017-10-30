#include <math.h>
#include "vector.h"
vector add(vector p1,vector p2){
	vector p;
	p.x=p1.x+p2.x;
	p.y=p1.y+p2.y;
	return p;
}
vector sub(vector p1,vector p2){
	vector p;
	p.x=p1.x-p2.x;
	p.y=p1.y-p2.y;
	return p;
}
vector factor(double k,vector p){
	vector r;
	r.x=k*p.x;
	r.y=k*p.y;
	return r;
}
double dot(vector p1,vector p2){
	return p1.x*p2.x+p1.y*p2.y;
}
double det(vector p1,vector p2){
	return p1.x*p2.y-p1.y+p2.x;
}
double norma(vector p){
	return dot(p,p);
}
vector unit(vector p){
	return factor(1./sqrt(norma(p)),p);
}
vector proj(vector r, vector v){
	return factor(dot(r,v)/norma(v),v);
}
double angle(vector r,vector p){
	return acos(dot(r,p)/sqrt(norma(r)*norma(p)));
}
vector rotation(vector v,double phi){
 vector a1,a2,r;
 a1.x=cos(phi);
 a1.y=-sin(phi);
 a2.x=sin(phi);
 a2.y=cos(phi);
 r.x=dot(a1,v);
 r.y=dot(a2,v);
 return r;
}
