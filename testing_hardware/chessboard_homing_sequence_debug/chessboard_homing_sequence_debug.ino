#include <Servo.h>
#include <FastLED.h>
#include <OneButton.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// Set the LCD address to 0x27 for a 16 chars and 2 lines display
LiquidCrystal_I2C lcd(0x27, 16, 2);

#define LED_PIN 3
#define NUM_LEDS 10
#define BUTTON_PIN A2
#define BRIGHTNESS 100

// Define rotary encoder pins (can be any digital pins)
#define ENC_A 4
#define ENC_B 5

#define ENC_C 7
#define ENC_D 8

unsigned long _lastIncReadTime = micros();
unsigned long _lastDecReadTime = micros();
int _pauseLength = 25000;
int _fastIncrement = 10;

volatile int last_RE_tick = 0;

CRGB leds[NUM_LEDS];
Servo motorServo;
Servo motorServo2;

bool halfSpeedMode = false;
bool goHome = false;
int MODE = 0;

OneButton button(BUTTON_PIN, true, true);  // active low, internal pullup

const int SERVO_PIN = 6;
const int SERVO_PIN2 = 9;

const int STOP_US = 1500;
const int FULL_FORWARD_US = 2000;
const int FULL_REVERSE_US = 1000;
const int HALF_FORWARD_US = 1600;
const int HALF_REVERSE_US = 1400;

const int JOY_X_PIN = A0;
const int JOY_Y_PIN = A1;
const int DEADZONE = 100;

// --- Interrupt pin ---
const byte REED_PIN = 2;  // D2 on Arduino Nano (INT0)
volatile bool reedTriggered = false;

// Debounce variables
volatile unsigned long lastReedInterrupt = 0;
const unsigned long debounceDelay = 100;  // milliseconds

unsigned long modeStartTime = 0;
const unsigned long homeDelay = 3000;  // 3 seconds

unsigned long reedTriggeredStartTime = 0;

// Home state machine
enum HomeState {
  HOME_WAIT_DELAY,
  HOME_MOVE_REVERSE,
  HOME_BACK_OFF,
  HOME_WAIT_REED,
  HOME_DONE
};

HomeState homeState = HOME_WAIT_DELAY;
unsigned long homeStepStartTime = 0;

// Second encoder globals
static uint8_t old_CD = 3;          // Lookup table index for encoder 2
static int8_t encval_2 = 0;         // Encoder value for encoder 2
volatile int _RE_tick2 = 0;          // Separate last_RE_tick for encoder 2
unsigned long _lastIncReadTime_2 = 0;
unsigned long _lastDecReadTime_2 = 0;

void updateLEDsForMode() {
  if (MODE == 0) {
    fill_solid(leds, NUM_LEDS, CRGB::Green);
  } else if (MODE == 1) {
    fill_solid(leds, NUM_LEDS, CRGB::Red);
  } else {
    fill_solid(leds, NUM_LEDS, CRGB::Blue);
  }
  FastLED.show();
}

void toggleSpeed() {
  if (!MODE) {
    fill_solid(leds, NUM_LEDS, CRGB::Red);
    halfSpeedMode = !halfSpeedMode;
    goHome = false;
    MODE++;
  } 
  else if (MODE == 1){
    fill_solid(leds, NUM_LEDS, CRGB::Blue);
    goHome = true;
    MODE++;
    modeStartTime = millis();
    homeState = HOME_WAIT_DELAY;  // Reset state machine
  } 
  else {
    goHome = false;
    fill_solid(leds, NUM_LEDS, CRGB::Green);
    halfSpeedMode = !halfSpeedMode;
    MODE = 0;
  }

  FastLED.show();
}

void setup() {
  pinMode(ENC_A, INPUT_PULLUP);
  pinMode(ENC_B, INPUT_PULLUP);

  pinMode(ENC_C, INPUT_PULLUP);
  pinMode(ENC_D, INPUT_PULLUP);

  Serial.begin(9600);

  lcd.init();          // initialize the lcd
  lcd.backlight();     // turn on the backlight

  motorServo.attach(SERVO_PIN);
  motorServo2.attach(SERVO_PIN2);
  motorServo.writeMicroseconds(STOP_US);
  motorServo2.writeMicroseconds(STOP_US);

  pinMode(JOY_X_PIN, INPUT);
  pinMode(JOY_Y_PIN, INPUT);

  FastLED.addLeds<WS2812B, LED_PIN, GRB>(leds, NUM_LEDS);
  FastLED.setBrightness(BRIGHTNESS);
  FastLED.clear();
  FastLED.show();

  button.attachClick(toggleSpeed);

  pinMode(REED_PIN, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(REED_PIN), reedChange, CHANGE);

  fill_solid(leds, NUM_LEDS, CRGB::Green);
  FastLED.show();
  delay(2000);
}

void loop() {
  read_encoder();
  read_encoder_2();

  button.tick();

  if (!goHome){
    // int joyX = analogRead(JOY_X_PIN);
    // int joyY = analogRead(JOY_Y_PIN);

    // if (joyX > 512 + DEADZONE) {
    //   motorServo.writeMicroseconds(halfSpeedMode ? HALF_FORWARD_US : FULL_FORWARD_US);
    // } else if (joyX < 512 - DEADZONE) {
    //   motorServo.writeMicroseconds(halfSpeedMode ? HALF_REVERSE_US : FULL_REVERSE_US);
    // } else {
    //   motorServo.writeMicroseconds(STOP_US);
    // }

    // if (joyY > 512 + DEADZONE) {
    //   motorServo2.writeMicroseconds(halfSpeedMode ? HALF_REVERSE_US : FULL_REVERSE_US);
    // } else if (joyY < 512 - DEADZONE) {
    //   motorServo2.writeMicroseconds(halfSpeedMode ? HALF_FORWARD_US : FULL_FORWARD_US);
    // } else {
    //   motorServo2.writeMicroseconds(STOP_US);
    // }
    move_encoder_to(1, 10);
  }
  else {
    // Non-blocking goHome state machine
    switch (homeState) {
      case HOME_WAIT_DELAY:
        if (millis() - modeStartTime >= homeDelay) {
          fill_solid(leds, NUM_LEDS, CRGB::Purple);
          FastLED.show();

          motorServo2.writeMicroseconds(HALF_REVERSE_US);
          homeStepStartTime = millis();
          homeState = HOME_MOVE_REVERSE;
        }
        break;

      case HOME_MOVE_REVERSE:
        if (millis() - homeStepStartTime >= 10000) {
          motorServo2.writeMicroseconds(HALF_FORWARD_US); // back off
          homeStepStartTime = millis();
          homeState = HOME_BACK_OFF;
        }
        break;

      case HOME_BACK_OFF:
        if (millis() - homeStepStartTime >= 500) {
          motorServo2.writeMicroseconds(STOP_US);
          reedTriggeredStartTime = millis();
          homeState = HOME_WAIT_REED;
        }
        break;

      case HOME_WAIT_REED:
        motorServo.writeMicroseconds(FULL_REVERSE_US);
        motorServo2.writeMicroseconds(FULL_REVERSE_US);

        if (reedTriggered || (millis() - reedTriggeredStartTime >= 10000)) {
          homeState = HOME_DONE;
        }
        break;

      case HOME_DONE:
        goHome = false;
        halfSpeedMode = false;  // full speed mode
        MODE = 0;               // green mode

        updateLEDsForMode();

        motorServo.writeMicroseconds(STOP_US);
        motorServo2.writeMicroseconds(STOP_US);

        homeState = HOME_WAIT_DELAY;  // reset for next time
        break;
    }
  }
}

void reedChange() {
  unsigned long now = millis();
  if (now - lastReedInterrupt > debounceDelay) {
    bool state = digitalRead(REED_PIN);
    reedTriggered = (state == LOW);
    lastReedInterrupt = now;
    if (reedTriggered) {
      Serial.print("Reed switch triggered! ");
    } else {
      Serial.print("Reed switch released! ");
    }
    Serial.println(now);
  }
}

void read_encoder() {
  static uint8_t old_AB = 3;  // Lookup table index
  static int8_t encval = 0;   // Encoder value
  static const int8_t enc_states[] = {
    0, -1, 1, 0,
    1, 0, 0, -1,
    -1, 0, 0, 1,
    0, 1, -1, 0
  };

  old_AB <<= 2;

  if (digitalRead(ENC_A)) old_AB |= 0x02;
  if (digitalRead(ENC_B)) old_AB |= 0x01;

  encval += enc_states[(old_AB & 0x0f)];

  if (encval > 3) {
    int changevalue = 1;
    if ((micros() - _lastIncReadTime) < _pauseLength) {
      changevalue *= _fastIncrement;
    }
    _lastIncReadTime = micros();
    last_RE_tick += changevalue;
    encval = 0;
  }
  else if (encval < -3) {
    int changevalue = -1;
    if ((micros() - _lastDecReadTime) < _pauseLength) {
      changevalue *= _fastIncrement;
    }
    _lastDecReadTime = micros();
    last_RE_tick += changevalue;
    encval = 0;
  }

  static int lastlast_RE_tick = 0;

  if (last_RE_tick != lastlast_RE_tick) {
    Serial.print("Encoder 1: ");
    Serial.println(last_RE_tick);
    print_LCD(last_RE_tick, _RE_tick2);
    lastlast_RE_tick = last_RE_tick;
  }
}

void read_encoder_2() {
  static const int8_t enc_states[] = {
    0, -1, 1, 0,
    1, 0, 0, -1,
    -1, 0, 0, 1,
    0, 1, -1, 0
  };

  old_CD <<= 2;

  if (digitalRead(ENC_C)) old_CD |= 0x02;
  if (digitalRead(ENC_D)) old_CD |= 0x01;

  encval_2 += enc_states[(old_CD & 0x0f)];

  if (encval_2 > 3) {
    int changevalue = 1;
    if ((micros() - _lastIncReadTime_2) < _pauseLength) {
      changevalue *= _fastIncrement;
    }
    _lastIncReadTime_2 = micros();
    _RE_tick2 += changevalue;
    encval_2 = 0;
  }
  else if (encval_2 < -3) {
    int changevalue = -1;
    if ((micros() - _lastDecReadTime_2) < _pauseLength) {
      changevalue *= _fastIncrement;
    }
    _lastDecReadTime_2 = micros();
    _RE_tick2 += changevalue;
    encval_2 = 0;
  }

  static int last_RE_tick2 = 0;

  if (_RE_tick2 != last_RE_tick2) {
    Serial.print("Encoder 2: ");
    Serial.println(_RE_tick2);
    print_LCD(last_RE_tick, _RE_tick2);
    last_RE_tick2 = _RE_tick2;
  }
}

void print_LCD(int last_RE_tick, int _RE_tick2) {
  lcd.clear();
  lcd.setCursor(0, 0);              // First line, first column
  lcd.print("Plate: ");
  lcd.print(last_RE_tick);

  lcd.setCursor(0, 1);              // Second line, first column
  lcd.print("Arm: ");
  lcd.print(_RE_tick2);
}

void move_encoder_to(int encoder, int tick){
  // while the current tick is not equal to the desired tick, move towards the desired tick
  read_encoder();
  read_encoder_2();
  while (last_RE_tick != tick){
    Serial.println(tick);
    Serial.println(last_RE_tick);
    // motorServo.writeMicroseconds(HALF_REVERSE_US);
    motorServo.writeMicroseconds(FULL_REVERSE_US);
    print_LCD(last_RE_tick, _RE_tick2);
    read_encoder();
    read_encoder_2();
  }
  motorServo.writeMicroseconds(STOP_US);
}