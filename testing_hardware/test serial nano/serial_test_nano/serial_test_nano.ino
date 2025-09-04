/*
Git repo: C:\Users\sethr\Chessboard-Attempt2-current

Known Issues:

The rack pops out vertically sometimes when it is at the end and hitting the spring.

"Breaking out: new serial data detected" prints a million times when breaking out, and sometimes doesn't break out

Electromagnet wires potentially could get tangled up and stressed/broken with current arrangment

Go home sequence sometimes fails when the magnet starts close to the reed, even though I tried to fix that previously

(-3,3) -> (3,3) works semi-well, along with (3,-3) -> (-3,-3)
  BUT (3,3) -> (3, -3) and (-3, -3) -> (-3,3) don't work at all. The radius doesn't even try to adjust.

homing sequence seems to have stopped working. it looks like the culprit is plate_tick. Plate tick is causing issues in the find reed initial and the center home functions

TODO: 

  Cartesian can have floats?

  Make Cart straight lines be able to go through the center

  Screw electromagnet onto holder

  try to understand ISRs that chat wrote 

  figure out how to keep the rack from popping out 

*/

#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <Servo.h>
#include <avr/pgmspace.h>

Servo motorServo;   // Plate
Servo motorServo2;  // Pinion
const int SERVO_PIN = 12; // Plate
const int SERVO_PIN2 = 11; //Pinion
const int STOP_US = 1500;

const int PLATE_FULL_CW_US = 2000;
const int PLATE_FULL_CCW_US = 1000;
// const int PLATE_HALF_CW_US = 1600;
const int PLATE_HALF_CW_US = 1750;
// const int PLATE_HALF_CCW_US = 1400;
const int PLATE_HALF_CCW_US = 1350;

const int RACK_FULL_DEC_US = 2000;
const int RACK_FULL_INC_US = 1000;
// const int RACK_HALF_DEC_US = 1600;
const int RACK_HALF_DEC_US = 1750;
// const int RACK_HALF_INC_US = 1400;
const int RACK_HALF_INC_US = 1350;

LiquidCrystal_I2C lcd(0x27, 16, 2);

// Define rotary encoder pins
#define ENC_A 4 // Plate // PB0
#define ENC_B 5  

#define ENC_C 7 // Pinion // PD7
#define ENC_D 8

volatile int encoder1Pos = 0;
volatile int encoder2Pos = 0;

volatile int globalDegrees = 0;
volatile float globalRadius = 0;

const int8_t enc_states[] = {
  0, -1, 1, 0,
  1, 0, 0, -1,
 -1, 0, 0, 1,
  0, 1, -1, 0
};

// Encoder 1 state
volatile uint8_t e1_old = 3;

// Encoder 2 state
volatile uint8_t e2_old = 3;

struct Polar {
  double r;
  double theta;  // degrees
};

struct Tuple {
  int8_t x;
  int8_t y;
};

// Generate tuples from (-3,3) to (3,-3), row by row (y descending, x ascending)
const Tuple mapping[49] PROGMEM = {
  {-3,  3}, {-2,  3}, {-1,  3}, {0,  3}, {1,  3}, {2,  3}, {3,  3},  // a–g
  {-3,  2}, {-2,  2}, {-1,  2}, {0,  2}, {1,  2}, {2,  2}, {3,  2},  // h–n
  {-3,  1}, {-2,  1}, {-1,  1}, {0,  1}, {1,  1}, {2,  1}, {3,  1},  // o–u
  {-3,  0}, {-2,  0}, {-1,  0}, {0,  0}, {1,  0}, {2,  0}, {3,  0},  // v–B
  {-3, -1}, {-2, -1}, {-1, -1}, {0, -1}, {1, -1}, {2, -1}, {3, -1},  // C–I
  {-3, -2}, {-2, -2}, {-1, -2}, {0, -2}, {1, -2}, {2, -2}, {3, -2},  // J–P
  {-3, -3}, {-2, -3}, {-1, -3}, {0, -3}, {1, -3}, {2, -3}, {3, -3}   // Q–W
};

ISR(PCINT2_vect) { // Port D: 4,5,7
  // --- Encoder 1 ---
  uint8_t e1_new = 0;
  if (PIND & (1 << PIND4)) e1_new |= 0x02;
  if (PIND & (1 << PIND5)) e1_new |= 0x01;

  uint8_t idx1 = ((e1_old << 2) | e1_new) & 0x0F;
  int delta1 = enc_states[idx1];      // amount encoder1 changed
  encoder1Pos -= delta1;              // inverse so CW -> +encoder CCW -> -encoder
  encoder2Pos -= delta1;              // change encoder 2 by same amount, since rack rotate around pinion when plate changes
  e1_old = e1_new;

  // --- Encoder 2 (A only, PD7) ---
  uint8_t a = (PIND & (1 << PIND7)) ? 0x02 : 0x00;
  uint8_t b = (PINB & (1 << PINB0)) ? 0x01 : 0x00;
  uint8_t e2_new = a | b;

  uint8_t idx2 = ((e2_old << 2) | e2_new) & 0x0F;
  encoder2Pos += enc_states[idx2];
  e2_old = e2_new;

  get_polar(encoder1Pos, encoder2Pos);
}

// For PB0 (pin 8) changes
ISR(PCINT0_vect) {
  uint8_t a = (PIND & (1 << PIND7)) ? 0x02 : 0x00;
  uint8_t b = (PINB & (1 << PINB0)) ? 0x01 : 0x00;
  uint8_t e2_new = a | b;

  uint8_t idx2 = ((e2_old << 2) | e2_new) & 0x0F;
  encoder2Pos += enc_states[idx2];
  e2_old = e2_new;

  get_polar(encoder1Pos, encoder2Pos);
}

const float degrees_per_tick = 1;   // ≈ 1 degree per tick
const float radius_per_tick = 78.87 / 275;  // ≈ 0.2868 mm per tick
const float mm_per_unit = 18.35;

volatile float average_CW_speed = 0;
volatile float average_CCW_speed = 0;
volatile float average_INC_speed = 0;
volatile float average_DEC_speed = 0;

// Message received: test calc speeds
// average clockwise speed (deg/s): 83.12
// average counter-clockwise speed (deg/s): 82.33
// average inc speed (mm/s): 25.42
// average dec speed (mm/s): 24.18

// --- Interrupt pin ---
const byte REED_PIN = 2;  // D2 on Arduino Nano (INT0)
volatile bool reedTriggered = false;
volatile bool ignoreReed = true;

void go_to_rack_end(bool forward = false, unsigned long maxtime = 5000);
void plate_tick(bool Clockwise = false, int degrees = 1, bool both = false);
void rack_tick(bool Decrease = false, int milli_m = 1);
void both_tick_sequential(bool both = false, int ticks = 1);
void both_tick_simultaneous(bool Clockwise = false, int ticks = 1);
void find_reed_initial(bool half = false);
float calc_linear_speed(bool increase = true);
float calc_angular_speed(bool clockwise = true);
void get_average_speeds(bool gohome = false);
void gotToPolarCoord(float degreesTarget, float radiusTarget, bool full=false);
void gotToRadius(float radiusTarget, bool full=false);

void setup() {
  pinMode(ENC_A, INPUT_PULLUP);
  pinMode(ENC_B, INPUT_PULLUP);

  pinMode(ENC_C, INPUT_PULLUP);
  pinMode(ENC_D, INPUT_PULLUP);

  // Encoder 1 → Port D (PCINT2_vect)
  PCICR  |= (1 << PCIE2);
  PCMSK2 |= (1 << PCINT20) | (1 << PCINT21); // pins 4,5
  // Encoder 2 → PCINT2 for PD7, PCINT0 for PB0
  PCMSK2 |= (1 << PCINT23); // PD7
  PCICR  |= (1 << PCIE0);   // PB0
  PCMSK0 |= (1 << PCINT0);

  // Initialize states
  e1_old = ((digitalRead(ENC_A) ? 0x02 : 0) | (digitalRead(ENC_B) ? 0x01 : 0));
  e2_old = ((digitalRead(ENC_C) ? 0x02 : 0) | (digitalRead(ENC_D) ? 0x01 : 0));

  lcd.init();
  lcd.backlight();
  Serial.begin(9600);
  Serial.println("READY");

  motorServo.attach(SERVO_PIN);
  motorServo2.attach(SERVO_PIN2);
  motorServo.writeMicroseconds(STOP_US);
  motorServo2.writeMicroseconds(STOP_US);

  pinMode(REED_PIN, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(REED_PIN), reedChange, CHANGE);
  delay(200);
  zero_RE_and_polars();
  delay(200);
}

void loop() {
  if (Serial.available() > 0) {
    String received = Serial.readStringUntil('\n');  // read from Pi
    String msg = "Message received: " + String(received);
    Serial.println(msg);

    interpret_message(received);
  }
}

// Fetch tuple from PROGMEM by character
Tuple getTuple(char c) {
  Tuple t;
  int index = -1;

  if (c >= 'a' && c <= 'z') {
    index = c - 'a';                // a=0 … z=25
  } else if (c >= 'A' && c <= 'W') {
    index = 26 + (c - 'A');         // A=26 … W=48
  }

  if (index >= 0 && index < 49) {
    memcpy_P(&t, &mapping[index], sizeof(Tuple));
  } else {
    t = {0, 0}; // fallback if out of range
  }
  return t;
}

void zero_RE_and_polars() {
  encoder1Pos = 0;    // Plate
  encoder2Pos = 0;    // Rack
  globalDegrees = 0;
  globalRadius = 0;
}

void setREandPolars(int degrees, int radius) {
    // Set polar globals
    globalDegrees = degrees;
    globalRadius = radius;

    // Convert polar position into encoder ticks
    // ≈ 1 degree per tick
    encoder1Pos = degrees;  // plate
    // radius_per_tick = 78.87 / 275;  // ≈ 0.2868 mm per tick
    encoder2Pos = radius * (275/78.87);    // rack

}

void reedChange() {
  reedTriggered = (digitalRead(REED_PIN) == LOW);
  // if (!ignoreReed && reedTriggered) {
  if (false) {
    //Stop the motors as soon as the switch is triggered
    motorServo.writeMicroseconds(STOP_US);
    motorServo2.writeMicroseconds(STOP_US);
  }
}

void interpret_message(String message) {
  if (message == "go home") {
    go_home_sequence();
    Serial.println("Home Sequence Completed");
  }

  if (message.startsWith("plate CW")) {
    plate_tick(true, get_ticks_from_message(9, message));
  }

  if (message.startsWith("plate CCW")) {
    plate_tick(false, get_ticks_from_message(10, message));
  }

  if (message.startsWith("rack inc")) {
    rack_tick(false, get_ticks_from_message(9, message) * radius_per_tick);
  }

  if (message.startsWith("rack dec")) {
    rack_tick(true, get_ticks_from_message(9, message) * radius_per_tick);
  }

  if (message.startsWith("both CCW se")) {
    both_tick_sequential(false, get_ticks_from_message(11, message));
  }

  if (message.startsWith("both CW se")) {
    both_tick_sequential(true, get_ticks_from_message(10, message));
  }

  if (message.startsWith("both CCW s")){
    both_tick_simultaneous(false, get_ticks_from_message(10, message));
  }

  if (message.startsWith("both CW s")) {
    both_tick_simultaneous(true, get_ticks_from_message(9, message));
  }

  if (message == "rack end") {
    go_to_rack_end();
  }

  if (message == "print encoders"){
    Serial.print("Enc1: ");
    Serial.print(encoder1Pos);
    Serial.print("  Enc2: ");
    Serial.println(encoder2Pos);
  }

  if (message == "print polar"){
    Serial.println(globalRadius);
    Serial.println(globalDegrees);
  }

  if (message == "zeros"){
    zero_RE_and_polars();
  }

  // Example: goto 90 150
  if (message.startsWith("goto")){
    int degrees; float radius;
    if (parseGotoCommand(message, radius, degrees)) {
        Serial.print("Radius = "); Serial.println(radius);
        Serial.print("Degrees = "); Serial.println(degrees);
        gotToPolarCoord(degrees, radius);
    } else {
        Serial.println("Invalid goto command!");
    }
  }

  if (message == "test direction") {
      Serial.println("Enter startTheta:");
      while (!Serial.available());  // wait for input
      double startTheta = Serial.parseFloat();
      Serial.println(startTheta);

      Serial.println("Enter endTheta:");
      while (!Serial.available());  // wait for input
      double endTheta = Serial.parseFloat();
      Serial.println(endTheta);

      if (shortestAngularDirection(startTheta, endTheta)){
        Serial.println("Clockwise");
      }
      else{
        Serial.println("Counter-Clockwise");
      }
  }

  if (message == "test sequence"){
    doCartMove('a', 'g');
    doCartMove('g', 'W');
    doCartMove('W', 'Q');
    doCartMove('Q', 'a');
    doCartMove('a', 'W');
    doCartMove('W', 'g');
    doCartMove('g', 'Q');
    doCartMove('Q', 'a');
  }

  if (message.startsWith("test cart")) {

    String letters = message.substring(9); 
    letters.trim();
    if (letters.length() != 2){
      return;
    }
    char first = letters.charAt(0);
    char second = letters.charAt(1);
    if (!isAlpha(first) || !isAlpha(second)) {
      return;
    }
    if (first == second){
      return;
    }

    doCartMove(first, second);

  }
}

void doCartMove(char first, char second){
    double x1, y1, x2, y2;

    Tuple t = getTuple(first);
    x1 = t.x;
    y1 = t.y;

    t = getTuple(second);
    x2 = t.x;
    y2 = t.y;

    bool vertical = false;
    bool throughCenter = false;

    if (x1 == x2) 
    {
      vertical = true;

      // Flip over y=x
      swapValues(x1, y1);
      swapValues(x2, y2);
      // Flip over y axis
      // swapValues(x1, x2);
      // swapValues(y1, y2);

      // Flip over y axis (negate x)
      x1 = -x1;
      x2 = -x2;
    }

    Polar polar1 = cartesian_to_polar(x1, y1);
    Polar polar2 = cartesian_to_polar(x2, y2);

    Serial.println(String(polar1.theta));
    Serial.println(String(polar1.r));
    Serial.println(String(polar2.theta));
    Serial.println(String(polar2.r));

    // return; //TODO: remove this

    float slope;
    if (!vertical) slope = (y2 - y1) / (x2 - x1); 
    else slope = 0;
    float b_value = y1 - slope * x1;

    if (abs(b_value) < 0.001 && (x1 == -x2 || y1 == -y2)){ // Small tolerance for floating b value, line also needs to pass through the center
      throughCenter = true;
      // Serial.println("Line through center (will need to stop in center and turn)");

      gotToPolarCoord(polar1.theta, polar1.r, false);
      gotToPolarCoord(polar2.theta, 0, false);
      gotToPolarCoord(polar2.theta, polar2.r, false);
      
      return;
    }

    bool Clockwise = shortestAngularDirection(polar1.theta, polar2.theta);
    Serial.println(String(Clockwise));

    if (Clockwise) {
        for (float deg = polar1.theta; angularDistance(deg, polar2.theta) > degrees_per_tick; deg -= 1) {
            float radius = calcRadiusFromTheta(deg, b_value, slope);
            // Serial.println(String(deg - 90));
            // Serial.println(String(radius));
            // Serial.println(" ");
            if (vertical) gotToPolarCoord(deg - 90, radius, false);
            else gotToPolarCoord(deg, radius, false);

        } 
    } else {
        for (float deg = polar1.theta; angularDistance(deg, polar2.theta) > degrees_per_tick; deg += 1) {
            float radius = calcRadiusFromTheta(deg, b_value, slope);
            // Serial.println(String(deg - 90));
            // Serial.println(String(radius));
            // Serial.println(" ");
            if (vertical) gotToPolarCoord(deg - 90, radius, false);
            else gotToPolarCoord(deg, radius, false);
        } 
    }
}


template<typename T>
void swapValues(T &a, T &b) {
  T temp = a;
  a = b;
  b = temp;
}

float calcRadiusFromTheta(float theta, float b, float m){
    float rad = theta * PI / 180.0;
    float denom = sin(rad) - m * cos(rad);
    if (abs(denom) < 1e-6) denom = 1e-6; // prevent division by zero
    return (b * mm_per_unit) / denom;
}

bool parseGotoCommand(String message, float &radius, int &degrees) {
    message.trim(); // remove any leading/trailing whitespace
    if (message.startsWith("goto ")) {
        message = message.substring(5); // remove "goto "
        int spaceIndex = message.indexOf(' ');
        if (spaceIndex == -1) return false;

        String rStr = message.substring(0, spaceIndex);
        String dStr = message.substring(spaceIndex + 1);

        radius = rStr.toFloat();
        degrees = dStr.toInt();

        return true;
    }
    return false;
}

int get_ticks_from_message(int len, String message){
    String numberPart = message.substring(len);  // length of the original message w/out the number
    int ticks = numberPart.toInt();  // Convert whole string to int
    return ticks;
}

void go_home_sequence() {
  go_to_rack_end();        // Find end of rack
  find_reed_initial(true); // Find the reed switch
  find_edge_of_reed();     // Orient around reed switch
  center_home();           // Go to center home. Polar: 0 deg<39.6mm (40)
  // get_average_speeds(true);
}

void find_reed_initial(bool half = false) {
  long releasePos = 0;
  const long minExitTicks = 100;

  // Step 1: ignore reed until we are OUTSIDE its active zone
  ignoreReed = true;

  // If reed is already triggered, move until it releases
  while (reedTriggered) {
    both_tick_sequential(false);  // Move CW
    reedTriggered = (digitalRead(REED_PIN) == LOW);

    if (serial_interrupt()) {
      motorServo.writeMicroseconds(STOP_US);
      motorServo2.writeMicroseconds(STOP_US);
      return;
    }
  }

  // Step 2: now reed is released → start caring about it
  ignoreReed = false;

  // EncoderValues e = read_encoders();
  // int pastPos = e.encoder1;
  int pastPos = globalDegrees;
  int currPos = pastPos;
  int ticks_not_triggered = 100;

  // Step 3: Move until the reed is not triggered, and have moved 100 degrees
  while (!(!reedTriggered && abs(pastPos - currPos) > ticks_not_triggered)) {
    // EncoderValues e = read_encoders();
    // currPos = e.encoder1;
    currPos = globalDegrees;
    motorServo.writeMicroseconds(PLATE_HALF_CW_US);
    motorServo2.writeMicroseconds(RACK_HALF_DEC_US);

    if (serial_interrupt()) {
      motorServo.writeMicroseconds(STOP_US);
      motorServo2.writeMicroseconds(STOP_US);
      return;
    }
  }

  // Step 4: keep moving until reed is triggered again
  while (true) {
    if (reedTriggered && !ignoreReed) {
      motorServo.writeMicroseconds(STOP_US);
      motorServo2.writeMicroseconds(STOP_US);
      break;
    }

    if (half) {
      motorServo.writeMicroseconds(PLATE_HALF_CW_US);
      motorServo2.writeMicroseconds(RACK_HALF_DEC_US);
    } else {
      motorServo.writeMicroseconds(PLATE_FULL_CW_US);
      motorServo2.writeMicroseconds(RACK_FULL_DEC_US);  // Decrease rack
    }

    if (serial_interrupt()) {
      motorServo.writeMicroseconds(STOP_US);
      motorServo2.writeMicroseconds(STOP_US);
      break;
    }
  }

  // Disarm after done so reed doesn’t interfere elsewhere
  ignoreReed = true;

}

void find_edge_of_reed(){
  bool success_on_inc = false;
  bool success_on_dec = false;
  bool edge_of_reed = false;
  unsigned long maxtime = 1000;
  unsigned long startTime;
  unsigned long endTime;

  // Step 4: Repeat Steps 5-7 till the reed is not triggered on the dec or inc
  while (!edge_of_reed){
    // Step 1: Increase arm till reed not triggered
    startTime = millis();
    endTime = startTime + maxtime;  // Maximum time for rack movement

    motorServo2.writeMicroseconds(RACK_HALF_INC_US);
    while (true){
      if (!reedTriggered){
        success_on_inc = true;
        break;
      }
      else{
        motorServo2.writeMicroseconds(RACK_HALF_INC_US);
      }
      if (millis() >= endTime){
        success_on_inc = false;
        break;
      }
      if (serial_interrupt()) {
        motorServo.writeMicroseconds(STOP_US);
        motorServo2.writeMicroseconds(STOP_US);
        return;
      }
    }
    motorServo2.writeMicroseconds(STOP_US);

    // Step 2: Move both CCW slightly
    both_tick_sequential(false, 1);

    // Step 3: Decrease arm till reed triggered
    startTime = millis();
    endTime = startTime + maxtime;  // Maximum time for rack movement

    motorServo2.writeMicroseconds(RACK_HALF_DEC_US);
    while (true){
      if (reedTriggered){
        success_on_inc = true;
        break;
      }
      if (millis() >= endTime){
        success_on_inc = false;
        break;
      }
      if (serial_interrupt()) {
        motorServo.writeMicroseconds(STOP_US);
        motorServo2.writeMicroseconds(STOP_US);
        return;
      }
    }
    motorServo2.writeMicroseconds(STOP_US);

    if (!success_on_inc && !success_on_dec){
      edge_of_reed = true;
    }

    if (serial_interrupt()) {
      motorServo.writeMicroseconds(STOP_US);
      motorServo2.writeMicroseconds(STOP_US);
      return;
    }
  }

  // Step 5: Inc rack significantly (so we know reed can't be triggered)
    rack_tick(false, 250 * radius_per_tick);

  // Step 6: Move both CW 
    both_tick_sequential(true, 10);

  // Step 7: Find where reed is first triggered
  ignoreReed = false;

  while (!reedTriggered){
    motorServo2.writeMicroseconds(RACK_HALF_DEC_US);
    if (serial_interrupt()) {
      motorServo.writeMicroseconds(STOP_US);
      motorServo2.writeMicroseconds(STOP_US);
      return;
    }
  }
  motorServo2.writeMicroseconds(STOP_US);

  // Disable reed
  ignoreReed = true;
}

void center_home(){
  // Used to go to polar: 0 deg<39.6mm (40)
  // Only call after calibrating with go_to_rack_end, find_reed_initial(true), and find_edge_of_reed

  zero_RE_and_polars();
  // Goto 22 < 100
  gotToPolarCoord(100, 22);
  setREandPolars(0, 39); // Set to 39 < 0
}

void both_tick_sequential(bool both = false, int ticks = 1) {
  plate_tick(both, ticks);
  rack_tick(both, ticks * 2 * radius_per_tick);
}

void both_tick_simultaneous(bool Clockwise = false, int ticks = 1){
  plate_tick(Clockwise, ticks, true);
}

void plate_tick(bool Clockwise = false, int degrees = 1, bool both = false) {
  int past_deg = globalDegrees;
  int curr_deg = past_deg;
  const int SLOWDOWN_THRESHOLD = 8;

  int fullSpeedUS = Clockwise ? PLATE_FULL_CW_US : PLATE_FULL_CCW_US;
  int halfSpeedUS = Clockwise ? PLATE_HALF_CW_US : PLATE_HALF_CCW_US;
  int fullSpeedUS2 = Clockwise ? RACK_FULL_DEC_US : RACK_FULL_INC_US;
  int halfSpeedUS2 = Clockwise ? RACK_HALF_DEC_US : RACK_HALF_INC_US;

  // Move until desired degrees reached
  // while (abs(curr_deg - past_deg) < degrees) {
  while (angularDistance(curr_deg, past_deg) < degrees) {
    int remaining = degrees - abs(curr_deg - past_deg);

    // Slow down when close to goal
    int directionUS1 = remaining <= SLOWDOWN_THRESHOLD ? halfSpeedUS : fullSpeedUS;
    int directionUS2 = remaining <= SLOWDOWN_THRESHOLD ? halfSpeedUS2 : fullSpeedUS2;
    
    motorServo.writeMicroseconds(directionUS1);
    if (both) motorServo2.writeMicroseconds(directionUS2);

    curr_deg = globalDegrees;

    if (serial_interrupt()) {
      motorServo.writeMicroseconds(STOP_US);
      if (both) motorServo2.writeMicroseconds(STOP_US);

      return;
    }
  }

  // Stop plate motor
  motorServo.writeMicroseconds(STOP_US);
  // Optionally stop pinion motor
  if (both) motorServo2.writeMicroseconds(STOP_US);
}

void rack_tick(bool Decrease = false, int milli_m = 1) {
  int past_Radius = globalRadius; // In mm
  int current_Radius = past_Radius;

  int fullSpeedUS = Decrease ? RACK_FULL_DEC_US : RACK_FULL_INC_US;
  int halfSpeedUS = Decrease ? RACK_HALF_DEC_US : RACK_HALF_INC_US;

  // Move until desired milli_m reached
  while (abs(current_Radius - past_Radius) < milli_m) {
    int remaining = milli_m - abs(current_Radius - past_Radius);

    // Slow down when close to goal
    int directionUS = remaining <= 8 ? halfSpeedUS : fullSpeedUS;
    motorServo2.writeMicroseconds(directionUS);

    current_Radius = globalRadius;

    if (serial_interrupt()) {
      motorServo2.writeMicroseconds(STOP_US);
      return;
    }
  }

  // Stop pinion motor
  motorServo2.writeMicroseconds(STOP_US);
}

void go_to_rack_end(bool forward = false, unsigned long maxtime = 5000) {
  unsigned long startTime = millis();
  unsigned long endTime = startTime + maxtime;  // Maximum time for rack movement

  // Move arm to the end of the rack
  while (millis() < endTime) {
    // Check 'forward' and move accordingly
    motorServo2.writeMicroseconds(forward ? RACK_FULL_DEC_US : RACK_FULL_INC_US);

    // Interrupt-like check for serial input
    if (serial_interrupt()) {
      motorServo2.writeMicroseconds(STOP_US);
      return;  // Exit entire function if needed
    }
  }

  int past_Radius = globalRadius;
  int current_Radius = past_Radius;

  if (!forward) {
    //Move arm in slightly
    while (abs(current_Radius - past_Radius) < 100 * radius_per_tick) { // In mm
      motorServo2.writeMicroseconds(RACK_HALF_DEC_US);  // Pinion motor
      current_Radius = globalRadius;

      if (serial_interrupt()) {
        motorServo.writeMicroseconds(STOP_US);
        motorServo2.writeMicroseconds(STOP_US);
        return;
      }
    }
  }

  else {
    //Move arm out slightly
    while (abs(current_Radius - past_Radius) < 100 * radius_per_tick) { // In mm
      motorServo2.writeMicroseconds(RACK_HALF_INC_US);  // Pinion motor
      current_Radius = globalRadius;

      if (serial_interrupt()) {
        motorServo.writeMicroseconds(STOP_US);
        motorServo2.writeMicroseconds(STOP_US);
        return;
      }
    }
  }


  // Stop pinion motor
  motorServo2.writeMicroseconds(STOP_US);
}

void get_polar(int encoder1, int encoder2) {
  // degrees_per_tick = 1;   // ≈ 1 degree per tick
  globalDegrees = - degrees_per_tick * float(encoder1);  // Negative -> flips so CCW is pos and CW is neg, reverse of homing logic
  while (true){
    if (globalDegrees >= 360) {
      globalDegrees -= 360;
    }
    else if (globalDegrees < 0){
      globalDegrees += 360;
    }
    else {
      break;
    }

    if (serial_interrupt()) {
      motorServo.writeMicroseconds(STOP_US);
      motorServo2.writeMicroseconds(STOP_US);
      return;
    }
  }

  // radius_per_tick = 78.87 / 275;  // ≈ 0.2868 mm per tick
  // Range of encoder2 should be 0-275
  globalRadius = (radius_per_tick * float(encoder2));
}

// TODO: Reverse degrees and radius to be in standard polar format
void gotToRadius(float radiusTarget, bool full=false){
  
  int fullSpeedUS = radiusTarget < globalRadius ? RACK_FULL_DEC_US : RACK_FULL_INC_US;
  int halfSpeedUS = radiusTarget < globalRadius ? RACK_HALF_DEC_US : RACK_HALF_INC_US;
  int directionUS;

  // Do rack first (radiusTarget)
  while(abs(radiusTarget - globalRadius) > radius_per_tick){ // ≈ radius_per_tick = 0.2868 mm
    int remaining = abs(radiusTarget - globalRadius);

    // Slow down when close to goal
    if (!full) directionUS = remaining <= 8 ? halfSpeedUS : fullSpeedUS;
    else directionUS = fullSpeedUS;
    motorServo2.writeMicroseconds(directionUS);

    if (serial_interrupt()) {
      motorServo2.writeMicroseconds(STOP_US);
      return;
    }
  }

  motorServo2.writeMicroseconds(STOP_US);
}

void gotToPolarCoord(float degreesTarget, float radiusTarget, bool full=false){

  // Serial.print("Theta: "); Serial.println(String(degreesTarget));
  // Serial.print("R: "); Serial.println(String(radiusTarget));
  // Serial.println(" ");

  //TODO: REMOVE THIS RETURN
  // return;

  gotToRadius(radiusTarget, full);

  bool Clockwise = shortestAngularDirection(globalDegrees, degreesTarget);
  // Serial.println("Result:" + String(Clockwise));
  int fullSpeedUS = Clockwise ? PLATE_FULL_CW_US : PLATE_FULL_CCW_US;
  int halfSpeedUS = Clockwise ? PLATE_HALF_CW_US : PLATE_HALF_CCW_US;
  int directionUS;

  // Do plate second (degreesTarget), but move rack at same speed/direction
    while(angularDistance(globalDegrees, degreesTarget) > degrees_per_tick){ // ≈ degrees_per_tick = 0.2868 mm
      int remaining = abs(degreesTarget - globalDegrees);

      // Serial.println("degreesTarget:" + String(degreesTarget));    // Caution: These print statements will cause the loop to be slow and inadvertently miss steps
      // Serial.println("globalDegrees:" + String(globalDegrees));
      // Serial.println("remaining:" + String(remaining));

      // Slow down when close to goal
      if (!full) directionUS = remaining <= 8 ? halfSpeedUS : fullSpeedUS;
      else directionUS = fullSpeedUS;
      motorServo.writeMicroseconds(directionUS);
      motorServo2.writeMicroseconds(directionUS);

      if (serial_interrupt()) {
        motorServo.writeMicroseconds(STOP_US);
        motorServo2.writeMicroseconds(STOP_US);
        return;
      }
  }
  
  motorServo.writeMicroseconds(STOP_US);
  motorServo2.writeMicroseconds(STOP_US);
  
}

float angularDistance(float a, float b) {
  // Returns the shortest angular distance from one theta to another
  float diff = fmod((b - a + 540.0), 360.0) - 180.0; 
  return fabs(diff);
}

bool shortestAngularDirection(double startTheta, double endTheta) {
    // Clockwise -> returns true
    // Counter-Clockwise -> returns false

    // normalize to [0,360)
    double t1 = fmod(startTheta, 360.0); if (t1 < 0) t1 += 360.0;
    double t2 = fmod(endTheta, 360.0); if (t2 < 0) t2 += 360.0;

    // signed difference t2 - t1
    double delta = t2 - t1;

    // normalize delta into (-180, 180]
    while (delta <= -180.0) delta += 360.0;
    while (delta > 180.0)  delta -= 360.0;

    if (fabs(delta) < degrees_per_tick){
        // Serial.println("same " + String(0.0));
        return true;
    }

    // tie at ±180°: pick a policy (here I pick clockwise for tie)
    if (fabs(fabs(delta) - 180.0) < degrees_per_tick){
        // Serial.println("clockwise " + String(180.0));
        return true;
    }

    if (delta > 0){
      // Serial.println("counter-clockwise " + String(delta)); // positive => CCW by delta
      return false;
    }
    else{
      // Serial.println("clockwise " + String(-delta)); // negative => CW by -delta
      return true;
    }
}

Polar cartesian_to_polar(double x_init, double y_init) {
  Polar polar;
  polar.r = sqrt(x_init * x_init + y_init * y_init) * mm_per_unit;
  polar.theta = atan2(y_init, x_init) * 180.0 / PI; // convert radians to degrees
  return polar;
}

bool serial_interrupt() {
  // "Interrupt-like" check for new data
  if (Serial.available() > 0) {
    Serial.println("Breaking out: new serial data detected");
    motorServo.writeMicroseconds(STOP_US);
    motorServo2.writeMicroseconds(STOP_US);
    return true;
  } else {
    return false;
  }
}