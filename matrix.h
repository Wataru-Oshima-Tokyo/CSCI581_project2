#ifndef matrix_
#define matrix_

#include <iostream>
#include <vector>
using namespace std;

class matrix{
    public:
        matrix();
        ~matrix();
        void initMatrix(long double **mat, int size);
        void assignValue(long double **mat, int size, vector<vector<int> > _input);
        void getTranpose(long double **mat, long double **t_matrix, int size);
        void showMatrix(long double **mat, int size);
        void setMatrix(long double *mat, int size);

};



#endif