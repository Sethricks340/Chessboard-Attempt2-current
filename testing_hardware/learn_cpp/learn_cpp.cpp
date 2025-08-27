// PS C:\Users\sethr\OneDrive\Desktop\Chess Board v2\learn_cpp> g++ learn_cpp.cpp -o learn_cpp.exe
// PS C:\Users\sethr\OneDrive\Desktop\Chess Board v2\learn_cpp> .\learn_cpp.exe  

#include <iostream>
#include <cmath>
#include <cstdlib>
#include <ctime>

using namespace std;

// int main() {
//     // const means that value can't change 
//     const double pi = 3.14;
//     int file_size = 100;
//     double sales = 9.99;

//     int x = 10;
//     // int y = x++;   // x= 11, y = 10    x incremented after assigned to y 
//     // int z = ++x; //x = 11, z = 11;     x is incremented first, and then assigned to z

//     // std::cout << "x = ";    
//     // std::cout << x;  
    
//     cout << "x = " << x << endl  //dont need std because of namespace std
//               << "this is the second line. " << x; // two lines, one statement

//     // std::cout << file_size - sales; // cout -> character out 
//     // python equivalent -> std.count.write("Hello World")
//     return 0;
// }

// int main() {
//     cout << "Enter a value: ";
//     int value;
//     cin >> value; //stream extraction operator -> >> (cin -> character in )
//     cout << value;
//     return 0;
// }

// int main() {
//     cout << "Fahrenheit: ";
//     int fahr;
//     cin >> fahr;
//     double celsius = (fahr - 32) / 1.8;
//     cout << celsius;
//     return 0;
// }

// int main() {
//     double result = floor(1.2);
//     cout << result << " ";
//     result = pow(2, 3);
//     cout << result;
//     return 0;
// }

// int main(){
//     double price = 99.99;
//     float interestRate = 3.67f;
//     long fileSize = 900000L;
//     char letter = 'a';
//     bool isValid = false;
//     auto isValid = false;

//     // int number = 1.2;
//     // cout << number ; //will print 1

//     int number {1.2}; //brace initializer stops from compiling
//     cout << number ;
//     return 0;
// }

// int main(){
//     int number = 0xff; 
//     cout << number;
//     number = 0b11111111; 
//     cout << number;
//     number = 255;
//     cout << number;
//     unsigned int number = 0; //this cant be negative
//     return 0;
// }

int main(){
    // time(nullptr); //Jan 1 1970'
    srand(time(nullptr));
    int number = rand() % 10;
    cout << number;
    return 0;
}