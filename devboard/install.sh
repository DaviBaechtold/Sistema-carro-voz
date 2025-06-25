#!/bin/bash

# Script consolidado de instalação para Google Dev Board (AA1)
# Combina instalação, configuração de rede e setup do serviço

set -e

echo "🚗 Instalação Completa - Assistente de Voz (Dev Board AA1)"
echo "========================================================="

# Verificar se está no Dev Board
if ! grep -q "Mendel" /etc/os-release 2>/dev/null; then
    echo "❌ Este script deve ser executado no Google Dev Board"
    echo "Conecte-se via SSH: ssh mendel@IP_DO_DEVBOARD"
    exit 1
fi

echo "✅ Google Dev Board detectado!"

# Verificar se já foi instalado
if systemctl is-active --quiet voice-assistant-car 2>/dev/null; then
    echo "⚠️  Assistente já está instalado e rodando"
    read -p "Deseja reinstalar? (y/N): " confirm
    if [[ ! $confirm =~ ^[Yy]$ ]]; then
        echo "Instalação cancelada"
        exit 0
    fi
    sudo systemctl stop voice-assistant-car
fi

# Funções auxiliares
log_step() {
    echo ""
    echo "📋 $1"
    echo "$(printf '=%.0s' {1..50})"
}

check_hardware() {
    log_step "Verificando hardware"
    
    # Verificar microfone USB
    if lsusb | grep -i "audio\|microphone\|sound" > /dev/null; then
        echo "✅ Dispositivo de áudio USB detectado"
    else
        echo "⚠️  Microfone USB não detectado - conecte o M-305"
    fi
    
    # Verificar temperatura
    temp=$(cat /sys/class/thermal/thermal_zone0/temp 2>/dev/null || echo "0")
    temp_c=$((temp/1000))
    echo "🌡️  Temperatura atual: ${temp_c}°C"
    
    if [ $temp_c -gt 70 ]; then
        echo "⚠️  Temperatura alta - aguarde esfriar antes de continuar"
        exit 1
    fi
}

install_dependencies() {
    log_step "Instalando dependências"
    
    # Atualizar sistema
    sudo apt update
    
    # Instalar pacotes essenciais
    sudo apt install -y python3-pip python3-dev python3-venv
    sudo apt install -y portaudio19-dev alsa-utils pulseaudio
    sudo apt install -y git curl wget htop
    
    # Instalar vozes TTS
    sudo apt install -y espeak espeak-data espeak-data-pt
    sudo apt install -y festival flite
    
    # Tentar instalar vozes brasileiras (pode falhar em alguns sistemas)
    sudo apt install -y festvox-br-cid mbrola mbrola-br1 mbrola-br3 2>/dev/null || {
        echo "⚠️  Algumas vozes brasileiras não estão disponíveis nos repositórios"
    }
    
    echo "✅ Dependências instaladas"
}

setup_python_env() {
    log_step "Configurando ambiente Python"
    
    # Navegar para diretório pai (fora da pasta devboard)
    cd ..
    
    # Criar ambiente virtual se não existir
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    
    # Ativar e instalar dependências
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    
    echo "✅ Ambiente Python configurado"
}

configure_audio() {
    log_step "Configurando áudio"
    
    # Configurar permissões
    sudo usermod -a -G audio,plugdev $USER
    
    # Criar configuração ALSA
    sudo tee /etc/asound.conf > /dev/null << 'EOF'
# Configuração otimizada para assistente de voz no carro
pcm.!default {
    type asym
    playback.pcm "car_speaker"
    capture.pcm "car_microphone"
}

pcm.car_microphone {
    type plug
    slave {
        pcm "hw:1,0"  # Microfone USB (M-305)
        rate 16000    # Taxa otimizada para reconhecimento
        channels 1    # Mono
    }
}

pcm.car_speaker {
    type plug
    slave {
        pcm "hw:0,0"  # Saída padrão
        rate 44100
        channels 2
    }
}

ctl.!default {
    type hw
    card 0
}
EOF
    
    echo "✅ Áudio configurado"
}

setup_network() {
    log_step "Configurando rede"
    
    echo "Configuração de rede:"
    echo "1) Configurar WiFi"
    echo "2) Manter configuração atual"
    echo "3) Configurar mais tarde"
    read -p "Escolha (1-3): " net_choice
    
    case $net_choice in
        1)
            setup_wifi
            ;;
        2)
            echo "Mantendo configuração atual"
            ;;
        3)
            echo "Configure manualmente depois com: ./manage.sh"
            ;;
    esac
}

setup_wifi() {
    read -p "Nome da rede WiFi (SSID): " ssid
    read -s -p "Senha da rede WiFi: " password
    echo
    
    # Backup da configuração atual
    sudo cp /etc/wpa_supplicant/wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicant.conf.backup
    
    # Adicionar nova rede
    sudo tee -a /etc/wpa_supplicant/wpa_supplicant.conf > /dev/null << EOF

network={
    ssid="$ssid"
    psk="$password"
    key_mgmt=WPA-PSK
    priority=10
}
EOF
    
    # Reiniciar rede
    sudo systemctl restart networking
    sleep 5
    
    # Testar conectividade
    if ping -c 3 8.8.8.8 > /dev/null 2>&1; then
        echo "✅ WiFi configurado com sucesso"
    else
        echo "❌ Falha na configuração WiFi"
        echo "Configure manualmente depois"
    fi
}

create_service() {
    log_step "Criando serviço systemd"
    
    # Criar script de inicialização
    cat > ../start_car_assistant.sh << 'EOF'
#!/bin/bash

# Script de inicialização para carro
echo "🚗 Iniciando Assistente de Voz..."

# Aguardar estabilização (importante no carro)
sleep 30

# Verificar conectividade com timeout
echo "📡 Verificando conectividade..."
timeout=60
while [ $timeout -gt 0 ]; do
    if ping -c 1 8.8.8.8 &> /dev/null; then
        echo "✅ Conectado"
        break
    fi
    echo "⏳ Aguardando conexão... ($timeout s)"
    sleep 5
    timeout=$((timeout-5))
done

# Configurar CPU para performance
echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor > /dev/null 2>&1 || true

# Verificar temperatura
temp=$(cat /sys/class/thermal/thermal_zone0/temp 2>/dev/null || echo "0")
temp_c=$((temp/1000))
echo "🌡️  Temperatura: ${temp_c}°C"

if [ $temp_c -gt 75 ]; then
    echo "⚠️  Temperatura alta - modo de economia"
    echo powersave | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor > /dev/null 2>&1 || true
fi

# Navegar para diretório e ativar ambiente
cd /home/mendel/Sistema-carro-voz
source venv/bin/activate

# Iniciar assistente (versão Dev Board se disponível)
if [ -f "devboard/voice_assistant_devboard.py" ]; then
    python3 devboard/voice_assistant_devboard.py
else
    python3 voice_assistant.py
fi
EOF
    
    chmod +x ../start_car_assistant.sh
    
    # Criar serviço systemd
    sudo tee /etc/systemd/system/voice-assistant-car.service > /dev/null << 'EOF'
[Unit]
Description=Assistente de Voz para Carro (Google Dev Board AA1)
After=network.target sound.target graphical-session.target
Wants=network.target

[Service]
Type=simple
User=mendel
Group=audio
WorkingDirectory=/home/mendel/Sistema-carro-voz
Environment=HOME=/home/mendel
Environment=XDG_RUNTIME_DIR=/run/user/1000
ExecStart=/home/mendel/Sistema-carro-voz/start_car_assistant.sh
Restart=always
RestartSec=30
StandardOutput=journal
StandardError=journal
TimeoutStartSec=180
KillMode=mixed
KillSignal=SIGTERM

[Install]
WantedBy=multi-user.target
EOF
    
    # Configurar logrotate
    sudo tee /etc/logrotate.d/voice-assistant > /dev/null << 'EOF'
/var/log/voice-assistant.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 644 mendel audio
    postrotate
        systemctl reload voice-assistant-car.service 2>/dev/null || true
    endscript
}
EOF
    
    # Habilitar serviço
    sudo systemctl daemon-reload
    sudo systemctl enable voice-assistant-car.service
    
    echo "✅ Serviço criado e habilitado"
}

test_installation() {
    log_step "Testando instalação"
    
    # Testar ambiente Python
    cd ..
    source venv/bin/activate
    
    echo "🐍 Testando dependências Python..."
    python3 -c "
try:
    import speech_recognition
    import pyttsx3
    import pyaudio
    print('✅ Dependências Python OK')
except ImportError as e:
    print(f'❌ Erro: {e}')
    exit(1)
"
    
    # Testar dispositivos de áudio
    echo "🎤 Testando áudio..."
    if arecord -l | grep -i "usb\|card 1" > /dev/null; then
        echo "✅ Microfone USB detectado"
    else
        echo "⚠️  Microfone USB não encontrado"
    fi
    
    # Testar TTS
    echo "🔊 Testando síntese de voz..."
    if command -v espeak > /dev/null; then
        echo "✅ TTS disponível"
    else
        echo "⚠️  TTS não encontrado"
    fi
    
    echo "✅ Testes concluídos"
}

create_management_script() {
    log_step "Criando script de gerenciamento"
    
    cat > manage.sh << 'EOF'
#!/bin/bash

# Script de gerenciamento local do assistente no Dev Board

echo "🚗 Gerenciamento - Assistente de Voz (Dev Board)"
echo "==============================================="

show_menu() {
    echo ""
    echo "Escolha uma opção:"
    echo "1) Status do sistema"
    echo "2) Iniciar assistente"
    echo "3) Parar assistente" 
    echo "4) Reiniciar assistente"
    echo "5) Ver logs em tempo real"
    echo "6) Configurar WiFi"
    echo "7) Verificar temperatura"
    echo "8) Testar microfone"
    echo "9) Atualizar código"
    echo "0) Sair"
    echo
    read -p "Digite sua escolha (0-9): " choice
}

while true; do
    show_menu
    
    case $choice in
        1)
            echo "📊 Status do Sistema:"
            echo "Serviço: $(systemctl is-active voice-assistant-car.service)"
            echo "Temperatura: $(cat /sys/class/thermal/thermal_zone0/temp | awk '{print $1/1000}')°C"
            echo "Memória: $(free -h | awk 'NR==2{print $3"/"$2}')"
            echo "SD Card: $(df -h / | awk 'NR==2{print $5" usado"}')"
            sudo systemctl status voice-assistant-car.service --no-pager -l
            ;;
        2)
            echo "🚀 Iniciando assistente..."
            sudo systemctl start voice-assistant-car.service
            ;;
        3)
            echo "🛑 Parando assistente..."
            sudo systemctl stop voice-assistant-car.service
            ;;
        4)
            echo "🔄 Reiniciando assistente..."
            sudo systemctl restart voice-assistant-car.service
            ;;
        5)
            echo "📝 Logs em tempo real (Ctrl+C para sair):"
            sudo journalctl -u voice-assistant-car.service -f
            ;;
        6)
            echo "📶 Configurando WiFi..."
            read -p "SSID: " ssid
            read -s -p "Senha: " password
            echo
            sudo tee -a /etc/wpa_supplicant/wpa_supplicant.conf > /dev/null << WIFI_EOF

network={
    ssid="$ssid"
    psk="$password"
    key_mgmt=WPA-PSK
    priority=5
}
WIFI_EOF
            sudo systemctl restart networking
            ;;
        7)
            temp=$(cat /sys/class/thermal/thermal_zone0/temp)
            temp_c=$((temp/1000))
            echo "🌡️  Temperatura: ${temp_c}°C"
            if [ $temp_c -gt 70 ]; then
                echo "⚠️  Temperatura alta!"
            else
                echo "✅ Temperatura normal"
            fi
            ;;
        8)
            echo "🎤 Testando microfone..."
            arecord -l
            echo "Gravando 3 segundos de teste..."
            arecord -d 3 -f cd test.wav 2>/dev/null && aplay test.wav 2>/dev/null
            rm -f test.wav
            ;;
        9)
            echo "🔄 Atualizando código..."
            cd ..
            git pull origin main
            sudo systemctl restart voice-assistant-car.service
            ;;
        0)
            exit 0
            ;;
        *)
            echo "Opção inválida"
            ;;
    esac
    
    echo
    read -p "Pressione Enter para continuar..."
done
EOF
    
    chmod +x manage.sh
    echo "✅ Script de gerenciamento criado"
}

# Execução principal
main() {
    check_hardware
    install_dependencies
    setup_python_env
    configure_audio
    setup_network
    create_service
    test_installation
    create_management_script
    
    echo ""
    echo "🎉 INSTALAÇÃO CONCLUÍDA COM SUCESSO!"
    echo "====================================="
    echo ""
    echo "📋 Próximos passos:"
    echo "1. Conecte o microfone USB M-305"
    echo "2. Reinicie o Dev Board: sudo reboot"
    echo "3. O assistente iniciará automaticamente após o boot"
    echo ""
    echo "🔧 Para gerenciar:"
    echo "./devboard/manage.sh"
    echo ""
    echo "📊 Para ver logs:"
    echo "sudo journalctl -u voice-assistant-car.service -f"
    echo ""
    echo "⚠️  IMPORTANTE: Reinicie agora para aplicar todas as configurações!"
}

# Executar instalação
main
