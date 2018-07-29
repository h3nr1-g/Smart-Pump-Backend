//
// Created by henry on 03.06.18.
//

#ifndef SERVER_H
#define SERVER_H


struct timings {
    unsigned long active; // in seconds
    unsigned long sleep; // in seconds
};


class PumpControlServer {

public:
    void setPort(unsigned short port);

    void setHost(const char *host);

    timings *fetchTimings(unsigned short id);


private:
    const char *host = nullptr;
    unsigned short port = 443;

    String sendRequest(unsigned short id);
};


#endif //SERVER_H
