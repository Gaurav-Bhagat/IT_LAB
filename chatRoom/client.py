import threading
import socket

alias = input('Choose an username >>> ')
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 50000))

client_running = True

def client_receive():
    global client_running
    while client_running:
        try:
            message = client.recv(1024).decode('utf-8')
            if message == "alias?":
                client.send(alias.encode('utf-8'))
            else:
                print(message)
        except:
            print('Error! Connection closed.')
            client.close()
            break

def client_send():
    global client_running
    while True:
        msg = input("")
        
        if msg == 'EXIT':
            client.send(msg.encode('utf-8'))
            client.close()
            client_running = False
            break
        
        elif msg.startswith('@'):  # Private message format: @alias message
            client.send(msg.encode('utf-8'))
        
        elif msg.startswith('#(') and ')' in msg:  # Group message format: #(user1 user2) message
            client.send(msg.encode('utf-8'))
        
        else:  # General broadcast message
            message = f'{alias}: {msg}'
            client.send(message.encode('utf-8'))

receive_thread = threading.Thread(target=client_receive)
receive_thread.start()

send_thread = threading.Thread(target=client_send)
send_thread.start()
