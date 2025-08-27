import serial
from pynput import keyboard
import threading
import time

# Replace with your Arduino's serial port
arduino = serial.Serial('COM3', 9600)  # Adjust COM port as needed

# Wait for Arduino to initialize and flush any startup data
time.sleep(2)
arduino.flushInput()
arduino.flushOutput()

def read_serial():
    """Function to continuously read from Arduino and print to terminal"""
    while True:
        try:
            if arduino.in_waiting > 0:
                data = arduino.readline().decode('utf-8').strip()
                if data:  # Only print non-empty lines
                    print(f"Arduino: {data}")
        except Exception as e:
            print(f"Serial read error: {e}")
            break
        time.sleep(0.01)  # Small delay to prevent excessive CPU usage

# Start the serial reading thread
serial_thread = threading.Thread(target=read_serial, daemon=True)
serial_thread.start()

def on_press(key):
    try:
        if key == keyboard.Key.left:
            arduino.write(b'l')  # Left pressed
        elif key == keyboard.Key.right:
            arduino.write(b'r')  # Right pressed
        elif key == keyboard.Key.up:
            arduino.write(b'w')  # Up pressed
        elif key == keyboard.Key.down:
            arduino.write(b's')  # Down pressed
    except AttributeError:
        pass

def on_release(key):
    try:
        if key == keyboard.Key.left:
            arduino.write(b'L')  # Left released
        elif key == keyboard.Key.right:
            arduino.write(b'R')  # Right released
        elif key == keyboard.Key.up:
            arduino.write(b'W')  # Up released
        elif key == keyboard.Key.down:
            arduino.write(b'S')  # Down released
    except AttributeError:
        pass

    if key == keyboard.Key.esc:
        print("Exiting...")
        arduino.close()  # Close serial connection before exiting
        return False

print("Arduino controller started. Use arrow keys to control, ESC to exit.")
print("Serial output from Arduino will be displayed below:")
print("-" * 50)

with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()





# #include <Servo.h>
# #include <EnableInterrupt.h>

# // --- Servo setup ---
# Servo motorServo;
# Servo motorServo2;
# const int SERVO_PIN = 6;
# const int SERVO_PIN2 = 9;

# // Define neutral stop signal for continuous servos
# const int STOP_US = 1500;
# const int FORWARD_US = 2000;
# const int REVERSE_US = 1000;

# // --- Encoder variables ---
# volatile int counter1 = 0;
# volatile int counter2 = 0;

# unsigned long _lastIncReadTime1 = 0;
# unsigned long _lastDecReadTime1 = 0;
# unsigned long _lastIncReadTime2 = 0;
# unsigned long _lastDecReadTime2 = 0;

# int _pauseLength = 25000;
# int _fastIncrement = 10;

# // Encoder 1 pins
# #define ENC1_A 2
# #define ENC1_B 3

# // Encoder 2 pins
# #define ENC2_A 4
# #define ENC2_B 5

# void setup() {
#   Serial.begin(9600);

#   // Attach servos
#   motorServo.attach(SERVO_PIN);
#   motorServo2.attach(SERVO_PIN2);
#   motorServo.writeMicroseconds(STOP_US);
#   motorServo2.writeMicroseconds(STOP_US);

#   // Setup encoder pins
#   pinMode(ENC1_A, INPUT_PULLUP);
#   pinMode(ENC1_B, INPUT_PULLUP);
#   pinMode(ENC2_A, INPUT_PULLUP);
#   pinMode(ENC2_B, INPUT_PULLUP);

#   // EnableInterrupt library used for ALL encoder pins
#   enableInterrupt(ENC1_A, read_encoder1, CHANGE);
#   enableInterrupt(ENC1_B, read_encoder1, CHANGE);
#   enableInterrupt(ENC2_A, read_encoder2, CHANGE);
#   enableInterrupt(ENC2_B, read_encoder2, CHANGE);
# }

# void loop() {
#   // Servo control from serial
#   if (Serial.available()) {
#     char c = Serial.read();

#     switch (c) {
#       // Motor 1 control
#       case 'l': motorServo.writeMicroseconds(REVERSE_US); break;
#       case 'r': motorServo.writeMicroseconds(FORWARD_US); break;
#       case 'L': motorServo.writeMicroseconds(STOP_US); break;
#       case 'R': motorServo.writeMicroseconds(STOP_US); break;

#       // Motor 2 control
#       case 'w': motorServo2.writeMicroseconds(REVERSE_US); break;
#       case 's': motorServo2.writeMicroseconds(FORWARD_US); break;
#       case 'W': motorServo2.writeMicroseconds(STOP_US); break;
#       case 'S': motorServo2.writeMicroseconds(STOP_US); break;
#     }
#   }

#   // Encoder counters printing
#   static int lastCounter1 = 0;
#   static int lastCounter2 = 0;

#   if (counter1 != lastCounter1) {
#     Serial.print("Encoder 1: ");
#     Serial.println(counter1);
#     lastCounter1 = counter1;
#   }

#   if (counter2 != lastCounter2) {
#     Serial.print("Encoder 2: ");
#     Serial.println(counter2);
#     lastCounter2 = counter2;
#   }
# }

# // === Encoder 1 ISR ===
# void read_encoder1() {
#   static uint8_t old_AB1 = 3;
#   static int8_t encval1 = 0;

#   static const int8_t enc_states[] = {
#      0, -1,  1,  0,
#      1,  0,  0, -1,
#     -1,  0,  0,  1,
#      0,  1, -1,  0
#   };

#   old_AB1 <<= 2;
#   if (digitalRead(ENC1_A)) old_AB1 |= 0x02;
#   if (digitalRead(ENC1_B)) old_AB1 |= 0x01;

#   encval1 += enc_states[old_AB1 & 0x0F];

#   if (encval1 > 3) {
#     int changevalue = 1;
#     if ((micros() - _lastIncReadTime1) < _pauseLength) {
#       changevalue *= _fastIncrement;
#     }
#     _lastIncReadTime1 = micros();
#     counter1 += changevalue;
#     encval1 = 0;
#   } else if (encval1 < -3) {
#     int changevalue = -1;
#     if ((micros() - _lastDecReadTime1) < _pauseLength) {
#       changevalue *= _fastIncrement;
#     }
#     _lastDecReadTime1 = micros();
#     counter1 += changevalue;
#     encval1 = 0;
#   }
# }

# // === Encoder 2 ISR ===
# void read_encoder2() {
#   static uint8_t old_AB2 = 3;
#   static int8_t encval2 = 0;

#   static const int8_t enc_states[] = {
#      0, -1,  1,  0,
#      1,  0,  0, -1,
#     -1,  0,  0,  1,
#      0,  1, -1,  0
#   };

#   old_AB2 <<= 2;
#   if (digitalRead(ENC2_A)) old_AB2 |= 0x02;
#   if (digitalRead(ENC2_B)) old_AB2 |= 0x01;

#   encval2 += enc_states[old_AB2 & 0x0F];

#   if (encval2 > 3) {
#     int changevalue = 1;
#     if ((micros() - _lastIncReadTime2) < _pauseLength) {
#       changevalue *= _fastIncrement;
#     }
#     _lastIncReadTime2 = micros();
#     counter2 += changevalue;
#     encval2 = 0;
#   } else if (encval2 < -3) {
#     int changevalue = -1;
#     if ((micros() - _lastDecReadTime2) < _pauseLength) {
#       changevalue *= _fastIncrement;
#     }
#     _lastDecReadTime2 = micros();
#     counter2 += changevalue;
#     encval2 = 0;
#   }
# }
