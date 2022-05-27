#include "cJSON/cJSON.h"
#include <stdio.h>
#include <stdlib.h>


int main(){

    FILE* fp;
    const char* path = "./protocol.json";
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
    cJSON* protocol = cJSON_Parse(file_content);
    if (protocol == NULL)
    {
        const char *error_ptr = cJSON_GetErrorPtr();
        if (error_ptr != NULL)
        {
            fprintf(stderr, "Error before: %s\n", error_ptr);
        }
    }
    const cJSON* commands = cJSON_GetObjectItemCaseSensitive(protocol, "commands");
    const char* commands_string = cJSON_Print(commands);
    printf(commands_string);

    cJSON_Delete(protocol);
    free(file_content);
    return 0;
}