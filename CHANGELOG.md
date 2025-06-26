# Changelog

## [1.1.0] - 2025-06-26

### 🆕 Suporte a Arduino Nano 2040 Connect como Microfone
- Adicionada opção de usar dois Arduinos Nano 2040 Connect como microfones remotos.
- Novo diretório `Sytem-arduino/` com:
  - `arduino-microphone.ino`: código para Arduino capturar e enviar áudio.
  - `voice_assistent_arduino.py`: recebe/processa áudio do Arduino (WiFi ou Serial).
  - `setup_arduino.sh` e `requirements_arduino.txt`: configuração e dependências específicas.
- Integração com Dev Board mantida para o processamento de voz.

## [1.0.0] - 2025-06-26

### 🚗 Projeto iniciado
- Estrutura inicial do sistema de assistente de voz para carro.
- Scripts principais:
  - `setup.sh`: configuração completa do ambiente e dependências.
  - `run.sh`: inicialização rápida do assistente.
  - `requirements.txt`: dependências Python.
  - `voice_assistant.py`: código principal do assistente de voz.

---
Este changelog reflete as principais mudanças e opções do projeto.
