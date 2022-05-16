#include "udp_client.h"

enum request_type{
    sensor_request,
    rpc_request
};

enum sensor_types{
    x_accell,
    y_accell,
    z_accell
};

enum command{
    write_text,
    toggle_button,
    vibrate
};

struct sensor_request
{
    const char* request_type;
    const char* sensor_type;
};

struct rpc_request
{
    const char* request_type;
    const char* command;
    const char* arg;
};
