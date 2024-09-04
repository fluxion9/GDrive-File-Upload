#include <ESPAsyncWebServer.h>
#include <WiFi.h>
#include <WiFiClient.h>
#include <esp32cam.h>

const char* ssid = "CAM_32_ESP";
const char* pswd = "CAM32-2024";

AsyncWebServer server(80);


static auto loRes = esp32cam::Resolution::find(320, 240);
static auto midRes = esp32cam::Resolution::find(350, 530);
static auto hiRes = esp32cam::Resolution::find(800, 600);

void setup() {
  Serial.begin(9600);
  {
    using namespace esp32cam;
    Config cfg;
    cfg.setPins(pins::AiThinker);
    cfg.setResolution(hiRes);
    cfg.setBufferCount(2);
    cfg.setJpeg(80);
    bool ok = Camera.begin(cfg);
    //Serial.println(ok ? "CAMERA OK" : "CAMERA FAIL");
  }
  WiFi.softAP(ssid, pswd);
  IPAddress IP = WiFi.softAPIP();
  Serial.println();
  Serial.println(IP);

  server.on("/capture", HTTP_GET, [](AsyncWebServerRequest* request) {
    auto frame = esp32cam::capture();
    if (frame == nullptr) {
      request->send(503);
    }
    else {
      AsyncWebServerResponse* response = request->beginResponse_P(200, "image/jpeg", frame->data(), frame->size());
      request->send(response);
    }
  });

  server.on("/ping", HTTP_GET, [](AsyncWebServerRequest* request) {
    request->send(200);
  });

  server.begin();
}

void loop() {
}