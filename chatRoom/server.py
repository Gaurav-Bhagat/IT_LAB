import threading
import socket

host = '127.0.0.1'
port = 50000
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

clients = []
aliases = []

def broadcast(message, sender=None):
    """Send a message to all clients except the sender."""
    for client in clients:
        if client != sender:
            client.send(message)

def private_message(sender_client, target_alias, message):
    """Send a private message to a specific client."""
    if target_alias in aliases:
        target_index = aliases.index(target_alias)
        target_client = clients[target_index]
        sender_index = clients.index(sender_client)
        sender_alias = aliases[sender_index]
        
        try:
            target_client.send(f'[Private from {sender_alias}]: {message}'.encode('utf-8'))
            sender_client.send(f'[Private to {target_alias}]: {message}'.encode('utf-8'))
        except:
            target_client.close()
            clients.remove(target_client)
            aliases.remove(target_alias)
    else:
        sender_client.send(f'User {target_alias} not found.'.encode('utf-8'))

def group_message(sender_client, raw_message):
    """Send a message to multiple users safely."""
    sender_index = clients.index(sender_client)
    sender_alias = aliases[sender_index]

    # Extract usernames and message
    start_idx = raw_message.find("(")
    end_idx = raw_message.find(")")
    
    if start_idx == -1 or end_idx == -1:
        sender_client.send("Invalid group message format! Use #(user1 user2) message".encode('utf-8'))
        return
    
    user_list = raw_message[start_idx + 1:end_idx].strip() 
    msg_content = raw_message[end_idx + 1:].strip() 

    recipients = [user.strip() for user in user_list.split()] 

    print(f"Extracted users: {recipients}")  
    print(f"Available aliases: {aliases}") 

    found_any = False
    failed_recipients = []

    for recipient in recipients:
        if recipient in aliases:
            target_index = aliases.index(recipient)
            target_client = clients[target_index]
            try:
                target_client.send(f'[Group from {sender_alias}]: {msg_content}'.encode('utf-8'))
                found_any = True
            except Exception as e:
                print(f"Error sending to {recipient}: {e}")
                failed_recipients.append(recipient) 

    # Notify the sender if some users didn't receive the message
    if failed_recipients:
        sender_client.send(f"Could not send message to: {', '.join(failed_recipients)}".encode('utf-8'))

    if not found_any:
        sender_client.send("No valid recipients found!".encode('utf-8'))



def handle_client(client):
    """Handle messages from clients."""
    while True:
        try:
            message = client.recv(1024).decode('utf-8')

            if message == 'EXIT':
                index = clients.index(client)
                alias = aliases[index]
                clients.remove(client)
                aliases.remove(alias)
                client.close()
                broadcast(f'{alias} has left the chat room!'.encode('utf-8'))
                break

            elif message.startswith('@'):  # Private message format: @alias message
                parts = message.split(' ', 1)
                if len(parts) > 1:
                    target_alias = parts[0][1:]  # Remove '@'
                    msg_content = parts[1]
                    private_message(client, target_alias, msg_content)
                else:
                    client.send("Invalid private message format! Use @alias message".encode('utf-8'))

            elif message.startswith('#(') and ')' in message:  # Group message format: #(user1 user2) message
                group_message(client, message)

            else:
                broadcast(message.encode('utf-8'), sender=client)

        except:
            index = clients.index(client)
            alias = aliases[index]
            clients.remove(client)
            aliases.remove(alias)
            client.close()
            broadcast(f'{alias} has left the chat room!'.encode('utf-8'))
            break

def receive():
    """Accept client connections."""
    while True:
        print('Server is running and listening ...')
        client, address = server.accept()
        print(f'Connection established with {str(address)}')

        client.send('alias?'.encode('utf-8'))
        alias = client.recv(1024).decode('utf-8')

        aliases.append(alias)
        clients.append(client)

        print(f'The Username of this client is {alias}')
        broadcast(f'{alias} has connected to the chat room'.encode('utf-8'))
        client.send('You are now connected!'.encode('utf-8'))

        thread = threading.Thread(target=handle_client, args=(client,))
        thread.start()

if __name__ == "__main__":
    receive()
