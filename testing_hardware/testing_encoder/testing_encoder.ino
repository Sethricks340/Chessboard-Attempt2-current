#define ENC_A 3  // Example pin numbers
#define ENC_B 5

volatile long encoderPos = 0;  // Encoder position counter

// Interrupt Service Routine for low-resolution
void encoderISR() {
  // Direction depends on state of B when A rises
  if (digitalRead(ENC_B) == HIGH) {
    encoderPos++;
  } else {
    encoderPos--;
  }
}

void setup() {
  pinMode(ENC_A, INPUT_PULLUP);
  pinMode(ENC_B, INPUT_PULLUP);

  // Attach interrupt only to Channel A, rising edge
  attachInterrupt(digitalPinToInterrupt(ENC_A), encoderISR, RISING);

  Serial.begin(9600);
}

void loop() {
  Serial.println(encoderPos);
  delay(100);
}
