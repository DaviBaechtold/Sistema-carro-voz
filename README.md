# 🚗 Assistente de Voz para Carro - Google Dev Board

Sistema de assistente de voz em português brasileiro para uso automotivo, desenvolvido para Google Dev Board (AA1).

## 📦 Sistemas Disponíveis

### 1. Sistema com Microfone USB (M-305)
- **Uso:** Microfone USB conectado diretamente ao Dev Board
- **Vantagem:** Configuração simples, plug-and-play
- **Ideal para:** Instalação fixa no carro
- **Arquivos:** `System-mic/voice_assistant.py`, `System-mic/setup.sh`, `System-mic/run.sh`, `System-mic/requirements.txt`

### 2. Sistema com Arduino como Microfone
- **Uso:** Arduino Nano RP2040 captura áudio e envia ao Dev Board
- **Vantagem:** Microfone remoto sem fio (WiFi) ou USB
- **Ideal para:** Flexibilidade de posicionamento, múltiplos microfones
- **Arquivos:** `System-arduino/voice_assistant_arduino.py`, `System-arduino/setup_arduino.sh`, `System-arduino/arduino-microphone.ino`, `System-arduino/requirements_arduino.txt`

## 🎯 Funcionalidades

Ambos os sistemas oferecem:

- ✅ Reconhecimento de voz em português brasileiro
- ✅ Wake words: "Assistente", "OK Google", "Hey Google", "Carro"
- ✅ Comandos para: chamadas, música, navegação, mensagens
- ✅ Síntese de voz natural em português
- ✅ Auto-inicialização com o sistema

## 🚀 Início Rápido

### 1. Configurando o PC para acessar o Dev Board

Antes de instalar o sistema, conecte o Dev Board à sua rede e configure o acesso SSH pelo seu computador:

- Siga o guia oficial: [Coral Dev Board - Getting Started](https://coral.ai/docs/dev-board/get-started/#connect-internet)
- Resumo dos passos:
  1. Conecte o Dev Board ao PC via USB-C.
  2. Instale drivers se necessário (veja o guia).
  3. Acesse o console serial (screen, PuTTY, minicom, etc) para configurar WiFi ou Ethernet.
  4. Descubra o IP do Dev Board (`hostname -I` no terminal do Dev Board).
  5. Teste o acesso SSH:
     ```bash
     ssh mendel@IP_DO_DEVBOARD
     ```

### 2. Instalação do Sistema USB (pasta System-mic)
```bash
ssh mendel@IP_DO_DEVBOARD
git clone https://github.com/DaviBaechtold/Sistema-carro-voz.git
cd Sistema-carro-voz/System-mic
chmod +x setup.sh
./setup.sh  # Escolha opção 1
```

### 3. Instalação do Sistema Arduino (pasta System-arduino)
```bash
# No Dev Board
cd Sistema-carro-voz/System-arduino
chmod +x setup_arduino.sh
./setup_arduino.sh  # Escolha opção 1

# No Arduino IDE
# Upload do sketch arduino-microphone.ino
```

## 📋 Comandos de Exemplo

- "Assistente, tocar música"
- "OK Google, ligar para João"
- "Carro, navegar para casa"
- "Hey Google, aumentar volume"

## 🔧 Requisitos

- Google Dev Board (AA1)
- Microfone USB M-305 **OU** Arduino Nano RP2040 Connect
- Conexão com internet
- Python 3.7.3+

## 📖 Documentação Detalhada

- `System-mic/README_USB.md` - Guia completo sistema USB
- `System-arduino/README_ARDUINO.md` - Guia completo sistema Arduino
- Wiki do projeto para tutoriais avançados

## 📱 Escolhendo o Sistema

| Característica | USB M-305 | Arduino |
|----------------|-----------|---------|
| Instalação | ⭐⭐⭐⭐⭐ Muito fácil | ⭐⭐⭐ Média |
| Custo | ⭐⭐⭐⭐ Baixo (~$10) | ⭐⭐ Médio (~$40) |
| Flexibilidade | ⭐⭐ Fixa | ⭐⭐⭐⭐⭐ Remota |
| Qualidade | ⭐⭐⭐⭐ Boa | ⭐⭐⭐ Boa |
| Múltiplos mics | ❌ Não | ✅ Sim |

## 📄 Licença

MIT License - veja LICENSE para detalhes.