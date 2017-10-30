#ifndef __VECTOR_H
#define __VECTOR_H
typedef struct {
	double x;
	double y;
} vector;
extern vector add(vector p1,vector p2);
extern vector sub(vector p1,vector p2);
extern vector factor(double k,vector p);
extern double dot(vector p1,vector p2);
extern double det(vector p1,vector p2);
extern double norma(vector p);
extern vector unit(vector p);
extern vector proj(vector r, vector v);
extern double angle(vector r,vector p);
extern vector rotation(vector v,double phi);
#endif
