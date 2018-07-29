//
// Created by henry on 03.06.18.
//

#include <cstdio>
#include <cstring>
#include <Arduino.h>
#include <ESP8266HTTPClient.h>
#include "server.h"
#include <ArduinoJson.h>


void PumpControlServer::setPort(const unsigned short port) {
    this->port = port;
}

void PumpControlServer::setHost(const char *host) {
    this->host = host;
}

struct timings *PumpControlServer::fetchTimings(unsigned short id) {
    String responseData = this->sendRequest(id);
    if (responseData.length() < 1)
        return nullptr;

    StaticJsonBuffer<200> jsonBuffer;
    JsonObject &data = jsonBuffer.parseObject(responseData);
    if (!data.success()) {
        Serial.println("[!] Parsing failed");
        return nullptr;
    }

    static struct timings *receivedTimings = nullptr;
    if (receivedTimings == nullptr) {
        receivedTimings = (struct timings *) (malloc(sizeof(struct timings)));
    } else {
        memset(receivedTimings, 0, sizeof(struct timings));
    }

    receivedTimings->active = data["active"].as<unsigned long>();
    receivedTimings->sleep = data["sleep"].as<unsigned long>();
    return receivedTimings;
}

String PumpControlServer::sendRequest(unsigned short id) {
    char url[200];
    memset(url, 0, sizeof(url));
    sprintf(url, "/api/pumps/%d/timings", id);

    //decide if we use HTTP or HTTPS for the data exchange
    HTTPClient http;
    http.begin(this->host, this->port, url);

    int responseCode = http.GET();
    if (responseCode != HTTP_CODE_OK) {
        Serial.print("[!] Received response with status code ");
        Serial.println(responseCode);
        return "";
    }

    return http.getString();
}
