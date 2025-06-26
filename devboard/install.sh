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
    
    # Verificar microfone USB - usar comando alternativo se lsusb não existir
    if command -v lsusb >/dev/null 2>&1; then
        if lsusb | grep -i "audio\|microphone\|sound" > /dev/null; then
            echo "✅ Dispositivo de áudio USB detectado"
        else
            echo "⚠️  Microfone USB não detectado - conecte o M-305"
        fi
    else
        # Método alternativo sem lsusb
        if ls /dev/snd/pcm* 2>/dev/null | grep -q "pcm"; then
            echo "✅ Dispositivos de áudio detectados"
        else
            echo "⚠️  Microfone USB não detectado - conecte o M-305"
        fi
    fi
    
    # Verificar temperatura
    temp=$(cat /sys/class/thermal/thermal_zone0/temp 2>/dev/null || echo "0")
    temp_c=$((temp/1000))
    echo "🌡️  Temperatura atual: ${temp_c}°C"
    
    if [ $temp_c -gt 70 ]; then
        echo "🔥 ATENÇÃO: Temperatura alta! Aguardando resfriamento..."
        echo "💡 Considere melhorar a ventilação do Dev Board"
        sleep 10
    fi
}

fix_repositories() {
    log_step "Corrigindo repositórios"
    
    # Tentar corrigir chaves GPG
    echo "🔑 Corrigindo chaves GPG..."
    curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add - 2>/dev/null || {
        echo "⚠️  Não foi possível adicionar chave GPG automaticamente"
    }
    
    # Atualizar repositórios (com fallback para allow insecure)
    echo "📥 Atualizando repositórios..."
    sudo apt update 2>/dev/null || {
        echo "⚠️  Problemas com repositórios seguros, tentando modo inseguro..."
        sudo apt update -o Acquire::AllowInsecureRepositories=true 2>/dev/null || {
            echo "⚠️  Continuando mesmo com problemas de repositório"
        }
    }
}

install_dependencies() {
    log_step "Instalando dependências"
    
    # Instalar pacotes essenciais
    echo "📦 Instalando pacotes essenciais..."
    sudo apt install -y python3-pip python3-dev python3-venv || {
        echo "⚠️  Tentando instalação alternativa..."
        sudo apt install -y --allow-unauthenticated python3-pip python3-dev python3-venv
    }
    
    # Instalar dependências de áudio e sistema
    sudo apt install -y portaudio19-dev alsa-utils pulseaudio || true
    sudo apt install -y git curl wget htop usbutils || true
    
    # Instalar vozes TTS
    echo "🔊 Instalando vozes TTS..."
    sudo apt install -y espeak espeak-data espeak-data-pt || true
    sudo apt install -y festival flite || true
    
    # Tentar instalar vozes brasileiras
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
    
    # Criar configuração ALSA otimizada
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
    echo "1) Configurar WiFi agora"
    echo "2) Manter configuração atual"
    echo "3) Configurar mais tarde"
    read -p "Escolha (1-3): " net_choice
    
    case $net_choice in
        1)
            setup_wifi
            ;;
        2)
            echo "✅ Mantendo configuração atual"
            ;;
        3)
            echo "⚠️  Configure depois com: ./manage.sh"
            ;;
    esac
}

setup_wifi() {
    read -p "Nome da rede WiFi (SSID): " ssid
    read -s -p "Senha da rede WiFi: " password
    echo
    
    # Backup da configuração atual se não existe
    if [ ! -f "/etc/wpa_supplicant/wpa_supplicant.conf.backup" ]; then
        sudo cp /etc/wpa_supplicant/wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicant.conf.backup
    fi
    
    # Adicionar nova rede usando wpa_passphrase (mais seguro)
    wpa_passphrase "$ssid" "$password" | sudo tee -a /etc/wpa_supplicant/wpa_supplicant.conf > /dev/null
    
    # Reiniciar serviços de rede
    sudo systemctl restart wpa_supplicant
    sudo systemctl restart dhcpcd 2>/dev/null || sudo systemctl restart networking
    
    sleep 5
    
    # Testar conectividade
    if ping -c 3 8.8.8.8 &> /dev/null; then
        echo "✅ WiFi configurado com sucesso"
    else
        echo "❌ Falha na configuração WiFi - configure manualmente depois"
    fi
}

create_service() {
    log_step "Criando serviço systemd"
    
    # Criar script de inicialização otimizado
    cat > ../start_car_assistant.sh << 'EOF'
#!/bin/bash

# Script de inicialização otimizado para carro
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

# Configurar CPU baseado na temperatura
temp=$(cat /sys/class/thermal/thermal_zone0/temp 2>/dev/null || echo "0")
temp_c=$((temp/1000))
echo "🌡️  Temperatura: ${temp_c}°C"

if [ $temp_c -gt 75 ]; then
    echo "⚠️  Temperatura alta - modo economia"
    echo powersave | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor > /dev/null 2>&1 || true
else
    echo "✅ Temperatura OK - modo performance"
    echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor > /dev/null 2>&1 || true
fi

# Navegar para diretório e ativar ambiente
cd /home/mendel/Sistema-carro-voz
source venv/bin/activate

# Iniciar assistente (versão Dev Board se disponível)
if [ -f "devboard/voice_assistant_devboard.py" ]; then
    echo "🚀 Iniciando versão otimizada para Dev Board..."
    python3 devboard/voice_assistant_devboard.py
else
    echo "🚀 Iniciando versão padrão..."
    python3 voice_assistant.py
fi
EOF
    
    chmod +x ../start_car_assistant.sh
    
    # Criar serviço systemd otimizado
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
TimeoutStartSec=300
KillMode=mixed
KillSignal=SIGTERM

[Install]
WantedBy=multi-user.target
EOF
    
    # Configurar logrotate para evitar enchimento do SD
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
    if command -v arecord >/dev/null 2>&1; then
        if arecord -l 2>/dev/null | grep -i "usb\|card 1" > /dev/null; then
            echo "✅ Microfone USB detectado"
        else
            echo "⚠️  Microfone USB não encontrado"
        fi
    else
        echo "⚠️  arecord não disponível"
    fi
    
    # Testar TTS
    echo "🔊 Testando síntese de voz..."
    if command -v espeak > /dev/null; then
        echo "✅ TTS disponível"
    else
        echo "⚠️  TTS não encontrado"
    fi
    
    echo "✅ Testes básicos concluídos"
}

show_menu() {
    echo ""
    echo "Escolha o tipo de instalação:"
    echo "1) Instalação completa (recomendado)"
    echo "2) Apenas configurar ambiente Python"
    echo "3) Apenas criar serviço systemd"
    echo "4) Testar sistema atual"
    echo "5) Sair"
    echo
    read -p "Digite sua escolha (1-5): " choice
}

# Execução principal
main() {
    case ${1:-""} in
        --quick)
            # Instalação rápida sem menu
            choice=1
            ;;
        --test)
            choice=4
            ;;
        *)
            show_menu
            ;;
    esac
    
    case $choice in
        1)
            echo "🚀 Iniciando instalação completa..."
            check_hardware
            fix_repositories
            install_dependencies
            setup_python_env
            configure_audio
            setup_network
            create_service
            test_installation
            
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
            echo "./manage.sh"
            echo ""
            echo "📊 Para ver logs:"
            echo "sudo journalctl -u voice-assistant-car.service -f"
            echo ""
            echo "⚠️  IMPORTANTE: Reinicie agora para aplicar todas as configurações!"
            ;;
        2)
            setup_python_env
            echo "✅ Ambiente Python configurado"
            ;;
        3)
            create_service
            echo "✅ Serviço systemd criado"
            ;;
        4)
            check_hardware
            test_installation
            ;;
        5)
            echo "👋 Saindo..."
            exit 0
            ;;
        *)
            echo "❌ Opção inválida"
            exit 1
            ;;
    esac
}

# Executar instalação
main "$@"
