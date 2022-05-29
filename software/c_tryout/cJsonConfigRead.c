#include "cJSON.h"
#include <stdio.h>
#include <stdlib.h>

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

int main(){
    const char* file_content = get_file_content("./protocol.json");
    cJSON* sensor_request = get_sensor_request(file_content, "accell_x");
    printf(cJSON_Print(sensor_request));
    // free(file_content);
    return 0;
}