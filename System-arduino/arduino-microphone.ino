/*
 * Sistema de Microfone Remoto com Arduino Nano RP2040 Connect
 * Captura áudio via PDM e envia para Dev Board via WiFi ou Serial
 * 
 * Hardware: Arduino Nano RP2040 Connect (microfone PDM integrado)
 * Autor: Sistema Assistente de Voz para Carro
 * Versão: 1.0
 */

#include <PDM.h>      // Biblioteca para microfone PDM
#include <WiFiNINA.h> // Biblioteca WiFi

// ===== CONFIGURAÇÕES DO USUÁRIO =====
const char* ssid = "SEU_WIFI";              // Nome da rede WiFi
const char* password = "SUA_SENHA";         // Senha do WiFi
const char* devboard_ip = "192.168.1.100";  // IP do Dev Board (descobrir com hostname -I)
const int devboard_port = 5555;             // Porta TCP para comunicação

// ===== CONFIGURAÇÕES DO SISTEMA =====
const int sampleRate = 16000;  // Taxa de amostragem em Hz (16kHz padrão para voz)
const int sampleBit = 16;      // Bits por amostra
const int bufferSize = 512;    // Tamanho do buffer de áudio
short sampleBuffer[bufferSize]; // Buffer para armazenar amostras de áudio
volatile int samplesRead;       // Contador de amostras lidas (volatile pois é usado em interrupt)

// ===== MODOS DE OPERAÇÃO =====
bool useWiFi = true;  // true = WiFi, false = Serial USB
bool debugMode = true; // Ativar mensagens de debug

// ===== OBJETOS =====
WiFiClient client;     // Cliente TCP para conexão WiFi

// ===== LED DE STATUS =====
// Usa o LED RGB integrado do Nano RP2040 Connect
const int LED_R = LEDR;
const int LED_G = LEDG;
const int LED_B = LEDB;

void setup() {
  // Inicializar Serial para debug
  Serial.begin(115200);
  while (!Serial && millis() < 5000); // Aguarda Serial ou timeout de 5s
  
  Serial.println("=== Arduino Microfone Remoto ===");
  Serial.println("Iniciando sistema...");
  
  // Configurar LEDs (são invertidos - LOW = ligado)
  pinMode(LED_R, OUTPUT);
  pinMode(LED_G, OUTPUT);
  pinMode(LED_B, OUTPUT);
  setLED(0, 0, 255); // Azul = iniciando
  
  // Configurar modo de operação
  if (useWiFi) {
    Serial.println("Modo: WiFi");
    setupWiFi();
  } else {
    Serial.println("Modo: Serial USB");
    setLED(0, 255, 0); // Verde = pronto
  }
  
  // Configurar microfone PDM
  setupPDM();
  
  Serial.println("Sistema pronto!");
}

void setupWiFi() {
  Serial.print("Conectando ao WiFi ");
  Serial.print(ssid);
  Serial.print("...");
  
  // Piscar LED azul enquanto conecta
  int attempts = 0;
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED && attempts < 30) {
    delay(500);
    Serial.print(".");
    toggleLED(0, 0, 255); // Piscar azul
    attempts++;
  }
  
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("\nFalha ao conectar WiFi!");
    setLED(255, 0, 0); // Vermelho = erro
    while (1); // Parar execução
  }
  
  Serial.println("\nWiFi conectado!");
  Serial.print("IP do Arduino: ");
  Serial.println(WiFi.localIP());
  
  // Conectar ao Dev Board
  connectToDevBoard();
}

void connectToDevBoard() {
  Serial.print("Conectando ao Dev Board ");
  Serial.print(devboard_ip);
  Serial.print(":");
  Serial.print(devboard_port);
  Serial.print("...");
  
  if (client.connect(devboard_ip, devboard_port)) {
    Serial.println(" Conectado!");
    setLED(0, 255, 0); // Verde = conectado
    
    // Enviar identificação
    client.println("ARDUINO_MIC_READY");
  } else {
    Serial.println(" Falha na conexão!");
    setLED(255, 0, 0); // Vermelho = erro
  }
}

void setupPDM() {
  Serial.println("Configurando microfone PDM...");
  
  // Configurar callback para quando há dados disponíveis
  PDM.onReceive(onPDMdata);
  
  // Inicializar PDM com 1 canal e taxa de amostragem
  if (!PDM.begin(1, sampleRate)) {
    Serial.println("Falha ao inicializar PDM!");
    setLED(255, 0, 0); // Vermelho = erro
    while (1); // Parar execução
  }
  
  Serial.println("Microfone PDM configurado!");
  Serial.print("Taxa de amostragem: ");
  Serial.print(sampleRate);
  Serial.println(" Hz");
}

void loop() {
  // Verificar se há amostras para enviar
  if (samplesRead > 0) {
    // Calcular tamanho em bytes
    int bytesToSend = samplesRead * 2; // 2 bytes por amostra (16 bits)
    
    if (useWiFi) {
      // Enviar via WiFi
      if (client.connected()) {
        // Enviar dados de áudio
        int bytesSent = client.write((byte*)sampleBuffer, bytesToSend);
        
        if (debugMode && bytesSent > 0) {
          Serial.print("Enviado: ");
          Serial.print(bytesSent);
          Serial.println(" bytes");
        }
      } else {
        // Tentar reconectar
        Serial.println("Conexão perdida. Reconectando...");
        setLED(255, 255, 0); // Amarelo = reconectando
        delay(1000);
        connectToDevBoard();
      }
    } else {
      // Enviar via Serial
      Serial.write((byte*)sampleBuffer, bytesToSend);
    }
    
    // Resetar contador
    samplesRead = 0;
  }
  
  // Pequena pausa para não sobrecarregar
  delay(1);
  
  // Verificar status da conexão WiFi periodicamente
  static unsigned long lastCheck = 0;
  if (useWiFi && millis() - lastCheck > 5000) {
    lastCheck = millis();
    
    if (WiFi.status() != WL_CONNECTED) {
      Serial.println("WiFi desconectado! Reconectando...");
      setLED(255, 255, 0); // Amarelo
      WiFi.begin(ssid, password);
    }
  }
}

// Callback chamado quando há dados do microfone PDM
void onPDMdata() {
  // Ler dados disponíveis
  int bytesAvailable = PDM.available();
  
  // Ler para o buffer
  PDM.read(sampleBuffer, bytesAvailable);
  
  // Converter bytes para número de amostras (16 bits = 2 bytes por amostra)
  samplesRead = bytesAvailable / 2;
  
  if (debugMode && samplesRead > 0) {
    // Calcular nível de áudio (RMS)
    long sum = 0;
    for (int i = 0; i < samplesRead; i++) {
      sum += abs(sampleBuffer[i]);
    }
    int average = sum / samplesRead;
    
    // Mostrar nível apenas se significativo
    if (average > 100) {
      Serial.print("Nível de áudio: ");
      Serial.println(average);
    }
  }
}

// ===== FUNÇÕES AUXILIARES =====

// Definir cor do LED RGB (valores 0-255, mas invertidos no hardware)
void setLED(int r, int g, int b) {
  analogWrite(LED_R, 255 - r);
  analogWrite(LED_G, 255 - g);
  analogWrite(LED_B, 255 - b);
}

// Alternar LED (para piscar)
void toggleLED(int r, int g, int b) {
  static bool state = false;
  if (state) {
    setLED(r, g, b);
  } else {
    setLED(0, 0, 0);
  }
  state = !state;
}

// ===== COMANDOS DE DEBUG VIA SERIAL =====
void serialEvent() {
  if (Serial.available()) {
    char cmd = Serial.read();
    
    switch (cmd) {
      case 'd': // Toggle debug
        debugMode = !debugMode;
        Serial.print("Debug: ");
        Serial.println(debugMode ? "ON" : "OFF");
        break;
        
      case 's': // Status
        printStatus();
        break;
        
      case 'r': // Reset conexão
        if (useWiFi) {
          client.stop();
          connectToDevBoard();
        }
        break;
        
      case 'h': // Help
        Serial.println("Comandos:");
        Serial.println("d - Toggle debug");
        Serial.println("s - Mostrar status");
        Serial.println("r - Reset conexão");
        Serial.println("h - Help");
        break;
    }
  }
}

void printStatus() {
  Serial.println("=== STATUS ===");
  Serial.print("Modo: ");
  Serial.println(useWiFi ? "WiFi" : "Serial");
  
  if (useWiFi) {
    Serial.print("WiFi: ");
    Serial.println(WiFi.status() == WL_CONNECTED ? "Conectado" : "Desconectado");
    Serial.print("IP: ");
    Serial.println(WiFi.localIP());
    Serial.print("Dev Board: ");
    Serial.println(client.connected() ? "Conectado" : "Desconectado");
  }
  
  Serial.print("Taxa amostragem: ");
  Serial.print(sampleRate);
  Serial.println(" Hz");
  Serial.print("Debug: ");
  Serial.println(debugMode ? "ON" : "OFF");
  Serial.println("============");
}