# 📟 Deploy Detalhado - Google Dev Board (AA1)

Guia completo de instalação manual do Assistente de Voz no Google Dev Board (AA1).

> 💡 **Para instalação automática, use:** `./install.sh`  
> Este guia é para instalação manual ou entendimento detalhado do processo.

## 🎯 Visão Geral

O Google Dev Board (AA1) é ideal para este projeto pois:
- ✅ Linux embarcado (Mendel Linux baseado em Debian)
- ✅ Edge TPU para IA/ML (futuras melhorias)
- ✅ GPIO para integração com sistemas do carro
- ✅ WiFi/Bluetooth integrados
- ✅ Baixo consumo de energia
- ✅ Tamanho compacto para instalação no carro

## 🔧 Pré-requisitos

### Hardware Necessário
- Google Coral Dev Board (AA1)
- Microfone USB M-305 ou similar
- Cartão microSD (32GB+ recomendado)
- Fonte 12V para carro → 5V/3A USB-C
- Caixa de som ou conexão com sistema de áudio do carro

### Software
- Mendel Linux (já vem no Dev Board)
- Acesso SSH ao Dev Board
- Conexão WiFi configurada

## 🚀 Instalação Automática (Recomendada)

### 1. Conectar ao Dev Board
```bash
ssh mendel@IP_DO_DEVBOARD
```

### 2. Clonar e instalar
```bash
git clone https://github.com/DaviBaechtold/Sistema-carro-voz.git
cd Sistema-carro-voz/devboard
chmod +x install.sh
./install.sh
```

### 3. Reiniciar
```bash
sudo reboot
```

O assistente iniciará automaticamente após o reboot.

## 🔧 Instalação Manual (Passo a Passo)

### 1. Acesso Inicial
```bash
# Conectar via SSH (substitua pelo IP do seu Dev Board)
ssh mendel@192.168.1.100

# Atualizar sistema
sudo apt update && sudo apt upgrade -y
```

### 2. Clonar e Configurar
```bash
# Clonar repositório
git clone https://github.com/DaviBaechtold/Sistema-carro-voz.git
cd Sistema-carro-voz

# Dar permissões
chmod +x setup.sh run.sh

# Configuração completa
./setup.sh
# Escolha opção 1 para configuração completa
```

### 3. Configuração Específica do Dev Board
```bash
# Configurar permissões de áudio
sudo usermod -a -G audio mendel

# Instalar dependências específicas do ARM64
sudo apt install -y python3-pyaudio portaudio19-dev

# Configurar microfone USB
sudo nano /etc/asound.conf
```

### 4. Teste de Hardware
```bash
# Testar microfone
arecord -l  # Listar dispositivos
arecord -D hw:1,0 -d 3 test.wav  # Gravar teste
aplay test.wav  # Reproduzir teste

# Testar sistema completo
./setup.sh
# Escolha opção 3 para testar
```

## ⚙️ Configuração para Auto-inicialização

### Criar Serviço Systemd
```bash
sudo nano /etc/systemd/system/voice-assistant.service
```

Conteúdo do arquivo:
```ini
[Unit]
Description=Assistente de Voz para Carro
After=network.target sound.target
Wants=network.target

[Service]
Type=simple
User=mendel
Group=audio
WorkingDirectory=/home/mendel/Sistema-carro-voz
Environment=PATH=/home/mendel/Sistema-carro-voz/venv/bin:/usr/local/bin:/usr/bin:/bin
ExecStart=/home/mendel/Sistema-carro-voz/venv/bin/python voice_assistant.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

### Ativar Serviço
```bash
# Habilitar serviço
sudo systemctl enable voice-assistant.service

# Iniciar serviço
sudo systemctl start voice-assistant.service

# Verificar status
sudo systemctl status voice-assistant.service

# Ver logs
sudo journalctl -u voice-assistant.service -f
```

## 🔊 Configuração de Áudio

### Arquivo /etc/asound.conf
```
pcm.!default {
    type asym
    playback.pcm "speaker"
    capture.pcm "microphone"
}

pcm.microphone {
    type plug
    slave {
        pcm "hw:1,0"  # Microfone USB
    }
}

pcm.speaker {
    type plug
    slave {
        pcm "hw:0,0"  # Saída de áudio padrão
    }
}
```

## 🔌 Integração com o Carro

### Conexão de Energia
```bash
# Criar script de inicialização que aguarda estabilização
sudo nano /home/mendel/start_assistant.sh
```

Conteúdo:
```bash
#!/bin/bash
# Aguardar sistema estabilizar (30 segundos após boot)
sleep 30

# Verificar conectividade
while ! ping -c 1 google.com &> /dev/null; do
    sleep 5
done

# Iniciar assistente
cd /home/mendel/Sistema-carro-voz
./run.sh
```

### GPIO para Integração (Futuro)
```python
# Exemplo de integração com GPIO do carro
import gpiozero

# Botão físico para ativar assistente
button = gpiozero.Button(2)
led = gpiozero.LED(18)

def on_button_press():
    led.on()
    # Ativar assistente por comando
    assistant.force_wake()

button.when_pressed = on_button_press
```

## 📱 Configuração WiFi Hotspot (Opcional)

Para configuração remota sem depender do WiFi do carro:

```bash
# Instalar hostapd
sudo apt install -y hostapd dnsmasq

# Configurar como hotspot
sudo nano /etc/hostapd/hostapd.conf
```

## 🛠️ Troubleshooting Dev Board

### Problemas Comuns

**1. Microfone não detectado:**
```bash
# Verificar dispositivos USB
lsusb
# Verificar dispositivos de áudio
arecord -l
```

**2. Erro de permissão de áudio:**
```bash
# Adicionar usuário aos grupos necessários
sudo usermod -a -G audio,plugdev mendel
```

**3. Problemas de conectividade:**
```bash
# Verificar WiFi
iwconfig
# Reiniciar rede
sudo systemctl restart networking
```

**4. Problemas de desempenho:**
```bash
# Verificar CPU e memória
htop
# Verificar temperatura
cat /sys/class/thermal/thermal_zone0/temp
```

## 🔋 Otimizações para Uso no Carro

### Economia de Energia
```bash
# Configurar CPU governor para economia
echo 'performance' | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
```

### Configurações de Rede
```bash
# Configurar WiFi para reconectar automaticamente
sudo nano /etc/wpa_supplicant/wpa_supplicant.conf
```

### Logs Rotativos
```bash
# Configurar logrotate para evitar enchimento do SD
sudo nano /etc/logrotate.d/voice-assistant
```

## 📊 Monitoramento Remoto

### Acesso SSH Remoto
```bash
# Configurar SSH keys para acesso sem senha
ssh-keygen -t rsa
ssh-copy-id mendel@192.168.1.100
```

### Script de Status
```bash
# Criar script para verificar status do sistema
./check_system_status.sh
```

## 🚀 Scripts de Deploy Automatizado

Todos os comandos acima foram automatizados nos scripts:
- `deploy_to_devboard.sh` - Deploy automático
- `setup_autostart.sh` - Configurar auto-inicialização  
- `monitor_system.sh` - Monitoramento

## 📞 Suporte Específico Dev Board

Para problemas específicos do Google Dev Board:
- [Documentação Oficial Coral](https://coral.ai/docs/dev-board/get-started/)
- [Fórum Coral Community](https://groups.google.com/forum/#!forum/coral-support)
- Issues do projeto no GitHub
