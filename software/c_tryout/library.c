#include "cJSON.h"
#include <stdio.h>
#include <stdlib.h>
#include <stdio.h> 
#include <stdlib.h> 
#include <unistd.h> 
#include <string.h> 
#include <sys/types.h> 
#include <winsock.h>

const char* get_file_content(const char* path){
FILE* fp;
    fp = fopen(path, "r");
    fseek(fp, 0, SEEK_END);
    long fsize = ftell(fp);
    fseek(fp, 0, SEEK_SET);
    char character;

    char *file_content = (char*) malloc(fsize + 1);
    for(int i = 0; i < fsize; i++){
        character = fgetc(fp);
        if(character != EOF){
            file_content[i] = character;
        }
        else{
            break;
        }
    }
    fclose(fp);
    return file_content;
}

cJSON* get_json_value(const char* json_string, const char* keypath[], int num_of_keysteps){
    cJSON* json_parsed = cJSON_Parse(json_string);
    if (json_parsed == NULL)
    {
        const char *error_ptr = cJSON_GetErrorPtr();
        if (error_ptr != NULL)
        {
            fprintf(stderr, "Error before: %s\n", error_ptr);
        }
    }
    cJSON* value = json_parsed;
    for(int i=0; i < num_of_keysteps; i++){
        value = cJSON_GetObjectItemCaseSensitive(value, keypath[i]);
    }
    //todo: memory leaking
    // cJSON_Delete(json_parsed);
    return value;
}

cJSON* get_sensor_request(const char* file_content, const char* sensor_type){
    const char* path[20]  = {"messages","sensor_request"};
    const char* sensor_type_path[20]  = {"sensors",sensor_type};

    cJSON* sensor_request = get_json_value(file_content, path, 2);
    cJSON* sensor_type_value = get_json_value(file_content, sensor_type_path, 2);
    cJSON_ReplaceItemInObject(sensor_request, "sensor_type", sensor_type_value);
    return sensor_request;
}

int startWinsock(){
    WSADATA wsaData;
    SOCKET socket = INVALID_SOCKET;
    const char *text_to_send = "hello from udp";
    char rcv_buffer[1024];
    int result = WSAStartup(MAKEWORD(2,2), &wsaData);
    if (result != 0){
        printf("WSAStatup failed with errornum %d\n" , result);
        return result;
    }
    else{
        printf("Socket initialized\n");
    }
}

void send_udp(const char* message){
    SOCKET sender_sock;
    sender_sock = socket(AF_INET, SOCK_DGRAM, 17);
    struct sockaddr_in server;
    server.sin_addr.s_addr  = inet_addr("127.0.0.1");
    server.sin_family = AF_INET;
    server.sin_port = htons(5006);
    if(sendto(sender_sock, message, strlen(message), 0,(SOCKADDR*) &server, sizeof(server)) < 0){
        printf("could not send data\n");
    }
    else{
        printf("sent data\n");
    }
}

void* send_and_receive(const char* message, char response[]){
    SOCKET receiver_sock;
    receiver_sock = socket(AF_INET, SOCK_DGRAM, 17);

    struct sockaddr_in client;
    client.sin_addr.s_addr  = inet_addr("127.0.0.1");
    client.sin_family = AF_INET;
    client.sin_port = htons(5005);

    char server_reply[200];

    int clientsize = sizeof(SOCKADDR_IN);
    struct sockaddr_in remove_addr;

    if(bind(receiver_sock ,(struct sockaddr *)&client , sizeof(client)) == SOCKET_ERROR){
		printf("Bind failed with error code : %d" , WSAGetLastError());
    }
    send_udp(message);
    if(recvfrom(receiver_sock, response, 256, 0, (SOCKADDR*)&remove_addr,(int*) &clientsize) == SOCKET_ERROR)
    {
      printf("Fehler: recvfrom, fehler code: %d\n",WSAGetLastError());
    }
    else
    {
      printf("Empfangene Daten: %s\n",server_reply);
    }
}

int main(){
    const char* file_content = get_file_content("./protocol.json");
    cJSON* sensor_request = get_sensor_request(file_content, "accell_x");
    free(file_content);
    const char* sensor_request_string = cJSON_Print(sensor_request);
    cJSON_Delete(sensor_request);
    char response[100];
    startWinsock();
    send_and_receive(sensor_request_string, response);
    printf(response);

    return 0;
}