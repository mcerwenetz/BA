#include <cJSON.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h> 
#include <string.h> 
#include <sys/types.h> 
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <errno.h>


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
    printf(cJSON_GetErrorPtr());
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
    return value;
}

const char* get_string_value(const char* json_string, const char* object_name){
	cJSON* json = cJSON_Parse(json_string);
	cJSON* value = cJSON_GetObjectItem(json, object_name);
	if(value->valuestring == NULL){
		const char *error_ptr = cJSON_GetErrorPtr();
			if (error_ptr != NULL)
			{
				fprintf(stderr, "Error before: %s\n", error_ptr);
			}
	}
    return value->valuestring;

}

cJSON* get_sensor_request(const char* file_content, const char* sensor_type){
    const char* path[20]  = {"messages","sensor_request"};
    const char* sensor_type_path[20]  = {"sensors",sensor_type};

    cJSON* sensor_request = get_json_value(file_content, path, 2);
    cJSON* sensor_type_value = get_json_value(file_content, sensor_type_path, 2);
    cJSON_ReplaceItemInObject(sensor_request, "sensor_type", sensor_type_value);
    return sensor_request;
}

cJSON* get_rpc_request(const char* file_content, const char* command, const char* value){
    const char* message_path[20]  = {"messages","rpc_request"};
    const char* command_path[20]  = {"commands",command};

    cJSON* rpc_request = get_json_value(file_content, message_path, 2);
    cJSON* rpc_request_command = get_json_value(file_content, command_path, 2);
    cJSON* value_json = cJSON_CreateString(value);

    cJSON_ReplaceItemInObject(rpc_request, "command", rpc_request_command);
    cJSON_ReplaceItemInObject(rpc_request, "value", value_json);
	return rpc_request;
}

void send_udp(const char* message){
    int sender_sock;
    sender_sock = socket(AF_INET, SOCK_DGRAM, 17);
    struct sockaddr_in server;
    server.sin_addr.s_addr  = inet_addr("127.0.0.1");
    server.sin_family = AF_INET;
    server.sin_port = htons(5006);
    if(sendto(sender_sock, message, strlen(message), 0,(const struct sockaddr*) &server, sizeof(server)) < 0){
        printf("could not send data\n");
    }
    else{
//        printf("sent data\n");
    }
    close(sender_sock);
}

void* send_and_receive(const char* message, char response[]){
    int receiver_sock;
    receiver_sock = socket(AF_INET, SOCK_DGRAM, 17);

    struct sockaddr_in client;
    client.sin_addr.s_addr  = inet_addr("127.0.0.1");
    client.sin_family = AF_INET;
    client.sin_port = htons(5005);


    int clientsize = sizeof(struct sockaddr_in);
    struct sockaddr_in remove_addr;

    if(bind(receiver_sock ,(struct sockaddr *)&client , sizeof(client)) < 0){
		printf("Bind failed with error code %d", errno);
    }
    send_udp(message);
    if(recvfrom(receiver_sock, response, 256, 0, (struct sockaddr*) &remove_addr, &clientsize) < 0)
    {
      printf("Fehler: recvfrom");

    }
    close(receiver_sock);
//    else
//    {
////      printf("Empfangene Daten: %s\n",response);
//    }
}

float get_prox(const char* file_content_string){
    cJSON* sensor_request = get_sensor_request(file_content_string, "prox");
    const char* sensor_request_string = cJSON_Print(sensor_request);
    cJSON_Delete(sensor_request);
    char response[500];
     send_and_receive(sensor_request_string, response);
    const char* prox_val_str = get_string_value(response, "value");
    float prox_val = atof(prox_val_str);
    return prox_val;
}


void vibrate(const char* filecontent, int miliseconds){
	char mili_string[20];
	sprintf(mili_string, "%d", miliseconds);
	cJSON* rpc_request = get_rpc_request(filecontent, "vibrate", mili_string);
	const char* rpc_request_string = cJSON_Print(rpc_request);
	send_udp(rpc_request_string);
}

void toggle_button(const char* filecontent){
	cJSON* rpc_request = get_rpc_request(filecontent, "button_toggle", "");
	const char* rpc_request_string = cJSON_Print(rpc_request);
	send_udp(rpc_request_string);
}

void write_text(const char* filecontent, const char* message){
	cJSON* rpc_request = get_rpc_request(filecontent, "write_text", message);
	const char* rpc_request_string = cJSON_Print(rpc_request);
	send_udp(rpc_request_string);
}

//int main(){
//    const char* file_content = get_file_content("./protocol.json");
//    cJSON* sensor_request = get_sensor_request(file_content, "accell_x");
//    free(file_content);
//    const char* sensor_request_string = cJSON_Print(sensor_request);
//    cJSON_Delete(sensor_request);
//    char response[100];
//    startWinsock();
//    send_and_receive(sensor_request_string, response);
//    printf(response);
//
//    return 0;
//}
