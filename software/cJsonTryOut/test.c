#include "cJSON/cJSON.h"
#include <stdio.h>

int main(){
    const char* json = "{\"schluessel\":\"wert\"}";
    const char* new_node_key = "key";
    const char* new_node_val = "val";
    cJSON* new_val_json = cJSON_CreateString(new_node_val);

    cJSON* beispiel = cJSON_Parse(json);
    cJSON_AddItemToObject(beispiel, new_node_key, new_val_json);
    const char* end =  cJSON_Print(beispiel);
    printf(end);
    cJSON_Delete(new_val_json);
    cJSON_Delete(beispiel);
    return 0;
}