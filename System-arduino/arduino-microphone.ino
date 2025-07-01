#include <PDM.h>
#include <WiFiNINA.h>

// Configuração WiFi
const char* ssid = "FRITZ!Box 7590 SU";
const char* password = "00747139424723748140";
const char* devboard_ip = "192.168.178.164"; // IP do Dev Board
const int devboard_port = 5555;

// Buffer de áudio
const int sampleRate = 16000;
const int sampleBit = 16;
short sampleBuffer[512];
volatile int samplesRead;

WiFiClient client;
bool useWiFi = true; // false para usar Serial

void setup() {
Serial.begin(115200);

if (useWiFi) {
  setupWiFi();
}

// Configurar PDM
PDM.onReceive(onPDMdata);
if (!PDM.begin(1, sampleRate)) {
  Serial.println("Falha ao iniciar PDM!");
  while (1);
}

Serial.println("Arduino Microfone Pronto!");
}

void setupWiFi() {
Serial.print("Conectando WiFi...");
WiFi.begin(ssid, password);

while (WiFi.status() != WL_CONNECTED) {
  delay(500);
  Serial.print(".");
}

Serial.println("\nWiFi conectado!");
Serial.print("IP: ");
Serial.println(WiFi.localIP());

// Conectar ao Dev Board
if (client.connect(devboard_ip, devboard_port)) {
  Serial.println("Conectado ao Dev Board!");
}
}

void loop() {
if (samplesRead) {
  if (useWiFi && client.connected()) {
    // Enviar via WiFi
    client.write((byte*)sampleBuffer, samplesRead * 2);
  } else if (!useWiFi) {
    // Enviar via Serial
    Serial.write((byte*)sampleBuffer, samplesRead * 2);
  }
  samplesRead = 0;
}

// Reconectar se necessário
if (useWiFi && !client.connected()) {
  delay(1000);
  client.connect(devboard_ip, devboard_port);
}
}

void onPDMdata() {
int bytesAvailable = PDM.available();
PDM.read(sampleBuffer, bytesAvailable);
samplesRead = bytesAvailable / 2;
}