// PS C:\Users\sethr\OneDrive\Desktop\Chess Board v2\polar_to_cartesian> g++ polar_to_cartesian.cpp -o polar_to_cartesian.exe
// PS C:\Users\sethr\OneDrive\Desktop\Chess Board v2\polar_to_cartesian> .\polar_to_cartesian.exe  

#include <iostream>
#include <cmath>
#include <string>
#include <utility>
#include <iomanip>

std::pair<std::string,double> shortestAngularDirection(double theta1, double theta2) {
    // normalize to [0,360)
    double t1 = fmod(theta1, 360.0); if (t1 < 0) t1 += 360.0;
    double t2 = fmod(theta2, 360.0); if (t2 < 0) t2 += 360.0;

    // signed difference t2 - t1
    double delta = t2 - t1;

    // normalize delta into (-180, 180]
    while (delta <= -180.0) delta += 360.0;
    while (delta > 180.0)  delta -= 360.0;

    const double EPS = 1e-12;
    if (std::fabs(delta) < EPS)
        return {"same", 0.0};

    // tie at ±180°: pick a policy (here I pick clockwise for tie)
    if (std::fabs(std::fabs(delta) - 180.0) < EPS)
        return {"clockwise", 180.0};

    if (delta > 0)
        return {"counter-clockwise", delta}; // positive => CCW by delta
    else
        return {"clockwise", -delta};         // negative => CW by -delta
}

int main() {
    double a, b;
    std::cout << "Enter a value: "; std::cin >> a;
    std::cout << "Enter another value: "; std::cin >> b;

    auto res = shortestAngularDirection(a, b);
    std::cout << "Shortest direction: " << res.first << " by " << res.second << " degrees\n";
    return 0;
}
