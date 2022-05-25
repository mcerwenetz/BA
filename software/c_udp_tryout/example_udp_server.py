import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
sock.bind(("127.0.0.1", 5006))
data = sock.recvfrom(1024)


print(str(data[0], encoding="utf-8"))

i = sock.sendto(bytes("Hallo vom Server", encoding="utf-8"), ("127.0.0.1",5005))
print("sent data %s"  % str(i))