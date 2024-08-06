import socket
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
def decrypt_message(payload):
    message : str = payload.decode('utf-8')
    if message.startswith(':::::') and message.endswith(':::::'):
        return message.strip(":::::")
    return ""

def decrypt_status_message(payload):
    message : str = payload.decode('utf-8')
    if message.startswith(':::::') and message.endswith(':::::'):
        message = message.strip(":::::")
        message_list = message.split(":::::")
        if(message_list[0] == '10' or message_list[0] == '40'):
            message_list[1] = bcolors.OKGREEN+message_list[1]+bcolors.ENDC
        elif message_list[0] == '20' or message_list[0] == '30':
            message_list[1] = bcolors.FAIL + message_list[1] + bcolors.ENDC
        return message_list
    return [-1, ""]

# Set up the server address and port
SERVER_ADDRESS = 'localhost'
SERVER_PORT = 10000

# Create a TCP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_ADDRESS, SERVER_PORT))

try:
    # Receive and send the name
    name_prompt = decrypt_message(client_socket.recv(1024))
    print(name_prompt, ' ')
    name = input()
    client_socket.sendall(name.encode('utf-8'))
    
    # Receive and send the color
    while True:
        color_list = ["red", "blue", "pink", "black", "yellow"]
        color_prompt = decrypt_message(client_socket.recv(1024))
        print(color_prompt, ' ')
        color = input()
        color = color.lower()
        client_socket.sendall(color.encode('utf-8'))
        if color in color_list:
            break
    
    # Receive welcome message
    status, welcome_message = decrypt_status_message(client_socket.recv(1024))
    print(status, welcome_message)
    
    while True:
        # Ask the user for input to send to the server
        message = input("Enter drawing command (draw square, draw circle, clear, move left, move right, move up, move down, gif or exit): ")
        message = message.lower() 
        if message.lower() == "exit":
            break
        
        # Send the command to the server
        client_socket.sendall(message.encode('utf-8'))
        
        # Receive response from the server
        status, response = decrypt_status_message(client_socket.recv(1024))
        print(status, response)

except Exception as e:
    print(f"An error occurred: {e}")
finally:
    client_socket.close()
