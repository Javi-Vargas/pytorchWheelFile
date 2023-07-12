import tkinter as tk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk
import depthai
import blobconverter
import numpy as np
import sqlite3
import paho.mqtt.client as mqtt

#open mqtt connection
mqtt_broker = "192.168.8.120"
mqtt_port = 1883
mqtt_topic = "Shot"

def frameNorm(frame, bbox):
    normVals = np.full(len(bbox), frame.shape[0])
    normVals[::2] = frame.shape[1]
    return (np.clip(np.array(bbox), 0, 1) * normVals).astype(int)


def update_frame(frame):
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(frame)
    img = img.resize((300, 300))
    imgTk = ImageTk.PhotoImage(image=img)
    video_label.imgTk = imgTk
    video_label.configure(image=imgTk)


def add_player():
    player = entry.get()
    team = team_entry.get()
    
    if player:
        table.insert("", "end", values=(player, 0, 0))
        insert_player_into_database(player, team)


def make_shot():
    selected_item = table.focus()
    if selected_item:
        score_value = int(score_label["text"].split(":")[1].strip())
        fgm_value = int(table.item(selected_item)["values"][1])
        fga_value = int(table.item(selected_item)["values"][2])

        table.item(selected_item, values=(table.item(selected_item)["values"][0], fgm_value + 1, fga_value + 1))
        score_label["text"] = f"Score: {score_value + 2}"
        update_player_in_database(table.item(selected_item)["values"][0], fgm_value + 1, fga_value + 1)
    else:
        score_value = int(score_label["text"].split(":")[1].strip())
        score_label["text"] = f"Score: {score_value + 2}"


def miss_shot():
    selected_item = table.focus()
    if selected_item:
        fga_value = int(table.item(selected_item)["values"][2])
        table.item(selected_item, values=(table.item(selected_item)["values"][0], table.item(selected_item)["values"][1], fga_value + 1))
        update_player_in_database(table.item(selected_item)["values"][0], table.item(selected_item)["values"][1], fga_value + 1)


def capture_image():
    selected_item = table.focus()
    if selected_item:
        player = table.item(selected_item)["values"][0]
        file_name = f"{player}.jpg"
    else:
        file_name = "image.jpg"

    in_rgb = q_rgb.tryGet()
    if in_rgb is not None:
        frame = in_rgb.getCvFrame()
        cv2.imwrite(file_name, frame)
        print(f"Image saved as {file_name}")


def insert_player_into_database(player, team):
    fgm = 0
    fga = 0
    conn = sqlite3.connect('sd2.db')
    c = conn.cursor()
    query = "INSERT INTO Players (player_name, team_id, fgm, fga) SELECT ?, team_id, 0, 0 FROM Team WHERE team_name = ?"
    c.execute(query, (player, team))
    conn.commit()
    conn.close()


def update_player_in_database(player, fgm, fga):
    conn = sqlite3.connect('sd2.db')
    c = conn.cursor()
    c.execute("UPDATE players SET fgm = ?, fga = ?, pts = ? WHERE player_name = ?", (fgm, fga, (fgm*2), player))
    conn.commit()
    conn.close()


def load_team():
    team_name = team_entry.get()
    if team_name:
        players = get_players_from_team(team_name)
        clear_table()
        for player in players:
            table.insert("", "end", values=(player[0], player[1], player[2]))


def get_players_from_team(team_name):
    conn = sqlite3.connect('sd2.db')
    c = conn.cursor()
    c.execute("SELECT Players.player_name, Players.fgm, Players.fga FROM Players JOIN Team ON Players.team_id = Team.team_id WHERE Team.team_name = ?", (team_name,))
    players = c.fetchall()
    conn.close()
    return players


def clear_table():
    for item in table.get_children():
        table.delete(item)


def process_frame():
    in_rgb = q_rgb.tryGet()
    in_nn = q_nn.tryGet()

    if in_rgb is not None:
        frame = in_rgb.getCvFrame()
        update_frame(frame)

        if in_nn is not None:
            detections = in_nn.detections

            for detection in detections:
                bbox = frameNorm(frame, (detection.xmin, detection.ymin, detection.xmax, detection.ymax))
                cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (255, 0, 0), 2)

        update_frame(frame)

    root.after(1, process_frame)

def reset_player_stats():
    team_name = team_entry.get()

    # Get the team_id based on the team_name
    conn = sqlite3.connect('sd2.db')
    c = conn.cursor()
    c.execute("SELECT team_id FROM Team WHERE team_name = ?", (team_name,))
    team_id = c.fetchone()[0]

    # Reset the player stats to 0 for the given team_id
    c.execute("UPDATE Players SET fgm = 0, fga = 0, pts = 0 WHERE team_id = ?", (team_id,))
    conn.commit()
    conn.close()

def end_game():
    team_name = team_entry.get()
    team_id = team_entry.get()
    players = get_players_from_team(team_id)
    with open('game_results.txt', 'w') as file:
        # Get the current score
        score_value = int(score_label["text"].split(":")[1].strip())
        file.write(f"Score: {score_value}\n")
        file.write(f"Team: {team_name}\n")
        file.write("\nPlayer\tFGM\tFGA\n")
        for player in players:
            file.write(f"{player[0]}\t\t{player[1]}\t{player[2]}\n")

    # Reset the player stats to 0
    reset_player_stats()

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT Broker")
    client.subscribe(mqtt_topic);
    
def on_message(client, userdata, msg):
    if(msg.payload.decode() == "Make"):
        print(msg.payload.decode())
        make_shot()
    
    if(msg.payload.decode() == "Miss"):
        print(msg.payload.decode())
        miss_shot()
    
#establish mqtt
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(mqtt_broker,mqtt_port,60)

#Starting camera use/ pipeline
pipeline = depthai.Pipeline()
cam_rgb = pipeline.create(depthai.node.ColorCamera)
cam_rgb.setPreviewSize(300, 300)
cam_rgb.setInterleaved(False)

detection_nn = pipeline.create(depthai.node.MobileNetDetectionNetwork)
detection_nn.setBlobPath(blobconverter.from_zoo(name='mobilenet-ssd', shaves=6))
detection_nn.setConfidenceThreshold(0.5)

cam_rgb.preview.link(detection_nn.input)

xout_rgb = pipeline.create(depthai.node.XLinkOut)
xout_rgb.setStreamName("rgb")
cam_rgb.preview.link(xout_rgb.input)

xout_nn = pipeline.create(depthai.node.XLinkOut)
xout_nn.setStreamName("nn")
detection_nn.out.link(xout_nn.input)

with depthai.Device(pipeline) as device:
    q_rgb = device.getOutputQueue("rgb")
    q_nn = device.getOutputQueue("nn")
    frame = None
    detections = []

    root = tk.Tk()
    root.title("Camera GUI")

    # Create a label for video feed
    video_label = tk.Label(root)
    video_label.pack(side="left")

    # Create a score label
    score_label = tk.Label(root, text="Score: 0", font=("Arial", 14, "bold"))
    score_label.pack()

    # Create a table for detections
    table_frame = tk.Frame(root)
    table_frame.pack(side="right")

    table = ttk.Treeview(table_frame, columns=("player", "fgm", "fga"))
    table["show"] = "headings"
    table.heading("player", text="Player")
    table.heading("fgm", text="FGM")
    table.heading("fga", text="FGA")
    table.pack()

    # Create a frame for the text box and buttons
    add_frame = tk.Frame(root)
    add_frame.pack(side="top", pady=10)

    # Create the text box
    entry = tk.Entry(add_frame)
    entry.pack(side="left")

    # Create the "Add Player" button
    add_button = tk.Button(add_frame, text="Add Player", command=add_player)
    add_button.pack(side="left")

    # Create the "Load Team" text box
    team_frame = tk.Frame(root)
    team_frame.pack(side="top", pady=10)

    team_label = tk.Label(team_frame, text="Team Name:")
    team_label.pack(side="left")

    team_entry = tk.Entry(team_frame)
    team_entry.pack(side="left")

    # Create the "Load Team" button
    load_button = tk.Button(team_frame, text="Load Team", command=load_team)
    load_button.pack(side="left")

    # Create the "Make" button
    make_button = tk.Button(root, text="Make", command=make_shot)
    make_button.pack(side="top")

    # Create the "Miss" button
    miss_button = tk.Button(root, text="Miss", command=miss_shot)
    miss_button.pack(side="top")

    # Create the "End Game" button
    end_game_button = tk.Button(root, text="End Game", command=end_game)
    end_game_button.pack(side="top")

    client.loop_start()
    process_frame()
    root.mainloop()
    cv2.destroyAllWindows()
