#!/bin/bash

# Script de configuração do Assistente de Voz com Arduino
# Para Google Dev Board (AA1) + Arduino Nano 2040 Connect

set -e

echo "=== Assistente de Voz com Arduino - Configuração ==="
echo "Google Dev Board (AA1) + Arduino Nano 2040 Connect"
echo

# Menu principal
show_menu() {
    echo "Escolha uma opção:"
    echo "1) Configuração inicial completa"
    echo "2) Instalar/atualizar vozes TTS"
    echo "3) Testar conexão Arduino"
    echo "4) Executar assistente (WiFi)"
    echo "5) Executar assistente (Serial)"
    echo "6) Configurar IP do Dev Board"
    echo "7) Sair"
    echo
    read -p "Digite sua escolha (1-7): " choice
}

# Configuração inicial
setup_initial() {
    echo "🔧 Configuração inicial..."
    
    # Atualizar sistema
    echo "Atualizando sistema..."
    sudo apt update && sudo apt upgrade -y
    
    # Instalar dependências do sistema
    echo "Instalando dependências do sistema..."
    sudo apt install -y python3-pip python3-dev python3-venv
    sudo apt install -y portaudio19-dev flac
    sudo apt install -y alsa-utils pulseaudio
    sudo apt install -y python3-numpy  # Numpy do sistema para compatibilidade
    
    # Configurar áudio
    echo "Configurando áudio..."
    sudo usermod -a -G audio,dialout $USER  # dialout para acesso serial
    
    # Criar ambiente virtual
    if [ ! -d "venv" ]; then
        echo "Criando ambiente virtual..."
        python3 -m venv venv
    fi
    
    # Instalar dependências Python
    echo "Instalando dependências Python..."
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements_arduino.txt
    
    echo "✅ Configuração inicial concluída!"
    echo "⚠️  Reinicie para aplicar permissões de grupo (audio, dialout)"
}

# Instalar vozes
install_voices() {
    echo "🎤 Instalando vozes TTS..."
    
    sudo apt-get update
    sudo apt-get install -y espeak espeak-data espeak-data-pt
    sudo apt-get install -y festival festvox-br-cid
    sudo apt-get install -y mbrola mbrola-br1 mbrola-br3 2>/dev/null || echo "⚠️ MBROLA não encontrado"
    sudo apt-get install -y flite
    
    echo "✅ Vozes instaladas!"
}

# Testar conexão Arduino
test_arduino() {
    echo "🧪 Testando conexão com Arduino..."
    
    source venv/bin/activate
    
    python3 -c "
import socket
import serial
import time

print('Testando conexão...')
print()

# Testar WiFi
print('1. Teste WiFi (porta 5555):')
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    sock.bind(('0.0.0.0', 5555))
    sock.listen(1)
    print('   ✅ Porta 5555 disponível para receber Arduino')
    sock.close()
except Exception as e:
    print(f'   ❌ Erro na porta WiFi: {e}')

print()

# Listar portas seriais
print('2. Portas seriais disponíveis:')
try:
    import serial.tools.list_ports
    ports = serial.tools.list_ports.comports()
    if ports:
        for port in ports:
            print(f'   - {port.device}: {port.description}')
    else:
        print('   ❌ Nenhuma porta serial encontrada')
except Exception as e:
    print(f'   ❌ Erro ao listar portas: {e}')

print()
print('💡 Dicas:')
print('   - WiFi: Configure ssid/password/IP no código Arduino')
print('   - Serial: Conecte Arduino via USB e use a porta listada acima')
"
    
    echo "✅ Teste concluído!"
}

# Executar assistente WiFi
run_wifi() {
    echo "🚀 Iniciando assistente (modo WiFi)..."
    echo
    echo "Certifique-se que o Arduino está:"
    echo "- Conectado na mesma rede WiFi"
    echo "- Com IP do Dev Board configurado corretamente"
    echo "- Com sketch carregado e rodando"
    echo
    
    source venv/bin/activate
    
    # Garantir que USE_WIFI está True
    sed -i 's/USE_WIFI = False/USE_WIFI = True/g' voice_assistant_arduino.py
    
    python3 voice_assistant_arduino.py
}

# Executar assistente Serial
run_serial() {
    echo "🚀 Iniciando assistente (modo Serial)..."
    echo
    
    # Listar portas disponíveis
    echo "Portas seriais detectadas:"
    ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null || echo "Nenhuma porta USB encontrada"
    echo
    
    read -p "Digite a porta serial (ex: /dev/ttyUSB0): " port
    
    source venv/bin/activate
    
    # Configurar porta no código
    sed -i "s|SERIAL_PORT = '.*'|SERIAL_PORT = '$port'|g" voice_assistant_arduino.py
    sed -i 's/USE_WIFI = True/USE_WIFI = False/g' voice_assistant_arduino.py
    
    python3 voice_assistant_arduino.py
}

# Configurar IP
config_ip() {
    echo "📡 Configuração de IP do Dev Board"
    echo
    echo "IP atual do Dev Board:"
    hostname -I
    echo
    echo "Este IP deve ser configurado no código Arduino em:"
    echo "const char* devboard_ip = \"XXX.XXX.XXX.XXX\";"
    echo
    read -p "Pressione Enter para continuar..."
}

# Menu principal
while true; do
    show_menu
    
    case $choice in
        1)
            setup_initial
            ;;
        2)
            install_voices
            ;;
        3)
            test_arduino
            ;;
        4)
            run_wifi
            ;;
        5)
            run_serial
            ;;
        6)
            config_ip
            ;;
        7)
            echo "Saindo..."
            exit 0
            ;;
        *)
            echo "Opção inválida!"
            ;;
    esac
    
    echo
    read -p "Pressione Enter para continuar..."
    echo
done