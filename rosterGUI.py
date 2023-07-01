#!/usr/bin/env python
# coding: utf-8

# In[6]:


import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as messagebox
import cv2
import PIL.Image, PIL.ImageTk
import numpy as np
import easyocr
import mysql.connector

#establish connection to DB
cnx = mysql.connector.connect(
    host='localhost',
    user='root',
    password='javi4',
    database='sd2'
)
cursor = cnx.cursor()
query = ""

def stop_camera():
    # Release the camera
    cap.release()
    cv2.destroyAllWindows()
    
    # Create a black image of the same size as the camera frame
    black_image = np.zeros((240, 320, 3), dtype=np.uint8)
    black_image = PIL.Image.fromarray(black_image)
    black_image = PIL.ImageTk.PhotoImage(black_image)
    
    # Display the black image in the camera frame
    camera_label.configure(image=black_image)
    camera_label.image = black_image

    
def start_camera():
    global cap  # Declare cap as global
    # Start the camera view
    cap = cv2.VideoCapture(0)
    capture_frame.counter = 0
    capture_frame()

# # Create a dropdown menu to select the team
# team_label = tk.Label(window, text="Team:")
# team_label.place(x=10, y=60)

# team_variable = tk.StringVar(window)
# team_dropdown = ttk.Combobox(window, textvariable=team_variable)
# team_dropdown.place(x=60, y=60)

# # Fetch team names from the database and populate the dropdown menu
# query = "SELECT team_name FROM Teams"
# cursor.execute(query)
# teams = cursor.fetchall()

# team_names = [team[0] for team in teams]
# team_dropdown['values'] = team_names
    
    
def add_player():
    team_id = 1
    player = player_entry.get()
    fga = fga_entry.get()
    fgm = fgm_entry.get()

    # Check if player_name already exists in the database
    query = "SELECT * FROM Players WHERE player_name = %s"
    cursor.execute(query, (player,))
    existing_player = cursor.fetchone()

    if existing_player:
        messagebox.showwarning("Error", "Player already exists in the database!")
        return

    # Add the player and values to the treeview
    treeview.insert("", tk.END, values=(player, fga, fgm))
    last_in_cam[0] = player

    # INSERT INTO Players (team_id, player_name, pts, fgm, fga)
    query = "INSERT INTO Players (team_id, player_name, pts, fgm, fga) VALUES (%s, %s, %s, %s, %s)"
    player_values = (team_id, player, 0, fgm, fga)
    cursor.execute(query, player_values)
    cnx.commit()

    # Clear the entry fields
    player_entry.delete(0, tk.END)
    fga_entry.delete(0, tk.END)
    fgm_entry.delete(0, tk.END)

def select_row(event):
    selected_item = treeview.focus()
    values = treeview.item(selected_item, "values")

    # Set the entry fields with the selected row values
    player_entry.delete(0, tk.END)
    fga_entry.delete(0, tk.END)
    fgm_entry.delete(0, tk.END)

    if values:
        player_entry.insert(tk.END, values[0])
        fga_entry.insert(tk.END, values[1])
        fgm_entry.insert(tk.END, values[2])

def move_to_next_row():
    if len(treeview.get_children()) == 0:
        messagebox.showwarning("Error", "No players in the roster. Add players first!")
        return

    selected_item = treeview.focus()
    next_item = treeview.next(selected_item)

    if next_item:
        treeview.selection_set(next_item)
        treeview.focus(next_item)
        treeview.see(next_item)
    else:
        # If no next item, wrap around to the first item
        first_item = treeview.get_children()[0]
        treeview.selection_set(first_item)
        treeview.focus(first_item)
        treeview.see(first_item)

def make_button_click():
    selected_item = treeview.focus()
    if not selected_item:
        messagebox.showwarning("Error", "Must select a player!")
        return

    values = treeview.item(selected_item, "values")
    player = values[0]
    fga = int(values[1]) + 1
    fgm = int(values[2]) + 1
    pts = fgm *2
    treeview.item(selected_item, values=(player, fga, fgm))

    # UPDATE Players SET fga = %s, fgm = %s WHERE player_name = %s
    query = "UPDATE Players SET pts = %s, fga = %s, fgm = %s WHERE player_name = %s"
    player_values = (pts, fga, fgm, player)
    cursor.execute(query, player_values)
    cnx.commit()

    global score
    score += 2
    score_label.config(text="Score: " + str(score))

def miss_button_click():
    selected_item = treeview.focus()
    if not selected_item:
        messagebox.showwarning("Error", "Must select a player!")
        return

    values = treeview.item(selected_item, "values")
    player = values[0]
    fga = int(values[1]) + 1
    fgm = int(values[2])
    treeview.item(selected_item, values=(player, fga, fgm))

    # UPDATE Players SET fga = %s WHERE player_name = %s
    query = "UPDATE Players SET fga = %s WHERE player_name = %s"
    player_values = (fga, player)
    cursor.execute(query, player_values)
    cnx.commit()

def capture_frame():
    ret, frame = cap.read()
    if ret:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = PIL.Image.fromarray(frame)
        image = image.resize((320, 240))
        photo = PIL.ImageTk.PhotoImage(image)
        camera_label.configure(image=photo)
        camera_label.image = photo

        # Perform player detection every 5 seconds
        if capture_frame.counter % 50 == 0:
            player = detect_player(image)
            if player:
                set_values(player, 0, 0)
                add_player()
                # Clear the entry fields
                player_entry.delete(0, tk.END)
                fga_entry.delete(0, tk.END)
                fgm_entry.delete(0, tk.END)

    capture_frame.counter += 1
    camera_label.after(100, capture_frame)

def set_values(player, fga, fgm):
    player_entry.delete(0, tk.END)
    player_entry.insert(tk.END, player)
    fga_entry.delete(0, tk.END)
    fga_entry.insert(tk.END, fga)
    fgm_entry.delete(0, tk.END)
    fgm_entry.insert(tk.END, fgm)

def detect_player(image):
    # Convert PIL image to numpy array
    image_np = np.array(image)

    # Initialize the EasyOCR reader
    reader = easyocr.Reader(['en'])

    # Perform text detection
    result = reader.readtext(image_np)
    

    if len(result) > 0:
        player = result[0][1]
        return player

    return None

# Create the main window
window = tk.Tk()
window.title("Roster")

window.geometry("1000x600")

#set up a state of who was last in camera
last_in_cam = [1]

# Create a label for the score
score = 0
score_label = tk.Label(window, text="Score: " + str(score))
score_label.place(x=10, y=10)

# Create a frame for the camera view
camera_frame = tk.Frame(window)
camera_frame.place(x=10, y=40)

# Create a label for the camera view
camera_label = tk.Label(camera_frame)
camera_label.pack()

# Create a treeview to display the roster
treeview = ttk.Treeview(window, columns=("Player", "FGA", "FGM"), show="headings")
treeview.heading("Player", text="Player")
treeview.heading("FGA", text="FGA")
treeview.heading("FGM", text="FGM")
treeview.place(x=350, y=40)
treeview.bind("<<TreeviewSelect>>", select_row)

# Create entry fields for player, FGA, and FGM
player_label = tk.Label(window, text="Player:")
player_label.place(x=350, y=10)
player_entry = tk.Entry(window)
player_entry.place(x=410, y=10)

fga_label = tk.Label(window, text="FGA:")
fga_label.place(x=530, y=10)
fga_entry = tk.Entry(window)
fga_entry.place(x=580, y=10)

fgm_label = tk.Label(window, text="FGM:")
fgm_label.place(x=700, y=10)
fgm_entry = tk.Entry(window)
fgm_entry.place(x=750, y=10)

# Create a button to add a player
add_button = tk.Button(window, text="Add Player", command=add_player)
add_button.place(x=900, y=8)

# Create a button to move to the next row
next_button = tk.Button(window, text="Next", command=move_to_next_row)
next_button.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

# Create a frame to hold the make and miss buttons
button_frame = tk.Frame(window)
button_frame.place(relx=0.5, rely=0.6, anchor=tk.CENTER)

# Create "Make" and "Miss" buttons inside the frame
make_button = tk.Button(button_frame, text="Make", command=make_button_click)
make_button.pack(side=tk.LEFT, padx=10)

miss_button = tk.Button(button_frame, text="Miss", command=miss_button_click)
miss_button.pack(side=tk.LEFT, padx=10)

# Create a button to stop the camera from 
stop_cam_button = tk.Button(window, text="Stop Camera", command=stop_camera)
stop_cam_button.place(x=120, y=300)

# Create a button to stop the camera from 
start_cam_button = tk.Button(window, text="Start Camera", command=start_camera)
start_cam_button.place(x=30, y=300)

# Start the camera view
cap = cv2.VideoCapture(0)
capture_frame.counter = 0
capture_frame()

# Start the GUI main loop
window.mainloop()

# Release the camera
cap.release()


# In[4]:


#try to have roster gui but use OAK cam instead of webcam
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as messagebox
import cv2
import depthai
import easyocr
import mysql.connector
import numpy as np
from PIL import ImageTk, Image

#establish connection to DB
cnx = mysql.connector.connect(
    host='localhost',
    user='root',
    password='javi4',
    database='sd2'
)
cursor = cnx.cursor()
query = ""

def add_player():
    team_id = 1
    player = player_entry.get()
    fga = fga_entry.get()
    fgm = fgm_entry.get()

    # Add the player and values to the treeview
    treeview.insert("", tk.END, values=(player, fga, fgm))
    last_in_cam[0] = player
    #INSERT INTO Players (team_id, player_name, pts, fgm, fga)
    query = "INSERT INTO Players (team_id, player_name, pts, fgm, fga) VALUES (%d, %s, %d, %d, %d)"
    player_values = (team_id, player_name, pts, fgm, fga)
    cursor.execute(query)
    #result = cursor.fetchall()
    #print(last_in_cam[0])

    # Clear the entry fields
    player_entry.delete(0, tk.END)
    fga_entry.delete(0, tk.END)
    fgm_entry.delete(0, tk.END)

def select_row(event):
    selected_item = treeview.focus()
    values = treeview.item(selected_item, "values")

    # Set the entry fields with the selected row values
    player_entry.delete(0, tk.END)
    fga_entry.delete(0, tk.END)
    fgm_entry.delete(0, tk.END)

    if values:
        player_entry.insert(tk.END, values[0])
        fga_entry.insert(tk.END, values[1])
        fgm_entry.insert(tk.END, values[2])

def move_to_next_row():
    if len(treeview.get_children()) == 0:
        messagebox.showwarning("Error", "No players in the roster. Add players first!")
        return

    selected_item = treeview.focus()
    next_item = treeview.next(selected_item)

    if next_item:
        treeview.selection_set(next_item)
        treeview.focus(next_item)
        treeview.see(next_item)
    else:
        # If no next item, wrap around to the first item
        first_item = treeview.get_children()[0]
        treeview.selection_set(first_item)
        treeview.focus(first_item)
        treeview.see(first_item)

def make_button_click():
    selected_item = treeview.focus()
    if not selected_item:
        messagebox.showwarning("Error", "Must select a player!")
        return

    values = treeview.item(selected_item, "values")
    fga = int(values[1]) + 1
    fgm = int(values[2]) + 1
    treeview.item(selected_item, values=(values[0], fga, fgm))

    global score
    score += 2
    score_label.config(text="Score: " + str(score))

def miss_button_click():
    selected_item = treeview.focus()
    if not selected_item:
        messagebox.showwarning("Error", "Must select a player!")
        return

    values = treeview.item(selected_item, "values")
    fga = int(values[1]) + 1
    fgm = int(values[2])
    treeview.item(selected_item, values=(values[0], fga, fgm))

def capture_frame():
    ret, frame = cap.read()
    if ret:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = PIL.Image.fromarray(frame)
        image = image.resize((320, 240))
        photo = PIL.ImageTk.PhotoImage(image)
        camera_label.configure(image=photo)
        camera_label.image = photo

        # Perform player detection every 5 seconds
        if capture_frame.counter % 50 == 0:
            player = detect_player(image)
            if player:
                set_values(player, 0, 0)
                add_player()
                # Clear the entry fields
                player_entry.delete(0, tk.END)
                fga_entry.delete(0, tk.END)
                fgm_entry.delete(0, tk.END)

    capture_frame.counter += 1
    camera_label.after(100, capture_frame)

def set_values(player, fga, fgm):
    player_entry.delete(0, tk.END)
    player_entry.insert(tk.END, player)
    fga_entry.delete(0, tk.END)
    fga_entry.insert(tk.END, fga)
    fgm_entry.delete(0, tk.END)
    fgm_entry.insert(tk.END, fgm)

def detect_player(image):
    # Convert PIL image to numpy array
    image_np = np.array(image)

    # Initialize the EasyOCR reader
    reader = easyocr.Reader(['en'])

    # Perform text detection
    result = reader.readtext(image_np)
    

    if len(result) > 0:
        player = result[0][1]
        return player

    return None

# Create the pipeline
pipeline = depthai.Pipeline()

# Create the input (color camera) and output (video file) nodes
cam_rgb = pipeline.createColorCamera()
video_out = pipeline.createXLinkOut()

# Set camera properties
cam_rgb.setPreviewSize(300, 300)
cam_rgb.setResolution(depthai.ColorCameraProperties.SensorResolution.THE_1080_P)
cam_rgb.setInterleaved(True)

# Define the video output stream
video_out.setStreamName("preview")

# Link the nodes
cam_rgb.preview.link(video_out.input)

# Connect to the device
with depthai.Device(pipeline) as device:
    # Start the pipeline
    device.startPipeline()

    # Create output queue for preview stream
    preview_queue = device.getOutputQueue("preview", 1, True)

    def stop_camera():
        # Release the camera
        device.stopPipeline()
        cv2.destroyAllWindows()
        
        # Create a black image of the same size as the camera frame
        black_image = np.zeros((240, 320, 3), dtype=np.uint8)
        black_image = Image.fromarray(black_image)
        black_image = ImageTk.PhotoImage(black_image)

        # Display the black image in the camera frame
        camera_label.configure(image=black_image)
        camera_label.image = black_image

    def start_camera():
        # Create the GUI window
        window = tk.Tk()
        window.title("Camera Preview")

        # Create a frame for the camera view
        camera_frame = tk.Frame(window)
        camera_frame.pack()

        # Create a label for the camera view
        camera_label = tk.Label(camera_frame)
        camera_label.pack()

        # Create a stop button
        stop_button = tk.Button(window, text="Stop", command=stop_camera)
        stop_button.pack()

        # Function to update the camera preview
        def update_preview():
            # Get the preview frame
            preview_data = preview_queue.get()

            # Retrieve the OpenCV BGR frame
            frame_bgr = preview_data.getCvFrame()

            # Convert the frame to PIL Image format
            image = Image.fromarray(frame_bgr)

            # Resize the image to fit the label
            image = image.resize((320, 240))

            # Convert the PIL Image to Tkinter PhotoImage format
            photo = ImageTk.PhotoImage(image)

            # Update the label with the new image
            camera_label.configure(image=photo)
            camera_label.image = photo

            # Schedule the next update
            window.after(1, update_preview)

        # Start updating the camera preview
        update_preview()

        # Start the GUI main loop
        window.mainloop()

    # Create the main window
    window = tk.Tk()
    window.title("Roster")

    window.geometry("1000x600")

    #set up a state of who was last in camera
    last_in_cam = [1]

    # Create a label for the score
    score = 0
    score_label = tk.Label(window, text="Score: " + str(score))
    score_label.place(x=10, y=10)

    # Create a frame for the camera view
    camera_frame = tk.Frame(window)
    camera_frame.place(x=10, y=40)

    # Create a label for the camera view
    camera_label = tk.Label(camera_frame)
    camera_label.pack()

    # Create a treeview to display the roster
    treeview = ttk.Treeview(window, columns=("Player", "FGA", "FGM"), show="headings")
    treeview.heading("Player", text="Player")
    treeview.heading("FGA", text="FGA")
    treeview.heading("FGM", text="FGM")
    treeview.place(x=350, y=40)
    treeview.bind("<<TreeviewSelect>>", select_row)

    # Create entry fields for player, FGA, and FGM
    player_label = tk.Label(window, text="Player:")
    player_label.place(x=350, y=10)
    player_entry = tk.Entry(window)
    player_entry.place(x=410, y=10)

    fga_label = tk.Label(window, text="FGA:")
    fga_label.place(x=530, y=10)
    fga_entry = tk.Entry(window)
    fga_entry.place(x=580, y=10)

    fgm_label = tk.Label(window, text="FGM:")
    fgm_label.place(x=700, y=10)
    fgm_entry = tk.Entry(window)
    fgm_entry.place(x=750, y=10)

    # Create a button to add a player
    add_button = tk.Button(window, text="Add Player", command=add_player)
    add_button.place(x=900, y=8)

    # Create a button to move to the next row
    next_button = tk.Button(window, text="Next", command=move_to_next_row)
    next_button.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    # Create a frame to hold the make and miss buttons
    button_frame = tk.Frame(window)
    button_frame.place(relx=0.5, rely=0.6, anchor=tk.CENTER)

    # Create "Make" and "Miss" buttons inside the frame
    make_button = tk.Button(button_frame, text="Make", command=make_button_click)
    make_button.pack(side=tk.LEFT, padx=10)

    miss_button = tk.Button(button_frame, text="Miss", command=miss_button_click)
    miss_button.pack(side=tk.LEFT, padx=10)

    # Create a button to stop the camera from
    stop_cam_button = tk.Button(window, text="Stop Camera", command=stop_camera)
    stop_cam_button.place(x=120, y=300)

    # Create a button to start the camera
    start_cam_button = tk.Button(window, text="Start Camera", command=start_camera)
    start_cam_button.place(x=30, y=300)

    # Start the GUI main loop
    window.mainloop()

# Release the camera
device.close()
cv2.destroyAllWindows()


# In[35]:


#code to swtich screens when buttons are pressed
import tkinter as tk

def switch_to_screen1(*args):
    # Function to switch to screen 1
    welcome_screen.pack_forget()  # Hide the welcome screen
    screen1.pack()  # Show screen 1
    selected_option = dropdown_var.get()
    label1.config(text=f"You selected: {selected_option}")

def switch_to_screen2():
    # Function to switch to screen 2
    welcome_screen.pack_forget()  # Hide the welcome screen
    screen2.pack()  # Show screen 2

root = tk.Tk()
root.title("Roster")
root.geometry("1000x600")

# Create the welcome screen
welcome_screen = tk.Frame(root)
welcome_screen.pack()

welcome_label = tk.Label(welcome_screen, text="Welcome")
welcome_label.pack(pady=10)  # Add vertical spacing using pady

# Create a frame for the buttons
button_frame = tk.Frame(welcome_screen)
button_frame.pack()

# Create a label above the dropdown menu
use_existing_label = tk.Label(button_frame, text="Use Existing Team")
use_existing_label.grid(row=0, column=0, sticky=tk.W)  # Align label to the left using sticky=tk.W

# Create a list of options for the dropdown menu
options = ["Option 1", "Option 2", "Option 3"]

# Create the dropdown menu
dropdown_var = tk.StringVar(root)
dropdown_var.set(options[0])  # Set the initial selected option
dropdown_menu = tk.OptionMenu(button_frame, dropdown_var, *options)
dropdown_menu.grid(row=0, column=1, padx=10)  # Add horizontal spacing using padx

# Create the button to switch to screen 2
button2 = tk.Button(button_frame, text="Create New Team", command=switch_to_screen2)
button2.grid(row=0, column=2, padx=10)  # Add horizontal spacing using padx

# Create screen 1
screen1 = tk.Frame(root)
label1 = tk.Label(screen1, text="You are now on Screen 1")
label1.pack()

# Create screen 2
screen2 = tk.Frame(root)
label2 = tk.Label(screen2, text="You are now on Screen 2")
label2.pack()

# Set the trace on the dropdown variable to switch to screen 1 when an option is selected
dropdown_var.trace("w", switch_to_screen1)

# Start with the welcome screen visible
welcome_screen.pack()

# Start the main event loop
root.mainloop()


# In[ ]:


##Trying to add MQTT Communication
import paho.mqtt.client as mqtt
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as messagebox
import cv2
import PIL.Image, PIL.ImageTk
import numpy as np
import easyocr
import mysql.connector

#Open MQTT Subscription
mqtt_broker = "192.168.8.120"
mqtt_port = 1883
mqtt_topic = "Shot Status"
    
#establish connection to DB
cnx = mysql.connector.connect(
    host='localhost',
    user='root',
    password='javi4',
    database='sd2'
)
cursor = cnx.cursor()
query = ""

def stop_camera():
    # Release the camera
    cap.release()
    cv2.destroyAllWindows()
    
    # Create a black image of the same size as the camera frame
    black_image = np.zeros((240, 320, 3), dtype=np.uint8)
    black_image = PIL.Image.fromarray(black_image)
    black_image = PIL.ImageTk.PhotoImage(black_image)
    
    # Display the black image in the camera frame
    camera_label.configure(image=black_image)
    camera_label.image = black_image
 
def start_camera():
    global cap  # Declare cap as global
    # Start the camera view
    cap = cv2.VideoCapture(0)
    capture_frame.counter = 0
    capture_frame()
    
def add_player():
    team_id = 1
    player = player_entry.get()
    fga = fga_entry.get()
    fgm = fgm_entry.get()

    # Check if player_name already exists in the database
    query = "SELECT * FROM Players WHERE player_name = %s"
    cursor.execute(query, (player,))
    existing_player = cursor.fetchone()

    if existing_player:
        messagebox.showwarning("Error", "Player already exists in the database!")
        return

    # Add the player and values to the treeview
    treeview.insert("", tk.END, values=(player, fga, fgm))
    last_in_cam[0] = player

    # INSERT INTO Players (team_id, player_name, pts, fgm, fga)
    query = "INSERT INTO Players (team_id, player_name, pts, fgm, fga) VALUES (%s, %s, %s, %s, %s)"
    player_values = (team_id, player, 0, fgm, fga)
    cursor.execute(query, player_values)
    cnx.commit()

    # Clear the entry fields
    player_entry.delete(0, tk.END)
    fga_entry.delete(0, tk.END)
    fgm_entry.delete(0, tk.END)

def select_row(event):
    selected_item = treeview.focus()
    values = treeview.item(selected_item, "values")

    # Set the entry fields with the selected row values
    player_entry.delete(0, tk.END)
    fga_entry.delete(0, tk.END)
    fgm_entry.delete(0, tk.END)

    if values:
        player_entry.insert(tk.END, values[0])
        fga_entry.insert(tk.END, values[1])
        fgm_entry.insert(tk.END, values[2])

def move_to_next_row():
    if len(treeview.get_children()) == 0:
        messagebox.showwarning("Error", "No players in the roster. Add players first!")
        return

    selected_item = treeview.focus()
    next_item = treeview.next(selected_item)

    if next_item:
        treeview.selection_set(next_item)
        treeview.focus(next_item)
        treeview.see(next_item)
    else:
        # If no next item, wrap around to the first item
        first_item = treeview.get_children()[0]
        treeview.selection_set(first_item)
        treeview.focus(first_item)
        treeview.see(first_item)

# def add_score():
#     global score
#     score += 2
#     score_label.config(text="Score: " + str(score))

def make_button_click():
    global score
    selected_item = treeview.focus()
    if not selected_item:
        score+=2
        #messagebox.showwarning("Error", "Must select a player!")
        return

    values = treeview.item(selected_item, "values")
    player = values[0]
    fga = int(values[1]) + 1
    fgm = int(values[2]) + 1
    pts = fgm *2
    treeview.item(selected_item, values=(player, fga, fgm))

    # UPDATE Players SET fga = %s, fgm = %s WHERE player_name = %s
    query = "UPDATE Players SET pts = %s, fga = %s, fgm = %s WHERE player_name = %s"
    player_values = (pts, fga, fgm, player)
    cursor.execute(query, player_values)
    cnx.commit()

    #add_score()
    
    score += 2
    score_label.config(text="Score: " + str(score))

def miss_button_click():
    selected_item = treeview.focus()
    if not selected_item:
        messagebox.showwarning("Error", "Must select a player!")
        return

    values = treeview.item(selected_item, "values")
    player = values[0]
    fga = int(values[1]) + 1
    fgm = int(values[2])
    treeview.item(selected_item, values=(player, fga, fgm))

    # UPDATE Players SET fga = %s WHERE player_name = %s
    query = "UPDATE Players SET fga = %s WHERE player_name = %s"
    player_values = (fga, player)
    cursor.execute(query, player_values)
    cnx.commit()

def capture_frame():
    global photo
    ret, frame = cap.read()
    if ret:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = PIL.Image.fromarray(frame)
        image = image.resize((320, 240))
        photo = PIL.ImageTk.PhotoImage(image)
        camera_label.configure(image=photo)
        camera_label.image = photo

        # Perform player detection every 5 seconds
        if capture_frame.counter % 50 == 0:
            player = detect_player(image)
            if player:
                set_values(player, 0, 0)
                add_player()
                # Clear the entry fields
                player_entry.delete(0, tk.END)
                fga_entry.delete(0, tk.END)
                fgm_entry.delete(0, tk.END)

    capture_frame.counter += 1
    camera_label.after(100, capture_frame)

def set_values(player, fga, fgm):
    player_entry.delete(0, tk.END)
    player_entry.insert(tk.END, player)
    fga_entry.delete(0, tk.END)
    fga_entry.insert(tk.END, fga)
    fgm_entry.delete(0, tk.END)
    fgm_entry.insert(tk.END, fgm)

def detect_player(image):
    # Convert PIL image to numpy array
    image_np = np.array(image)

    # Initialize the EasyOCR reader
    reader = easyocr.Reader(['en'])

    # Perform text detection
    result = reader.readtext(image_np)
    

    if len(result) > 0:
        player = result[0][1]
        return player #

    return None

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT Broker")
    client.subscribe(mqtt_topic)
    
def on_message(client, userdata, msg):
    print("Message recieved at topic: ", msg.topic)
    if(msg.payload.decode() == "Sensors Triggered in Correct Order"):
        #add_score()
        print("Basket Status: Make")
        make_button_click()
        
    if(msg.payload.decode() == "Pi"):
        print("Basket Status: Miss")
        miss_button_click()
        
    print("Message: " + msg.payload.decode())

#Main() Start here
#establish mqtt connection Sub/Pub
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(mqtt_broker, mqtt_port, 60)

# client.loop_forever()
# Create the main window
window = tk.Tk()
window.title("Roster")

window.geometry("1000x600")

#set up a state of who was last in camera
last_in_cam = [1]

# Create a label for the score
score = 0
score_label = tk.Label(window, text="Score: " + str(score))
score_label.place(x=10, y=10)

# Create a frame for the camera view
camera_frame = tk.Frame(window)
camera_frame.place(x=10, y=40)

# Create a label for the camera view
camera_label = tk.Label(camera_frame)
camera_label.pack()

# Create a treeview to display the roster
treeview = ttk.Treeview(window, columns=("Player", "FGA", "FGM"), show="headings")
treeview.heading("Player", text="Player")
treeview.heading("FGA", text="FGA")
treeview.heading("FGM", text="FGM")
treeview.place(x=350, y=40)
treeview.bind("<<TreeviewSelect>>", select_row)

# Create entry fields for player, FGA, and FGM
player_label = tk.Label(window, text="Player:")
player_label.place(x=350, y=10)
player_entry = tk.Entry(window)
player_entry.place(x=410, y=10)

fga_label = tk.Label(window, text="FGA:")
fga_label.place(x=530, y=10)
fga_entry = tk.Entry(window)
fga_entry.place(x=580, y=10)

fgm_label = tk.Label(window, text="FGM:")
fgm_label.place(x=700, y=10)
fgm_entry = tk.Entry(window)
fgm_entry.place(x=750, y=10)

# Create a button to add a player
add_button = tk.Button(window, text="Add Player", command=add_player)
add_button.place(x=900, y=8)

# Create a button to move to the next row
next_button = tk.Button(window, text="Next", command=move_to_next_row)
next_button.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

# Create a frame to hold the make and miss buttons
button_frame = tk.Frame(window)
button_frame.place(relx=0.5, rely=0.6, anchor=tk.CENTER)

# Create "Make" and "Miss" buttons inside the frame
make_button = tk.Button(button_frame, text="Make", command=make_button_click)
make_button.pack(side=tk.LEFT, padx=10)

miss_button = tk.Button(button_frame, text="Miss", command=miss_button_click)
miss_button.pack(side=tk.LEFT, padx=10)

# Create a button to stop the camera from 
stop_cam_button = tk.Button(window, text="Stop Camera", command=stop_camera)
stop_cam_button.place(x=120, y=300)

# Create a button to Start the camera from 
start_cam_button = tk.Button(window, text="Start Camera", command=start_camera)
start_cam_button.place(x=30, y=300)

#Start mqtt client loop
client.loop_start()

# Start the camera view
cap = cv2.VideoCapture(0)
capture_frame.counter = 0
capture_frame()
#start_camera()

# Start the GUI main loop
window.mainloop()
# client.loop_forever()
# Release the camera
cap.release()


# In[4]:


cap.release()

