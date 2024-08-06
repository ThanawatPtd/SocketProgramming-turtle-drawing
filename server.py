import socket
import threading
import turtle

# Set up the server address and port
SERVER_ADDRESS = 'localhost'
SERVER_PORT = 10000

# Create a TCP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((SERVER_ADDRESS, SERVER_PORT))
server_socket.listen(5)

print(f"Drawing server started on {SERVER_ADDRESS}:{SERVER_PORT}")

# Initialize Turtle
screen = turtle.Screen()
screen.title("Turtle Drawing Server")
t = turtle.Turtle()

# Register shapes
shapes = ['spiderman.gif', 'captain.gif', 'thor.gif', 'ironman.gif']
for shape in shapes:
    screen.register_shape("gif/" + shape)

# Dictionary to keep track of each client's name, color, and active shape
client_info = {}
gif_active = False

# Function to handle drawing based on the message
def handle_message(message, client_address):
    global gif_active
    response = "OK - Executed: " + message  # Default response message
    status = 10
    if message == "gif":
        response = " Spiderman.gif, Thor.gif, Captain.gif, Ironman.gif"
        return status, response

    # Clear the screen if a new drawing command is received and a GIF is currently displayed
    if gif_active and message not in shapes:
        t.clear()
        gif_active = False

    # Reset the shape to the default if the current shape is a GIF
    if 'active_shape' in client_info[client_address] and client_info[client_address]['active_shape'] in shapes:
        t.clear()
        t.shape('classic')
        client_info[client_address]['active_shape'] = None

    t.color(client_info[client_address]['color'])

    if message == "draw square":
        for _ in range(4):
            t.forward(100)
            t.right(90)
    elif message == "draw circle":
        t.circle(50)
    elif message == "clear":
        t.clear()
    elif message == "move left":
        t.setheading(180)
        t.forward(50)
    elif message == "move right":
        t.setheading(0)
        t.forward(50)
    elif message == "move up":
        t.setheading(90)
        t.forward(50)
    elif message == "move down":
        t.setheading(270)
        t.forward(50)
    elif message in shapes:
        t.shape("gif/" + message)
        client_info[client_address]['active_shape'] = message
        gif_active = True
    else:
        response = f"Bad Request - Unknown command from {client_address}: {message}"
        status = 20

    return status, response

def process_message(message, client_address):
    status ,response = handle_message(message, client_address)
    return status ,response

def encrypt_send(conn, message):
    # protocol design for encrypt message before send to client
    payload = ":::::" + message + ":::::"
    conn.sendall(payload.encode('utf-8'))

def encrypt_status_send(conn, message, status_code):
    # protocol design for encrypt message with staus before send to client
    payload = ":::::" + str(status_code) + ":::::"  + message +  ":::::"
    conn.sendall(payload.encode('utf-8'))

def client_thread(conn, client_address):
    try:
        # Receive client name and color
        # conn.sendall("Enter your name: ".encode('utf-8'))
        encrypt_send(conn, "Enter your name: ")
        client_name = conn.recv(1024).decode('utf-8').strip()
        color = ["red", "blue", "black", "pink", "yellow"]
        while True:
             # conn.sendall("Enter your color: ".encode('utf-8'))
            encrypt_send(conn, "Enter your color: ")
            client_color = conn.recv(1024).decode('utf-8').strip()
            if client_color in color:
                break
        
        client_info[client_address] = {'name': client_name, 'color': client_color, 'active_shape': None}

        # Send login successful message
        login_success_message = f"Login successful, {client_name}! You can start drawing. Available commands: draw square, draw circle, move left, move right, move up, move down, clear, gif, [gif_name]"
        encrypt_status_send(conn, login_success_message, "40")      

        # # Welcome message
        # welcome_message = f"Welcome {client_name}! You can start drawing. Available commands: draw square, draw circle, move left, move right, move up, move down, clear, gif, [gif_name]"
        #
        # encrypt_status_send(conn, welcome_message, 10)
        
        while True:
            # Receive message from client
            message = conn.recv(1024).decode('utf-8')
            if not message:
                break
            print(f"Received message: {message} from {client_address}")
            
            # Process the message and get the response
            status, response = process_message(message, client_address)
            print(status)
            print(response)
            
            # Send response back to client
            encrypt_status_send(conn, response, status) 
    except Exception as e:
        error_message = f"Internal Server Error - {e}"
        encrypt_status_send(conn, error_message, 30)
        print(f"Error with client {client_address}: {e}")
    finally:
        conn.close()
        if client_address in client_info:
            del client_info[client_address]
        print(f"Client {client_address} disconnected.")

def accept_clients():
    while True:
        conn, client_address = server_socket.accept()
        print(f"Client {client_address} connected.")
        threading.Thread(target=client_thread, args=(conn, client_address)).start()

accept_thread = threading.Thread(target=accept_clients)
accept_thread.start()

turtle.mainloop()
