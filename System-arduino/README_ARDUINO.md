# 🎙️ Assistente de Voz - Arduino como Microfone

Sistema de assistente de voz usando Arduino Nano 2040 Connect como microfone remoto para o Google Dev Board.

## 📋 Requisitos

### Hardware
- Google Dev Board (AA1)
- Arduino Nano RP2040 Connect
- Rede WiFi (para modo WiFi)
- Cabo USB (para modo Serial)

### Software
- Arduino IDE 2.0+
- Python 3.7.3 no Dev Board
- Bibliotecas Arduino: PDM, WiFiNINA

## 🔌 Arquitetura do Sistema

```
[Arduino Nano] ---(WiFi/Serial)---> [Dev Board] ---> [Google Speech API]
     PDM Mic                          Processing         Voice Recognition
```

## 🚀 Instalação

### 1. Preparar o Arduino

**No Arduino IDE:**

1. **Instale as bibliotecas:**
   - Tools → Manage Libraries
   - Buscar e instalar: `PDM` e `WiFiNINA`

2. **Configure o código Arduino:**
```cpp
// Editar no arduino_microphone.ino:
const char* ssid = "SEU_WIFI";
const char* password = "SUA_SENHA";
const char* devboard_ip = "IP_DO_DEVBOARD";
```

3. **Upload para o Arduino:**
   - Selecione Board: Arduino Nano RP2040 Connect
   - Selecione a porta correta
   - Upload do sketch

### 2. Preparar o Dev Board

**Via SSH no Dev Board:**

```bash
# Conectar ao Dev Board
ssh mendel@IP_DO_DEVBOARD

# Clonar repositório
git clone https://github.com/DaviBaechtold/Sistema-carro-voz.git
cd Sistema-carro-voz

# Dar permissão aos scripts
chmod +x setup_arduino.sh

# Executar setup
./setup_arduino.sh
```

**No menu do setup:**
1. Escolha **1** - Configuração inicial completa
2. Escolha **6** - Ver IP do Dev Board (anote este IP)
3. Escolha **3** - Testar conexão Arduino

## 🎯 Modos de Operação

### Modo WiFi (Recomendado)

**Vantagens:**
- Sem fios
- Arduino pode ficar distante
- Menor latência

**Configuração:**
1. Arduino e Dev Board na mesma rede WiFi
2. Configurar IP correto no código Arduino
3. Executar no Dev Board:
```bash
./setup_arduino.sh
# Escolha 4 - Executar assistente (WiFi)
```

### Modo Serial USB

**Vantagens:**
- Não precisa WiFi
- Conexão mais estável
- Alimentação pelo USB

**Configuração:**
1. Conecte Arduino via USB ao Dev Board
2. Executar no Dev Board:
```bash
./setup_arduino.sh
# Escolha 5 - Executar assistente (Serial)
# Digite a porta (ex: /dev/ttyUSB0)
```

## 🎤 Como Usar

### Comandos de Voz

Mesmo formato do sistema USB:
- `"Assistente, tocar música"`
- `"OK Google, ligar para João"`
- `"Carro, navegar para casa"`

### LED de Status no Arduino

- **Azul piscando**: Conectando WiFi
- **Verde fixo**: Conectado e pronto
- **Vermelho**: Erro de conexão

## 🔧 Configuração Avançada

### Ajustar Taxa de Amostragem

No Arduino:
```cpp
const int sampleRate = 16000; // Pode testar 8000 para menos dados
```

### Buffer de Áudio

No Arduino:
```cpp
short sampleBuffer[512]; // Aumentar para 1024 se áudio cortado
```

### Timeout de Gravação

No Python:
```python
time.sleep(5) # Aumentar para comandos mais longos
```

## 🔍 Solução de Problemas

### Arduino não conecta (WiFi)

1. **Verificar credenciais WiFi:**
```cpp
const char* ssid = "SEU_WIFI";  // Nome correto?
const char* password = "SUA_SENHA"; // Senha correta?
```

2. **Verificar IP do Dev Board:**
```bash
# No Dev Board
hostname -I
```

3. **Monitor Serial Arduino:**
```
Tools → Serial Monitor (115200 baud)
Verificar mensagens de erro
```

### Arduino não conecta (Serial)

1. **Verificar porta:**
```bash
# No Dev Board
ls /dev/tty*
# Procurar por ttyUSB0, ttyACM0, etc
```

2. **Permissões:**
```bash
sudo usermod -a -G dialout $USER
# Fazer logout e login
```

### Áudio não reconhecido

1. **Testar microfone PDM:**
```cpp
// Adicionar no loop() do Arduino:
Serial.println(samplesRead); // Deve mostrar números
```

2. **Aumentar volume de entrada:**
```python
# No Python, ajustar ganho
audio_data = audio_data * 2  # Amplificar
```

## 📊 Monitoramento

### Logs do Python
```bash
# Ver saída em tempo real
./setup_arduino.sh
# Escolha 4 ou 5 para executar
```

### Monitor Serial Arduino
- Arduino IDE → Tools → Serial Monitor
- Baud rate: 115200
- Mostra status da conexão

### Teste de Latência
```python
# Adicionar timestamps no Python
print(f"Início gravação: {time.time()}")
# ... código ...
print(f"Fim reconhecimento: {time.time()}")
```

## 🚦 Inicialização Automática

### Serviço no Dev Board

```bash
sudo nano /etc/systemd/system/voice-arduino.service
```

```ini
[Unit]
Description=Voice Assistant Arduino
After=network.target

[Service]
Type=simple
User=mendel
WorkingDirectory=/home/mendel/Sistema-carro-voz
ExecStart=/home/mendel/Sistema-carro-voz/venv/bin/python /home/mendel/Sistema-carro-voz/voice_assistant_arduino.py
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable voice-arduino
sudo systemctl start voice-arduino
```

### Auto-start Arduino

O Arduino inicia automaticamente ao receber energia. Certifique-se que:
1. WiFi está sempre disponível
2. IP do Dev Board não muda (IP fixo recomendado)

## 📱 Múltiplos Arduinos

Para usar vários Arduinos:

1. **Diferentes portas:**
```python
WIFI_PORT = 5555  # Arduino 1
WIFI_PORT2 = 5556 # Arduino 2
```

2. **Thread por Arduino:**
```python
arduino1 = ArduinoMicrophone(port=5555)
arduino2 = ArduinoMicrophone(port=5556)
```

## 🛠️ Desenvolvimento

### Debug Mode

No Arduino:
```cpp
#define DEBUG 1  // Ativar prints de debug
```

No Python:
```python
DEBUG = True  # Mais logs
```

### Salvar áudio para análise
```python
# Salvar WAV para debug
with open(f"debug_{time.time()}.wav", "wb") as f:
    f.write(audio_data)
```