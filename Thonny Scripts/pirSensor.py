from gpiozero import MotionSensor

pir = MotionSensor(4)
i=0
while True:
    pir.wait_for_motion()
    i+=1
    print("Motion Detected: " , i)
    pir.wait_for_no_motion()

# import RPi.GPIO as GPIO
# import time
# 
# GPIO.setmode(GPIO.BCM)
# PIR_PIN = 17
# 
# 
# GPIO.setup(PIR_PIN, GPIO.IN)
# 
# print("PIR module test (CTRL+C to exit)")
# 
# time.sleep(2)
# 
# print("Ready")
# i=0
# try:
#     while True:
#         if GPIO.input(PIR_PIN):
#             i+=1
#             print("Motion detected!: " , i)
#         time.sleep(2)
# except KeyboardInterrupt:
#     print("Quit")
#     GPIO.cleanup()