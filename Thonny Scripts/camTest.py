import picamera

# Create a new instance of the PiCamera
camera = picamera.PiCamera()

# Set camera resolution (optional)
camera.resolution = (640, 480)

# Start the camera preview
camera.start_preview()

# Wait for a key press to stop the preview
input("Press Enter to stop the preview...")

# Stop the camera preview
camera.stop_preview()

# Release the camera resources
camera.close()
