robot: main.o robot.o matrix.o
	g++ -o robot main.o robot.o matrix.o
main.o: main.cpp robot.h matrix.h
	g++ -c -Wall -pedantic -g -std=c++11 main.cpp
robot.o: robot.cpp robot.h
	g++ -c -Wall -pedantic -g -std=c++11 robot.cpp
matrix.o: matrix.cpp matrix.h
	g++ -c -Wall -pedantic -g -std=c++11 matrix.cpp

clean:
	rm matrix.o main.o robot.o robot