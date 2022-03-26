#ifndef matrix_
#define matrix_

#include <iostream>
#include <vector>
using namespace std;

class matrix{
    public:
        matrix();
        ~matrix();
        void initMatrix(vector<vector<long double > > &mat, int size);
        void assignValue(vector<vector<long double > > &mat, int size, vector<vector<int> > _input);
        void getTranpose(vector<vector<long double > > &mat, vector<vector<long double > > &t_mat, int size);
        void showMatrix(vector<vector<long double > > &mat, int size);
        void setMatrix(vector<vector<long double > > &mat, int size);

};



#endif