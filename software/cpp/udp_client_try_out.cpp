#include "udp_client.h"

int main(int argc, char* argv[]){
    const std::string address = "127.0.0.1";
    const int port = 5006;
    udp_client client = udp_client(address, port);
    client.send()
 
}