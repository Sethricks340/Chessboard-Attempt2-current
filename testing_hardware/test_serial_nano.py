import serial
import time

PORT = "COM4"
BAUD = 9600

ser = serial.Serial(PORT, BAUD, timeout=1)

# Wait for READY from Arduino
while True:
    line = ser.readline().decode('utf-8', errors='ignore').strip()
    if line:
        print("Arduino:", line)
    if "READY" in line:
        break

# Send messages in a loop
message = ""
while message != "quit":
    ser.write((message + "\n").encode('utf-8'))  # encode string → bytes
    message = input("enter message: ")
