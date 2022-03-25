#include "matrix.h"


matrix::matrix(){

}

matrix::~matrix(){

}

void matrix::setMatrix(long double *mat, int size){
    mat = new long double[size];
};

void matrix::initMatrix(long double **mat, int size){
    for(int i=0; i<size; i++){
        for(int j =0; j<size; j++){
            mat[i][j] =0;
        }
    }
}

void matrix::assignValue(long double **mat, int size, vector<vector<int> > _input){
    
    for(int i=0; i<size; i++){
        for(int j=0; j<_input[i+1][2];j++){
            int location = _input[i+1][j+3];
            long double value = (long double)1/(long double)(_input[i+1][2]);
            // cout << input_vector[i+1][j+3] << " ";
            mat[i][location] = value;
        }
        // cout <<endl;
        }
}

void matrix::getTranpose(long double **mat, long double **t_matrix, int size){
    for(int i=0; i<size; i++){
        for(int j =0; j<size;j++){
            t_matrix[j][i] = mat[i][j];
        }
    }
}

void matrix::showMatrix(long double **mat, int size){
    for (int i = 0; i < size; ++i){
        for (int j = 0; j < size; ++j) {
            cout << mat[i][j] << " ";
        }
        // cout << endl;
    }
}