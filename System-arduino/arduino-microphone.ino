#include <PDM.h>
#include <WiFiNINA.h>

// WiFi
const char* ssid = "FRITZ!Box 7590 SU";
const char* password = "00747139424723748140";
const char* devboard_ip = "192.168.178.164";
const int devboard_port = 5555;

// Audio
const int frequency = 16000;
short sampleBuffer[512];
volatile int samplesRead = 0;

WiFiClient client;
bool useWiFi = true;
unsigned long lastReconnect = 0;

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  // PDM
  PDM.onReceive(onPDMdata);
  PDM.setGain(50);
  
  if (!PDM.begin(1, frequency)) {
    Serial.println("PDM ERRO!");
    while (1);
  }
  
  if (useWiFi) {
    setupWiFi();
  }
  
  Serial.println("Pronto!");
}

void setupWiFi() {
  WiFi.begin(ssid, password);
  
  int tries = 0;
  while (WiFi.status() != WL_CONNECTED && tries++ < 30) {
    delay(500);
  }
  
  if (WiFi.status() != WL_CONNECTED) {
    useWiFi = false;
    return;
  }
  
  connectServer();
}

void connectServer() {
  if (client.connect(devboard_ip, devboard_port)) {
    Serial.println("Conectado!");
  }
}

void loop() {
  // Enviar dados quando disponível
  if (samplesRead > 0) {
    int bytes = samplesRead * 2;
    
    if (useWiFi && client.connected()) {
      client.write((uint8_t*)sampleBuffer, bytes);
    } else if (!useWiFi) {
      Serial.write((uint8_t*)sampleBuffer, bytes);
    }
    
    samplesRead = 0;
  }
  
  // Reconectar WiFi
  if (useWiFi && !client.connected()) {
    if (millis() - lastReconnect > 5000) {
      lastReconnect = millis();
      connectServer();
    }
  }
}

void onPDMdata() {
  int bytes = PDM.available();
  if (bytes > 0) {
    PDM.read(sampleBuffer, bytes);
    samplesRead = bytes / 2;
  }
}