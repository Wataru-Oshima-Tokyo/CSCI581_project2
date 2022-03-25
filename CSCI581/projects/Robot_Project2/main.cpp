#include <iostream>
#include <vector>
#include <fstream>
#include <math.h>
#include <bitset>
#include <string>
#include <sstream>
using namespace std;

int main(int argc, char **argv){
    string observation_txt, input_txt;
    double probability =0;
    if(argc==4){
        observation_txt = argv[1];
        input_txt = argv[3];
        probability = atof(argv[2]);
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
            cout << input_vector[i][j] << " ";
        }
        printf("\n");
    }
    input_file.close();

    int mat_size = input_vector[0][0];
    cout << "mat size is " << mat_size << endl;
    double matrix[mat_size][mat_size];
    double t_matrix[mat_size][mat_size];
    // matrix[0][0] =1;
    
    for(int i=0; i<mat_size; i++){
        for(int j =0; j<mat_size;j++){
            matrix[i][j] =0;
        }
    }
    
    for(int i=0; i<mat_size; i++){
        for(int j=0; j<input_vector[i+1][2];j++){
            int location = input_vector[i+1][j+3];
            double value = (double)1/(double)(input_vector[i+1][2]);
            cout << input_vector[i+1][j+3] << " ";
            matrix[i][location] = value;
            t_matrix[location][i] = matrix[i][location];
        }
        cout <<endl;
    }

    cout <<  "show the matrix after assigning numnber"<<endl;
    for(int i=0; i<mat_size; i++){
        for(int j =0; j<mat_size;j++){
            cout << matrix[i][j] << " ";
            t_matrix[j][i] = matrix[i][j];
        }
        cout <<endl;
    }
    cout <<  "show the transpose matrix after assigning numnber"<<endl;
    for (int i = 0; i < mat_size; ++i){
        for (int j = 0; j < mat_size; ++j) {
            cout << t_matrix[i][j] << " ";
        }
        cout << endl;
    }
    
    // Observation prob at time 0;
    double obs_t0[mat_size];
    double value_t0 = (double)1/(double)(mat_size);
    for(int i=0;i<mat_size;i++){
        obs_t0[i] = value_t0;
    }
    for(int i=0;i<mat_size;i++){
        cout << obs_t0[i] <<endl;
    }
    //getting the JP at time 0
    double jp_t0[mat_size];
    for(int i=0;i<mat_size;i++){
        double temp=0;
        for(int j=0; j<mat_size;j++){
            temp += (double)t_matrix[i][j] * (double)obs_t0[j];
        }
        jp_t0[i] = temp;
    }
    cout << "show the joint probability at time 0"<< endl;
    //the sum of jp at time 0
    double sum_t0=0;
    for(int i=0;i<mat_size;i++){
        cout << jp_t0[i] <<endl;
        sum_t0 +=jp_t0[i];
    }
    cout << "The sum of estimation" <<endl;
    cout <<sum_t0 <<endl;

    // cout << "The joint prediction probability at time 0" <<endl;
    // for(int i=0;i<mat_size;i++){
    //     cout << (double)jp_t0[i]/(double)(sum_t0) <<endl;
    // }
    // bitset<6> b4 = 51;
    // cout << b4 << endl;
    // int a = 1 & 0xFF;
    // int b = a >> 24 & 0xFF;
    // cout << b3.count()<< endl;
    // ifstream 
    // cout << b2 << endl;
    return 0;
}
