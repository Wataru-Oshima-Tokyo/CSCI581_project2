#include "robot.h"

robot::robot(){

}
robot::~robot(){

}

long double robot::getInitValue(int size){
   return  (long double)1/(long double)(size);
}

long double robot::calculateJP(long double mat_value, long double obs_prob){
   return (long double)mat_value * (long double)obs_prob;
}

std::bitset<6> robot::getObs(int digit){
            std::bitset<6> tempbit=0;
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
    return tempbit;
}

long double robot::calculateJE(std::bitset<6> sensor_info,std::bitset<6>obs_info, long double ep, long double _jp){
            std::bitset<6> diff = sensor_info ^ obs_info;
            // cout << " diff[i] "<< diff[i] <<endl;
            int diff_d = diff.count();
            return (long double)pow((long double)ep, diff_d)*(long double)pow((long double)(1-ep), (6-diff_d)) * _jp;
}
long double robot::getE(long double je, long double sum){
    return (long double)je/(long double)sum;
}

void robot:: getEP(long double E, long double &MAX, std::vector<int> &idx, int i){
    long double temp = E;
    if(temp>MAX){
        MAX = temp;
        if(!idx.empty()){
            idx.clear();
        }
        // cout << temp << endl;
        idx.push_back(i);
    } else if(temp==MAX){
        idx.push_back(i);
    }
}