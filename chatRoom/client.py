import threading
import socket
alias = input('Choose an alias >>> ')
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
            print('Error!')
            client.close()
            break


def client_send():
    global client_running
    while True:
        msg = input("")
        message = f'{alias}: {msg}'
        if(msg == 'EXIT'):
            client.send(msg.encode('utf-8'))
            client.close()
            client_running = False
            break
        else:
            client.send(message.encode('utf-8'))


receive_thread = threading.Thread(target=client_receive)
receive_thread.start()

send_thread = threading.Thread(target=client_send)
send_thread.start()