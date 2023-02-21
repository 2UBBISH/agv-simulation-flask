#include "cbs.h"
#include "ecbs.h"
int main(int /*argc*/, const char* args[])
{
    socket::ptr client_socket1 = cbs::connect();
    socket::ptr client_socket2 = ecbs::connect();
    client_socket1->on("mapInitc++cbs", &cbs::map_init);
    client_socket2->on("mapInitc++ecbs", &ecbs::map_init);
    client_socket1->on("computeRoute_cbs", &cbs::compute_route);
    client_socket2->on("computeRoute_ecbs", &ecbs::compute_route);
    //client_socket->on("computeRoute_ecbs", &compute_route);
    while (true)
    {
        std::this_thread::sleep_for(std::chrono::milliseconds(5));
    }
    ecbs::disconnect();
    cbs::disconnect();
    return 0;
}