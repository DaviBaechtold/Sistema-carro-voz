#!/bin/bash

# Script automatizado para deploy no Google Dev Board (AA1)
# Execute este script NO DEV BOARD após clonar o repositório

set -e  # Parar se houver erro

echo "🚗 Deploy para Google Dev Board (AA1)"
echo "====================================="

# Verificar se está rodando no Dev Board
if ! grep -q "Mendel" /etc/os-release 2>/dev/null; then
    echo "⚠️  Este script deve ser executado no Google Dev Board"
    echo "Execute no Dev Board: ssh mendel@IP_DO_DEVBOARD"
    exit 1
fi

echo "✅ Dev Board detectado!"

# Função para verificar comando
check_command() {
    if command -v $1 &> /dev/null; then
        echo "✅ $1 disponível"
    else
        echo "❌ $1 não encontrado - instalando..."
        return 1
    fi
}

# Atualizar sistema
echo "📦 Atualizando sistema..."
sudo apt update

# Instalar dependências específicas do Dev Board
echo "🔧 Instalando dependências do Dev Board..."
sudo apt install -y python3-pip python3-dev python3-venv
sudo apt install -y portaudio19-dev alsa-utils pulseaudio
sudo apt install -y git curl wget

# Configurar permissões de áudio
echo "🔊 Configurando permissões de áudio..."
sudo usermod -a -G audio,plugdev $USER

# Configurar ambiente Python
echo "🐍 Configurando ambiente Python..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Configurar áudio para microfone USB
echo "🎤 Configurando áudio para microfone USB..."
sudo tee /etc/asound.conf > /dev/null << EOF
pcm.!default {
    type asym
    playback.pcm "speaker"
    capture.pcm "microphone"
}

pcm.microphone {
    type plug
    slave {
        pcm "hw:1,0"
    }
}

pcm.speaker {
    type plug
    slave {
        pcm "hw:0,0"
    }
}

ctl.!default {
    type hw
    card 0
}
EOF

# Testar microfone
echo "🧪 Testando configuração de áudio..."
if arecord -l | grep -q "USB"; then
    echo "✅ Microfone USB detectado"
else
    echo "⚠️  Microfone USB não detectado - verifique conexão"
fi

# Criar script de inicialização otimizado para carro
echo "🚀 Criando script de inicialização..."
cat > start_car_assistant.sh << 'EOF'
#!/bin/bash

# Script otimizado para inicialização no carro
echo "🚗 Iniciando Assistente de Voz para Carro..."

# Aguardar estabilização do sistema (importante no carro)
sleep 30

# Verificar conectividade (WiFi do carro ou hotspot)
echo "📡 Verificando conectividade..."
timeout=60
while [ $timeout -gt 0 ]; do
    if ping -c 1 8.8.8.8 &> /dev/null; then
        echo "✅ Conectividade OK"
        break
    fi
    echo "⏳ Aguardando conexão... ($timeout segundos restantes)"
    sleep 5
    timeout=$((timeout-5))
done

if [ $timeout -le 0 ]; then
    echo "⚠️  Sem conectividade - usando modo offline limitado"
fi

# Configurar CPU para performance (importante para reconhecimento de voz)
echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor > /dev/null

# Verificar temperatura
temp=$(cat /sys/class/thermal/thermal_zone0/temp)
temp_celsius=$((temp/1000))
echo "🌡️  Temperatura: ${temp_celsius}°C"

if [ $temp_celsius -gt 70 ]; then
    echo "⚠️  Temperatura alta - reduzindo performance"
    echo powersave | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor > /dev/null
fi

# Iniciar assistente
cd /home/mendel/Sistema-carro-voz
source venv/bin/activate
python3 voice_assistant.py
EOF

chmod +x start_car_assistant.sh

# Criar serviço systemd
echo "⚙️  Criando serviço de auto-inicialização..."
sudo tee /etc/systemd/system/voice-assistant-car.service > /dev/null << EOF
[Unit]
Description=Assistente de Voz para Carro (Dev Board)
After=network.target sound.target
Wants=network.target

[Service]
Type=simple
User=mendel
Group=audio
WorkingDirectory=/home/mendel/Sistema-carro-voz
Environment=PATH=/home/mendel/Sistema-carro-voz/venv/bin:/usr/local/bin:/usr/bin:/bin
ExecStart=/home/mendel/Sistema-carro-voz/start_car_assistant.sh
Restart=always
RestartSec=30
StandardOutput=journal
StandardError=journal
TimeoutStartSec=120

[Install]
WantedBy=multi-user.target
EOF

# Configurar logrotate para evitar enchimento do SD card
echo "📝 Configurando rotação de logs..."
sudo tee /etc/logrotate.d/voice-assistant > /dev/null << EOF
/var/log/voice-assistant.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 644 mendel audio
}
EOF

# Habilitar serviço
echo "🔄 Habilitando auto-inicialização..."
sudo systemctl daemon-reload
sudo systemctl enable voice-assistant-car.service

# Criar script de monitoramento
echo "📊 Criando script de monitoramento..."
cat > monitor_system.sh << 'EOF'
#!/bin/bash

echo "🚗 Status do Assistente de Voz no Carro"
echo "======================================"

# Status do serviço
echo "📋 Status do Serviço:"
sudo systemctl status voice-assistant-car.service --no-pager -l

echo ""
echo "🔊 Dispositivos de Áudio:"
arecord -l | grep -E "(card|USB)" || echo "Nenhum dispositivo encontrado"

echo ""
echo "🌡️  Temperatura do Sistema:"
temp=$(cat /sys/class/thermal/thermal_zone0/temp)
echo "Temperatura: $((temp/1000))°C"

echo ""
echo "💾 Uso do SD Card:"
df -h / | tail -1

echo ""
echo "🧠 Uso de Memória:"
free -h

echo ""
echo "📶 Conectividade:"
if ping -c 1 8.8.8.8 &> /dev/null; then
    echo "✅ Internet OK"
else
    echo "❌ Sem internet"
fi

echo ""
echo "📝 Últimos logs (últimas 10 linhas):"
sudo journalctl -u voice-assistant-car.service --no-pager -n 10
EOF

chmod +x monitor_system.sh

# Testar instalação
echo ""
echo "🧪 Testando instalação..."
source venv/bin/activate

# Verificar dependências Python
python3 -c "
try:
    import speech_recognition
    import pyttsx3
    import pyaudio
    print('✅ Todas as dependências Python estão OK')
except ImportError as e:
    print(f'❌ Erro na dependência: {e}')
"

echo ""
echo "✅ Deploy concluído com sucesso!"
echo ""
echo "📋 Próximos passos:"
echo "1. Reinicie o Dev Board: sudo reboot"
echo "2. Conecte o microfone USB M-305"
echo "3. O assistente iniciará automaticamente após o boot"
echo "4. Monitore com: ./monitor_system.sh"
echo "5. Ver logs: sudo journalctl -u voice-assistant-car.service -f"
echo ""
echo "🔧 Para testar manualmente antes do reboot:"
echo "./setup.sh  # Opção 3 para testar"
echo "🚀 Para iniciar manualmente:"
echo "./start_car_assistant.sh"
