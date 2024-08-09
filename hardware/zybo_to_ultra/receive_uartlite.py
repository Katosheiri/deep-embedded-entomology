import serial

# Serial port configuration
port = '/dev/ttyUSB0'
# baudrate = 115200
baudrate = 230400
timeout = 10

# Open the serial port
ser = serial.Serial(port, baudrate, timeout=timeout)

# # Load buffer to send
# buffer_length = 100
# buffer = []
# for i in range(0, buffer_length):
#     buffer.append(170)

# # Send buffer
# for i in range(0, buffer_length):
#     ser.write(buffer[i].to_bytes(1, byteorder='big'))

# # Close the serial port
# ser.close()

# print(f"Data sent")

# File to save the received audio data
filename = 'received_data.txt'

# Open the text file to save the received data
with open(filename, 'wb') as f:
    try:
        while True:
            # Read data from the serial port
            data = ser.read()
            # Write data to the file
            f.write(data)
    except KeyboardInterrupt:
        print("Reception interrupted by user.")
    finally:
        ser.close()

print(f"Data received and saved in {filename}")
