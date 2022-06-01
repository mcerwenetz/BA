#include <stdio.h> 
#include <stdlib.h> 
#include <unistd.h> 
#include <string.h> 
#include <sys/types.h> 
#include <winsock.h>

#define MAXLINE 1024
    
int startWinsock(){
    WSADATA wsaData;
    SOCKET socket = INVALID_SOCKET;
    const char *text_to_send = "hello from udp";
    char rcv_buffer[MAXLINE];
    int result = WSAStartup(MAKEWORD(2,2), &wsaData);
    if (result != 0){
        printf("WSAStatup failed with errornum %d\n" , result);
        return result;
    }
    else{
        printf("Socket initialized\n");
    }
}

// Driver code 
int main() { 
    startWinsock();
    SOCKET sender_sock;
    sender_sock = socket(AF_INET, SOCK_DGRAM, 17);
    SOCKET receiver_sock;
    receiver_sock = socket(AF_INET, SOCK_DGRAM, 17);

    char* message = "hallo von lib";
    char server_reply[2000];
    int rc;
    int clientsize = sizeof(SOCKADDR_IN);
    struct sockaddr_in remove_addr;

    if (sender_sock == INVALID_SOCKET){
        printf("Socket could not be created\n");
    }
    printf("socket created\n");
    struct sockaddr_in server;
    //ip = pma
    server.sin_addr.s_addr  = inet_addr("127.0.0.1");
    server.sin_family = AF_INET;
    server.sin_port = htons(5006);

    struct sockaddr_in client;
    client.sin_addr.s_addr  = inet_addr("127.0.0.1");
    client.sin_family = AF_INET;
    client.sin_port = htons(5005);


    if( bind(receiver_sock ,(struct sockaddr *)&client , sizeof(client)) == SOCKET_ERROR)
	{
		printf("Bind failed with error code : %d" , WSAGetLastError());
	}

    if(sendto(sender_sock, message, strlen(message), 0,(SOCKADDR*) &server, sizeof(server)) < 0){
        printf("could not send data\n");
    }
    else{
        printf("sent data\n");
    }

    
    rc = recvfrom(receiver_sock, server_reply, 256, 0, (SOCKADDR*)&remove_addr,(int*) &clientsize);
    if(rc==SOCKET_ERROR)
    {
      printf("Fehler: recvfrom, fehler code: %d\n",WSAGetLastError());
      return 1;
    }
    else
    {
      printf("%d Bytes empfangen!\n", rc);
      printf("Empfangene Daten: %s\n",server_reply);
    }

    closesocket(sender_sock);
    WSACleanup();
    return 0;

}