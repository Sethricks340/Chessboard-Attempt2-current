/*
Known Issues:

W/ the current wire setup, they keep getting in the way of the home sequence. Need to be cleaned up and put down.

The rack pops out vertically sometimes when it is at the end and hitting the spring.

Movements are off by just a few degrees. This adds up over time.

"Breaking out: new serial data detected" prints a million times when breaking out, and sometimes doesn't break out

Electromagnet wires potentially could get tangled up and stressed/broken with current arrangment

TODO: 

Screw electromagnet onto holder

try to understand ISRs that chat wrote 

convert polar to cartesian 

figure out how to keep the rack from popping out 

*/

#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <Servo.h>

Servo motorServo;   // Plate
Servo motorServo2;  // Pinion
const int SERVO_PIN = 12; // Plate
const int SERVO_PIN2 = 11; //Pinion
const int STOP_US = 1500;

const int PLATE_FULL_CW_US = 2000;
const int PLATE_FULL_CCW_US = 1000;
const int PLATE_HALF_CW_US = 1600;
const int PLATE_HALF_CCW_US = 1400;

const int RACK_FULL_DEC_US = 2000;
const int RACK_FULL_INC_US = 1000;
const int RACK_HALF_DEC_US = 1600;
const int RACK_HALF_INC_US = 1400;

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
  // Serial.print("Radius: "); Serial.println(globalRadius);
  // Serial.print("Degrees: "); Serial.println(globalDegrees);
}

void zero_RE_and_polars() {
  encoder1Pos = 0;    // Plate
  encoder2Pos = 0;    // Rack
  globalDegrees = 0;
  globalRadius = 0;
}

void reedChange() {
  reedTriggered = (digitalRead(REED_PIN) == LOW);
  if (!ignoreReed && reedTriggered) {
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

  if (message == "zeros"){
    zero_RE_and_polars();
  }

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
  unsigned long maxtime = 1500;
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
  rack_tick(true, 70 * radius_per_tick); // Move rack in 70 ticks (electromagnet on center)
  both_tick_simultaneous(false, 10); // Arm is at around 90 degrees
  both_tick_simultaneous(false, 90); // Arm is at around 0 degrees, still centered
  zero_RE_and_polars();
  rack_tick(false, 138 * radius_per_tick); // increase rack by half, so rack is centered on plate
}

void both_tick_sequential(bool both = false, int ticks = 1) {
  plate_tick(both, ticks);
  rack_tick(both, ticks * radius_per_tick);
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
  while (abs(curr_deg - past_deg) < degrees) {
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
  globalDegrees = degrees_per_tick * float(encoder1);
  while (true){
    if (globalDegrees >= 360) {
      globalDegrees -= 360;
    }
    else if (globalDegrees <= -360){
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