import time
import board
import busio
import adafruit_vl53l4cd

# Initialize the I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Initialize the sensor
sensor = adafruit_vl53l4cd.VL53L4CD(i2c)

sensor.version()

# Start continuous measurement
# sensor.start_continuous()
# 
# while True:
#     # Get the distance in millimeters
#     distance = sensor.range
# 
#     # Print the distance
#     print("Distance: {}mm".format(distance))
# 
#     time.sleep(0.1)