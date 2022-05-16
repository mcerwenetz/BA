#include <sys/types.h>
#include <sys/socket.h>
#include <string.h>
#include <netdb.h>
#include <stdexcept>
#include <unistd.h>

class udp_client_server_runtime_error : public std::runtime_error
{
public:
    udp_client_server_runtime_error(const char *w) : std::runtime_error(w) {}
};

class udp_client
{
private:
    int f_socket;
    int f_port;
    std::string f_addr;
    struct addrinfo *f_addrinfo;

public:
    udp_client(const std::string &addr, int port)
        : f_port(port), f_addr(addr)
    {
        char decimal_port[16];
        snprintf(decimal_port, sizeof(decimal_port), "%d", f_port);
        decimal_port[sizeof(decimal_port) / sizeof(decimal_port[0]) - 1] = '\0';
        struct addrinfo hints;
        memset(&hints, 0, sizeof(hints));
        hints.ai_family = AF_UNSPEC;
        hints.ai_socktype = SOCK_DGRAM;
        hints.ai_protocol = IPPROTO_UDP;
        int r(getaddrinfo(addr.c_str(), decimal_port, &hints, &f_addrinfo));
        if (r != 0 || f_addrinfo == NULL)
        {
            throw udp_client_server_runtime_error(("invalid address or port: \"" + addr + ":" + decimal_port + "\"").c_str());
        }
        f_socket = socket(f_addrinfo->ai_family, SOCK_DGRAM | SOCK_CLOEXEC, IPPROTO_UDP);
        if (f_socket == -1)
        {
            freeaddrinfo(f_addrinfo);
            throw udp_client_server_runtime_error(("could not create socket for: \"" + addr + ":" + decimal_port + "\"").c_str());
        }
    }
    ~udp_client()
    {
        freeaddrinfo(f_addrinfo);
        close(f_socket);
    }

    int get_socket() const
    {
        return f_socket;
    }
    std::string get_addr() const
    {
        return f_addr;
    }
    std::string get_addr() const
    {
        return f_addr;
    }

    int send(const char *msg, size_t size)
    {
        return sendto(f_socket, msg, size, 0, f_addrinfo->ai_addr, f_addrinfo->ai_addrlen);
    }
};