#include <iostream>
#include <vector>
#include <fstream>
#include <math.h>
#include <bitset>
#include <string>
#include <sstream>
#include <iomanip>
#include "robot.h"
#include "matrix.h"
using namespace std;
#define rep(i,a,b) for(int i=a; i<b;i++)


int main(int argc, char **argv){
    string observation_txt, input_txt;
    long double epsilon =0;
    if(argc==4){
        observation_txt = argv[3];
        input_txt = argv[1];
        epsilon = atof(argv[2]);
    }else{
        cout << "hell no! put 2 files and 1 probability" <<endl;
        exit(-1);
    }
    ifstream observation_file(observation_txt);
    vector<vector<int > > observation_vector;
    vector<vector<int > > input_vector;
    if (observation_file.is_open())
    {  
        string temp;
        while(getline(observation_file, temp)){
            vector<int> temp_vec;
            std::istringstream iss(temp);
            string tempint;
            while(iss >> tempint){
                // std::istringstream _iss(tempint);
                temp_vec.push_back(atoi(tempint.c_str()));
            }
            observation_vector.push_back(temp_vec);
            // cout << observation_vector[0][0] <<endl;
        }
        
    }
    observation_file.close();
    ifstream input_file(input_txt);
    if (input_file.is_open())
    {  
        string temp;
        while(getline(input_file, temp)){
            vector<int> temp_vec;
            std::istringstream iss(temp);
            string tempint;
            while(iss >> tempint){
                // std::istringstream _iss(tempint);
                temp_vec.push_back(atoi(tempint.c_str()));
            }
            input_vector.push_back(temp_vec);

            // cout << input_vector <<endl;
        }        
    }
    // std::vector<vector<int> >::iterator it;
    // std::vector<int>::iterator jt;
    for(int i=0; i<input_vector.size();i++){
        for(int j=0; j<input_vector[i].size();j++){
            // cout << input_vector[i][j] << " ";
        }
        // printf("\n");
    }
    input_file.close();

    int mat_size = input_vector[0][0];
    // cout << "mat size is " << mat_size << endl;
    // long double** _matrix = new long double*[mat_size];
    // long double** t_matrix = new long double*[mat_size];
    vector<vector<long double > > _matrix;
    vector<vector<long double > > t_matrix;
    _matrix.resize(mat_size, vector<long double>(mat_size));
    t_matrix.resize(mat_size, vector<long double>(mat_size));
    // long double** t_matrix = (long double **)alloca(sizeof(int) * mat_size);
    // matrix[0][0] =1;
    robot rb;
    matrix mt;
    // rep(i,0,mat_size){
        
    //     _matrix[i] = new long double[mat_size];
    //     t_matrix[i] = new long double[mat_size];
    // } 
    
    // mt.initMatrix(_matrix, mat_size);
    mt.assignValue(_matrix, mat_size, input_vector);
    mt.getTranpose(_matrix, t_matrix, mat_size);
    // mt.showMatrix(_matrix, mat_size);
    // for(int i=0; i<mat_size; i++){
    //     for(int j =0; j<mat_size;j++){
    //         _matrix[i][j] =0;
    //     }
    // }
    
    // for(int i=0; i<mat_size; i++){
    //     for(int j=0; j<input_vector[i+1][2];j++){
    //         int location = input_vector[i+1][j+3];
    //         long double value = (long double)1/(long double)(input_vector[i+1][2]);
    //         // cout << input_vector[i+1][j+3] << " ";
    //         matrix[i][location] = value;
    //         t_matrix[location][i] = matrix[i][location];
    //     }
    //     // cout <<endl;
    // }

    // cout <<  "show the matrix after assigning numnber"<<endl;

    // for(int i=0; i<mat_size; i++){
    //     for(int j =0; j<mat_size;j++){
    //         // cout << matrix[i][j] << " ";
    //         t_matrix[j][i] = matrix[i][j];
    //     }
    //     // cout <<endl;
    // }
    // cout <<  "show the transpose matrix after assigning numnber"<<endl;
    // for (int i = 0; i < mat_size; ++i){
    //     for (int j = 0; j < mat_size; ++j) {
    //         // cout << t_matrix[i][j] << " ";
    //     }
    //     // cout << endl;
    // }
    int time_iteration = observation_vector.size();
    // Observation prob at time 0;
    vector<vector<long double> > observation_prob;
    observation_prob.resize(time_iteration, vector<long double>(mat_size));
    // long double observation_prob[time_iteration][mat_size];
    // long double value[time_iteration][mat_size];
    vector<vector<long double> > value;
    value.resize(time_iteration, vector<long double>(mat_size));
    // long double JE[mat_size];
    vector<long double> JE;
    JE.resize(mat_size);
    rep(q,0, time_iteration){
        // bitset<6> *diff = new bitset<6>[mat_size];
        bitset<6> *sensor_info= new bitset<6>[mat_size];
        bitset<6> *obs_info= new bitset<6>[mat_size];
        vector<long double> E;
        E.resize(mat_size);
        // long double E[mat_size];
        long double sum = 0;
        long double MAX = -1;
        vector<int> idx;
        if(q==0){
            rep(i,0,mat_size) value[q][i] = rb.getInitValue(mat_size);
        }else{
            rep(i,0,mat_size){
                value[q][i] = JE[i];
            }
        }
        for(int i=0;i<mat_size;i++){
            observation_prob[q][i] = value[q][i];
        }
        //getting the JP at time 0
        // long double _jp[mat_size];
        vector<long double > _jp;
        _jp.resize(mat_size);
        for(int i=0;i<mat_size;i++){
            long double temp=0;
            for(int j=0; j<mat_size;j++){
                temp += rb.calculateJP(t_matrix[i][j], observation_prob[q][j]);
            }
            _jp[i] = temp;
        }

        //convert decimal to binary 
        rep(i,0,mat_size){
            sensor_info[i] = input_vector[i+1][1];
            obs_info[i]=0;
        }
        //calucate observation from observation.txt
        rep(i,0, observation_vector[q][0]){
            obs_info[q] |= rb.getObs(observation_vector[q][i+1]);
        }
        //calculate Joint Estimation
        rep(i,0,mat_size){
            JE[i] = rb.calculateJE(sensor_info[i],obs_info[q], epsilon, _jp[i]);
            sum+=JE[i];
        }
        
        //get Estimation
        rep(i,0,mat_size){
            E[i] = rb.getE(JE[i],sum);
        }
        //get estimation probability
        rep(i,0,mat_size){
            rb.getEP(E[i], MAX, idx,i);
        }

        //show the highest probability and state
        cout << showpoint << fixed << setprecision(16) << MAX << " ";
        rep(i,0,idx.size()) cout << idx[i] << " ";

        //initialize the vector idx
        idx.clear();
        cout << endl;
        delete[] sensor_info;
        delete[] obs_info;
    }
    

    return 0;
}
