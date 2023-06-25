import tkinter as tk
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer

# Global variable to store the entered text
entered_text = ""

# Web server request handler


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html_content = '''
            <html>
            <head>
                <title>Text Display</title>
                <script>
    function displayText() {
        var text = document.getElementById("text-input").value;
        var xhr = new XMLHttpRequest();
        xhr.open("GET", "/submit?text=" + encodeURIComponent(text), true);
        xhr.send();
    }
    
        function displayTextboxText() {
        var textboxText = document.getElementById("text-display").value;
        var xhr = new XMLHttpRequest();
        xhr.open("GET", "/submit?text=" + encodeURIComponent(textboxText), true);
        xhr.send();
    }

                </script>
            </head>
            <body>
                <input type="text" id="text-input">
                <button onclick="displayText(document.getElementById('text-input').value)">Submit</button>
                <br><br>
                <button onclick="displayText('Make')">Make</button>
                <button onclick="displayText('Miss')">Miss</button>
            </body>
            </html>
            '''
            self.wfile.write(html_content.encode())

        elif self.path.startswith('/submit'):
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            query_params = self.path.split('?')[1]
            text = query_params.split('=')[1]
            global entered_text
            entered_text = text
            print(f"Received text: {entered_text}")
            self.wfile.write(b'Text received and processed.')

        else:
            self.send_error(404)

# Function to start the web server


def start_web_server():
    server_address = ('', 8010)
    httpd = HTTPServer(server_address, RequestHandler)
    httpd.serve_forever()

# Function to update the GUI with the entered text


def update_gui():
    global entered_text
    while True:
        if entered_text:
            textbox.config(state=tk.NORMAL)
            textbox.delete(1.0, tk.END)
            textbox.insert(tk.END, entered_text + '\n')
            textbox.config(state=tk.DISABLED)
            entered_text = ""
        window.update()

# Function to handle the "Make" button click


def make_button_click():
    # global entered_text
    # entered_text = "make"
    print("make")

# Function to handle the "Miss" button click


def miss_button_click():
    # global entered_text
    # entered_text = "miss"
    print("miss")


# Create the main window
window = tk.Tk()
window.title("Text Display")

# Create the text box in the GUI
textbox = tk.Text(window, height=10, width=30)
textbox.pack()
textbox.config(state=tk.DISABLED)

# Create the "Make" button
make_button = tk.Button(window, text="Make", command=make_button_click)
make_button.pack()

# Create the "Miss" button
miss_button = tk.Button(window, text="Miss", command=miss_button_click)
miss_button.pack()

# Start the web server in a separate thread
server_thread = threading.Thread(target=start_web_server)
server_thread.daemon = True
server_thread.start()

# Open the web page in a browser
webbrowser.open("http://localhost:8010")

# Start the GUI update loop
gui_thread = threading.Thread(target=update_gui)
gui_thread.daemon = True
gui_thread.start()

# Start the main loop
window.mainloop()
