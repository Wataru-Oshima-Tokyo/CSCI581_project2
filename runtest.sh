./robot $(cat tests/t01.cmd) >t01.my
 diff t01.my tests/t01.out
./robot $(cat tests/t02.cmd) >t02.my
 diff t02.my tests/t02.out
./robot $(cat tests/t03.cmd) >t03.my
 diff t03.my tests/t03.out
./robot $(cat tests/t04.cmd) >t04.my
 diff t04.my tests/t04.out
./robot $(cat tests/t05.cmd) >t05.my
 diff t05.my tests/t05.out
./robot $(cat tests/t06.cmd) >t06.my
diff t06.my tests/t06.out
