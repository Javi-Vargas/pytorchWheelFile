import tkinter as tk
from tkinter import messagebox

#print("Hello World")

def close_window():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        window.destroy()

window = tk.Tk()
window.title("Hello GUI")

# Creating a label widget
label = tk.Label(window, text="Hi")
label.pack(padx=20, pady=20)

# Creating a button widget
button = tk.Button(window, text="Close", command=close_window)
button.pack(pady=10)

window.mainloop()
# ~ import PySimpleGUI as sg
# ~ layout = [[sg.Text('GUI Autorun at Startup', font = ("Helvetica",30))], [sg.Text('It works! Click exit to go to Desktop', font=("Calibri",20))],[sg.Exit()]

# ~ window = sg.Window('GUI Autorun', layout, size = (800,400), element_justification="center", finalize=True)
# ~ window.Maximize()

# ~ while True:
    # ~ event, values = windows.read()
    # ~ print(event, values)
    # ~ if event in (sg.WIN_CLOSED, 'Exit'):
        # ~ break

# ~ window.close()

# ~ import depthai
# ~ import blobconverter
# ~ import cv2
# ~ import numpy as np

# ~ def frameNorm(frame, bbox):
    # ~ normVals = np.full(len(bbox), frame.shape[0])
    # ~ normVals[::2] = frame.shape[1]
    # ~ return (np.clip(np.array(bbox), 0, 1) * normVals).astype(int)

# ~ pipeline = depthai.Pipeline()
# ~ cam_rgb = pipeline.create(depthai.node.ColorCamera)
# ~ cam_rgb.setPreviewSize(300, 300)
# ~ cam_rgb.setInterleaved(False)

# ~ detection_nn = pipeline.create(depthai.node.MobileNetDetectionNetwork)
# ~ # Set path of the blob (NN model). We will use blobconverter to convert&download the model
# ~ # detection_nn.setBlobPath("/path/to/model.blob")
# ~ detection_nn.setBlobPath(blobconverter.from_zoo(name='mobilenet-ssd', shaves=6))
# ~ detection_nn.setConfidenceThreshold(0.5)

# ~ cam_rgb.preview.link(detection_nn.input)

# ~ xout_rgb = pipeline.create(depthai.node.XLinkOut)
# ~ xout_rgb.setStreamName("rgb")
# ~ cam_rgb.preview.link(xout_rgb.input)

# ~ xout_nn = pipeline.create(depthai.node.XLinkOut)
# ~ xout_nn.setStreamName("nn")
# ~ detection_nn.out.link(xout_nn.input)

# ~ with depthai.Device(pipeline) as device:
    # ~ q_rgb = device.getOutputQueue("rgb")
    # ~ q_nn = device.getOutputQueue("nn")
    # ~ frame = None
    # ~ detections = []
    
    # ~ while True:
        # ~ in_rgb = q_rgb.tryGet()
        # ~ in_nn = q_nn.tryGet()
        
        # ~ if in_rgb is not None:
            # ~ frame = in_rgb.getCvFrame()
            
        # ~ if in_nn is not None:
            # ~ detections = in_nn.detections
            
        # ~ if frame is not None:
            # ~ for detection in detections:
                # ~ bbox = frameNorm(frame, (detection.xmin, detection.ymin, detection.xmax, detection.ymax))
                # ~ cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (255, 0, 0), 2)
            # ~ cv2.imshow("preview", frame)
            
        # ~ if cv2.waitKey(1) == ord('q'):
            # ~ break
    # ~ cv2.destroyAllWindows()
