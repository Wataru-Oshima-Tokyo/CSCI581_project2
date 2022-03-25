#ifndef robot_
#define robot_

#include <bitset>
#include <math.h>
#include <vector>
class robot{
    public:
        long double getInitValue(int size);
        long double calculateJP(long double, long double);
        std::bitset<6> getObs(int digit);
        long double calculateJE(std::bitset<6> sensor_info,std::bitset<6>obs_info, long double ep, long double _jp);
        long double getE(long double, long double);
        void getEP(long double E, long double &MAX, std::vector<int> &idx, int i);
        robot();
        ~robot();
};

#endif