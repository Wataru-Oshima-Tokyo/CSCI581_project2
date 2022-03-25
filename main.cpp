#include <iostream>
#include <vector>
#include <fstream>
#include <math.h>
#include <bitset>
#include <string>
#include <sstream>
#include <iomanip>
using namespace std;
#define rep(i,a,b) for(int i=a; i<b;i++)


int main(int argc, char **argv){
    string observation_txt, input_txt;
    double epsilon =0;
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
            long double value = (double)1/(double)(input_vector[i+1][2]);
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
    int time_iteration = observation_vector.size();
    // Observation prob at time 0;
    long double observation_prob[time_iteration][mat_size];
    long double value[time_iteration][mat_size];
    rep(q,0, time_iteration){
        long double obs_t0[mat_size];
        long double value_t0 = (double)1/(double)(mat_size);
        for(int i=0;i<mat_size;i++){
            obs_t0[i] = value_t0;
        }
        for(int i=0;i<mat_size;i++){
            cout << obs_t0[i] <<endl;
        }
        //getting the JP at time 0
        long double jp_t0[mat_size];
        for(int i=0;i<mat_size;i++){
            long double temp=0;
            for(int j=0; j<mat_size;j++){
                temp += (double)t_matrix[i][j] * (double)obs_t0[j];
            }
            jp_t0[i] = temp;
        }
        cout << "show the joint probability at time 0"<< endl;
        //the sum of jp at time 0
        // Iteration 1;
        bitset<6> sensor_info[mat_size];
        bitset<6> obs_info[mat_size];
        rep(i,0,mat_size){
            sensor_info[i] = input_vector[i+1][1];
            cout << sensor_info[i] << endl;
            obs_info[i]=0;
        }
        rep(i,0, observation_vector[0][0]){
            bitset<6> tempbit=0;
            int digit = observation_vector[0][i+1];
            // cout << digit <<endl;
            switch (digit)
            {
            case 1:
                tempbit = 32 & 0xFF;
                break;
            case 2:
                tempbit = 16 & 0xFF;
                break;
            case 3:
                tempbit = 8 & 0xFF;
                break;
            case 4:
                tempbit = 4 & 0xFF;
                break;
            case 5:
                tempbit = 2 & 0xFF;
                break;
            case 6:
                tempbit = 1 & 0xFF;
                break;
            default:
                break;
            }
            obs_info[0] |=tempbit;
        
        }
        //  cout << obs_info[0] <<endl;
        //calculating the difference here at time 0 and E
        bitset<6> diff[mat_size];
        long double JE[mat_size];
        double sum = 0;
        rep(i,0,mat_size){
            diff[i] = sensor_info[i] ^ obs_info[0];
            // cout << " diff[i] "<< diff[i] <<endl;
            int diff_d = diff[i].count();
            // cout << diff_d <<endl;
            JE[i] = (double)pow((double)epsilon, diff_d)*(double)pow((double)(1-epsilon), (6-diff_d)) * jp_t0[i];
            cout << JE[i] <<endl;
            sum+=JE[i];
        }

        //Estimation probability at time 0 
        long double E[mat_size];
        cout << sum <<endl;
        rep(i,0,mat_size){
            E[i] = (long double)JE[i]/(long double)sum;
            cout << E[i] <<endl;
        }
        long double MAX =0;
        int idx = 0;
        rep(i,0,mat_size){
            long double temp = E[i];
            if(temp>MAX){
                MAX = temp;
                idx =i;
            } 
        }
        cout << showpoint << fixed << setprecision(16) << MAX << " " << idx <<endl;
    }
    

    return 0;
}
