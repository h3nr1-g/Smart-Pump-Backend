#include <Arduino.h>
#include <ESP8266WiFi.h>
#include "server.h"

#define BAUD_RATE 115200


// wifi configuration
const char *WIFI_SSID = "WIFI-SSID";
const char *WIFI_PASSWORD = "PASSWORD-1234";


// Pin configuration
const int ID_SW_1 = 5;
const int ID_SW_2 = 14;
const int ID_SW_4 = 4;
const int ID_SW_8 = 12;
const int PUMP = 13;


// Back end configuration
const char *HOST = "192.168.178.91";
const unsigned short PORT = 8000;


//Runtime variables
long unsigned int SLEEP_PERIOD = 1;
unsigned short ID = 1;
PumpControlServer server;


unsigned short getBoardID() {
    unsigned short id = 0;
    if (digitalRead(ID_SW_1) == LOW)
        id += 1;
    if (digitalRead(ID_SW_2) == LOW)
        id += 2;
    if (digitalRead(ID_SW_4) == LOW)
        id += 4;
    if (digitalRead(ID_SW_8) == LOW)
        id += 8;

    Serial.print("Board ID: ");
    Serial.println(id);
    return id;
}


bool initializeWiFi() {
    Serial.print("[*] Try to connect to WiFi with SSID ");
    Serial.println(WIFI_SSID);

    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");

        if (WiFi.status() == WL_CONNECT_FAILED) {
            Serial.println("[!] Incorrect SSID or password");
            return false;
        }
    }
    Serial.println("");
    Serial.println("[+] WiFi connected");
    Serial.print("[*] IP address: ");
    Serial.println(WiFi.localIP());

    return true;
}


void setup() {
    Serial.begin(BAUD_RATE);
    Serial.println("[+] Start ESP firmware initialization\n");

    pinMode(ID_SW_1, INPUT);
    pinMode(ID_SW_2, INPUT);
    pinMode(ID_SW_4, INPUT);
    pinMode(ID_SW_8, INPUT);
    pinMode(PUMP, OUTPUT);
    digitalWrite(PUMP, 0);

    ID = getBoardID();
    server.setHost(HOST);
    server.setPort(PORT);
    Serial.println("[+]Finished ESP firmware initialization\n");
}


void loop() {
    if (initializeWiFi()) {
        struct timings *t = server.fetchTimings(ID);
        if (t) {
            SLEEP_PERIOD = t->sleep;
            if (t->active > 0) {
                Serial.print("Activate pump for ");
                Serial.print(t->active);
                Serial.println(" s\n");
                digitalWrite(PUMP, 1);
                delay(t->active * 1000);
                digitalWrite(PUMP, 0);
            }
        } else {
            Serial.println("[!] Failed to get pump timings\n");
        }
    }
    if (SLEEP_PERIOD > 0) {
        Serial.print("Sleep for ");
        Serial.print(SLEEP_PERIOD);
        Serial.println(" s\n");
        ESP.deepSleep(SLEEP_PERIOD * 1000000, WAKE_RF_DEFAULT);
    }
}

