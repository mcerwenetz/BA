import socket



localIP     = "127.0.0.1"



# Create a datagram socket

UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)



# Bind to address and ip

UDPServerSocket.bind((localIP, 5006))



print("UDP server up and listening")



# Listen for incoming datagrams

while(True):

    bytesAddressPair = UDPServerSocket.recvfrom(1024)

    message = bytesAddressPair[0]

    address = bytesAddressPair[1]

    clientMsg = "Message from Client:{}".format(message)
    clientIP  = "Client IP Address:{}".format(address)
    
    print(clientMsg)
    print(clientIP)