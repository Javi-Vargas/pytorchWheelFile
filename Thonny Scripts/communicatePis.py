import serial

serial_port = serial.Serial('/dev/ttySO', baudrate=9600,timeout=1)

data = "Test from Javi's Pi4"
serial_port.write(data.encode())

serial_port.close()