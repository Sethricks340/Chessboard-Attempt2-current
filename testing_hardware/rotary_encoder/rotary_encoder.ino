#define ENC1_A 4
#define ENC1_B 5
#define ENC2_A 7  // PD7
#define ENC2_B 8  // PB0

volatile long encoder1Pos = 0;
volatile long encoder2Pos = 0;

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
  encoder1Pos += enc_states[idx1];
  e1_old = e1_new;

  // --- Encoder 2 (A only, PD7) ---
  uint8_t a = (PIND & (1 << PIND7)) ? 0x02 : 0x00;
  uint8_t b = (PINB & (1 << PINB0)) ? 0x01 : 0x00;
  uint8_t e2_new = a | b;

  uint8_t idx2 = ((e2_old << 2) | e2_new) & 0x0F;
  encoder2Pos += enc_states[idx2];
  e2_old = e2_new;
}

// For PB0 (pin 8) changes
ISR(PCINT0_vect) {
  uint8_t a = (PIND & (1 << PIND7)) ? 0x02 : 0x00;
  uint8_t b = (PINB & (1 << PINB0)) ? 0x01 : 0x00;
  uint8_t e2_new = a | b;

  uint8_t idx2 = ((e2_old << 2) | e2_new) & 0x0F;
  encoder2Pos += enc_states[idx2];
  e2_old = e2_new;
}

void setup() {
  pinMode(ENC1_A, INPUT_PULLUP);
  pinMode(ENC1_B, INPUT_PULLUP);
  pinMode(ENC2_A, INPUT_PULLUP);
  pinMode(ENC2_B, INPUT_PULLUP);

  // Encoder 1 → Port D (PCINT2_vect)
  PCICR  |= (1 << PCIE2);
  PCMSK2 |= (1 << PCINT20) | (1 << PCINT21); // pins 4,5
  // Encoder 2 → PCINT2 for PD7, PCINT0 for PB0
  PCMSK2 |= (1 << PCINT23); // PD7
  PCICR  |= (1 << PCIE0);   // PB0
  PCMSK0 |= (1 << PCINT0);

  // Initialize states
  e1_old = ((digitalRead(ENC1_A) ? 0x02 : 0) | (digitalRead(ENC1_B) ? 0x01 : 0));
  e2_old = ((digitalRead(ENC2_A) ? 0x02 : 0) | (digitalRead(ENC2_B) ? 0x01 : 0));

  Serial.begin(9600);
}

void loop() {
  static long last1 = 0, last2 = 0;
  long p1, p2;
 
  noInterrupts();
  p1 = encoder1Pos;
  p2 = encoder2Pos;
  interrupts();

  if (p1 != last1 || p2 != last2) {
    Serial.print("Enc1: ");
    Serial.print(p1);
    Serial.print("  Enc2: ");
    Serial.println(p2);
    last1 = p1;
    last2 = p2;
  }
}
