#include <PDM.h>
#include <WiFiNINA.h>

// Configuração WiFi
const char* ssid = "FRITZ!Box 7590 SU";
const char* password = "00747139424723748140";
const char* devboard_ip = "192.168.178.164";
const int devboard_port = 5555;

// Buffer de áudio
const int sampleRate = 16000;
const int sampleBit = 16;
short sampleBuffer[2048]; // Aumentado de 512
volatile int samplesRead;
volatile bool isRecording = false;

WiFiClient client;
bool useWiFi = true;
unsigned long lastDataTime = 0;
int totalSamples = 0;

// LEDs para status
const int LED_BUILTIN_RED = 23;
const int LED_BUILTIN_GREEN = 24;
const int LED_BUILTIN_BLUE = 25;

void setup() {
  Serial.begin(115200);
  while (!Serial && millis() < 3000); // Aguarda Serial ou timeout
  
  // Configurar LEDs
  pinMode(LED_BUILTIN_RED, OUTPUT);
  pinMode(LED_BUILTIN_GREEN, OUTPUT);
  pinMode(LED_BUILTIN_BLUE, OUTPUT);
  
  // LED azul = inicializando
  setLED(0, 0, 255);
  
  if (useWiFi) {
    setupWiFi();
  } else {
    // LED verde para Serial
    setLED(0, 255, 0);
  }
  
  // Configurar PDM
  PDM.onReceive(onPDMdata);
  PDM.setBufferSize(2048); // Aumentar buffer interno
  
  if (!PDM.begin(1, sampleRate)) {
    Serial.println("ERRO: PDM falhou!");
    setLED(255, 0, 0); // LED vermelho
    while (1);
  }
  
  Serial.println("PDM OK!");
  Serial.println("READY"); // Sinal para Python
  
  lastDataTime = millis();
}

void setupWiFi() {
  Serial.print("Conectando WiFi...");
  WiFi.begin(ssid, password);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 30) {
    delay(500);
    Serial.print(".");
    // LED azul piscando
    setLED(0, 0, attempts % 2 ? 255 : 0);
    attempts++;
  }
  
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("\nERRO: WiFi falhou!");
    setLED(255, 0, 0); // LED vermelho
    useWiFi = false;
    return;
  }
  
  Serial.println("\nWiFi OK!");
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());
  
  // Conectar ao Dev Board
  if (client.connect(devboard_ip, devboard_port)) {
    Serial.println("Conectado ao Dev Board!");
    setLED(0, 255, 0); // LED verde
    // Enviar handshake
    client.println("ARDUINO_READY");
  } else {
    Serial.println("ERRO: Conexão Dev Board falhou!");
    setLED(255, 0, 0);
  }
}

void loop() {
  // Processar comandos seriais
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    
    if (cmd == "START") {
      isRecording = true;
      totalSamples = 0;
      Serial.println("RECORDING");
    } else if (cmd == "STOP") {
      isRecording = false;
      Serial.println("STOPPED");
      Serial.print("SAMPLES:");
      Serial.println(totalSamples);
    } else if (cmd == "STATUS") {
      Serial.print("STATUS:");
      Serial.print(isRecording ? "REC" : "IDLE");
      Serial.print(",SAMPLES:");
      Serial.println(totalSamples);
    }
  }
  
  // Enviar dados de áudio
  if (samplesRead && isRecording) {
    int bytesToSend = samplesRead * 2;
    totalSamples += samplesRead;
    
    if (useWiFi && client.connected()) {
      // Enviar header antes dos dados
      client.write('A'); // Marcador de início
      client.write((byte)(bytesToSend >> 8)); // MSB
      client.write((byte)(bytesToSend & 0xFF)); // LSB
      client.write((byte*)sampleBuffer, bytesToSend);
    } else if (!useWiFi) {
      // Protocolo serial: START_MARKER + SIZE + DATA
      Serial.write(0xFF); // Marcador
      Serial.write(0xFE); // Marcador
      Serial.write((byte)(bytesToSend >> 8));
      Serial.write((byte)(bytesToSend & 0xFF));
      Serial.write((byte*)sampleBuffer, bytesToSend);
    }
    
    lastDataTime = millis();
    samplesRead = 0;
  }
  
  // Reconectar WiFi se necessário
  if (useWiFi && !client.connected()) {
    static unsigned long lastReconnect = 0;
    if (millis() - lastReconnect > 5000) {
      Serial.println("Reconectando...");
      setLED(255, 255, 0); // LED amarelo
      
      if (client.connect(devboard_ip, devboard_port)) {
        Serial.println("Reconectado!");
        setLED(0, 255, 0);
        client.println("ARDUINO_READY");
      }
      lastReconnect = millis();
    }
  }
  
  // Heartbeat - piscar LED se gravando
  static unsigned long lastBlink = 0;
  if (isRecording && millis() - lastBlink > 500) {
    static bool ledState = false;
    setLED(0, ledState ? 255 : 128, 0); // Verde piscando
    ledState = !ledState;
    lastBlink = millis();
  }
}

void onPDMdata() {
  int bytesAvailable = PDM.available();
  if (bytesAvailable > 0) {
    PDM.read(sampleBuffer, bytesAvailable);
    samplesRead = bytesAvailable / 2;
  }
}

void setLED(int r, int g, int b) {
  analogWrite(LED_BUILTIN_RED, 255 - r);
  analogWrite(LED_BUILTIN_GREEN, 255 - g);
  analogWrite(LED_BUILTIN_BLUE, 255 - b);
}