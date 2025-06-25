#!/bin/bash

# Funções utilitárias compartilhadas entre scripts do Dev Board
# Source este arquivo nos outros scripts: source ./utils.sh

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configurações padrão
SERVICE_NAME="voice-assistant-car"
PROJECT_DIR="/home/mendel/Sistema-carro-voz"

# Função para imprimir mensagens coloridas
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_step() {
    echo ""
    echo -e "${PURPLE}📋 $1${NC}"
    echo "$(printf '=%.0s' {1..50})"
}

# Verificar se está no Dev Board
check_devboard() {
    if ! grep -q "Mendel" /etc/os-release 2>/dev/null; then
        print_error "Este script deve ser executado no Google Dev Board"
        exit 1
    fi
}

# Verificar conectividade com internet
check_internet() {
    if ping -c 1 8.8.8.8 &> /dev/null; then
        return 0
    else
        return 1
    fi
}

# Verificar se o serviço existe
check_service() {
    if systemctl list-unit-files | grep -q "$SERVICE_NAME"; then
        return 0
    else
        return 1
    fi
}

# Verificar status do serviço
service_status() {
    if systemctl is-active --quiet $SERVICE_NAME; then
        echo "running"
    elif systemctl is-enabled --quiet $SERVICE_NAME; then
        echo "stopped"
    else
        echo "not_installed"
    fi
}

# Obter temperatura da CPU
get_cpu_temp() {
    local temp=$(cat /sys/class/thermal/thermal_zone0/temp 2>/dev/null || echo "0")
    echo $((temp/1000))
}

# Verificar uso da memória
get_memory_usage() {
    free -h | awk 'NR==2{print $3"/"$2}'
}

# Verificar uso do SD card
get_disk_usage() {
    df -h / | awk 'NR==2{print $5}'
}

# Verificar uptime
get_uptime() {
    uptime -p
}

# Verificar dispositivos de áudio USB
check_usb_audio() {
    if lsusb | grep -i "audio\|microphone\|sound" > /dev/null; then
        return 0
    else
        return 1
    fi
}

# Verificar microfone especificamente
check_microphone() {
    if arecord -l | grep -i "usb\|card 1" > /dev/null; then
        return 0
    else
        return 1
    fi
}

# Função comum para configurar WiFi
configure_wifi_network() {
    local ssid="$1"
    local password="$2"
    local method="${3:-wpa_passphrase}" # wpa_passphrase ou manual
    
    if [ -z "$ssid" ] || [ -z "$password" ]; then
        print_error "SSID e senha são obrigatórios"
        return 1
    fi
    
    # Backup da configuração atual se for primeira vez
    if [ ! -f "/etc/wpa_supplicant/wpa_supplicant.conf.backup" ]; then
        sudo cp /etc/wpa_supplicant/wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicant.conf.backup
    fi
    
    if [ "$method" = "wpa_passphrase" ]; then
        # Método usando wpa_passphrase (mais seguro)
        wpa_passphrase "$ssid" "$password" | sudo tee -a /etc/wpa_supplicant/wpa_supplicant.conf > /dev/null
    else
        # Método manual
        sudo tee -a /etc/wpa_supplicant/wpa_supplicant.conf > /dev/null << EOF

network={
    ssid="$ssid"
    psk="$password"
    key_mgmt=WPA-PSK
    priority=10
}
EOF
    fi
    
    # Reiniciar serviços de rede
    print_info "Reiniciando serviços de rede..."
    sudo systemctl restart wpa_supplicant
    sudo systemctl restart dhcpcd 2>/dev/null || sudo systemctl restart networking
    
    sleep 5
    
    # Testar conectividade
    if check_internet; then
        print_success "WiFi configurado com sucesso!"
        return 0
    else
        print_error "Falha na conexão. Verifique as credenciais."
        return 1
    fi
}

# Função para mostrar redes WiFi disponíveis
scan_wifi_networks() {
    print_info "Escaneando redes disponíveis..."
    sudo iwlist scan | grep ESSID | cut -d'"' -f2 | sort | uniq | grep -v "^$"
}

# Função comum para testar áudio básico
test_audio_basic() {
    print_step "Testando áudio básico"
    
    if check_microphone; then
        print_success "Microfone USB detectado"
    else
        print_warning "Microfone USB não encontrado"
        return 1
    fi
    
    if command -v espeak > /dev/null; then
        print_success "TTS disponível"
    else
        print_warning "TTS não encontrado"
    fi
    
    return 0
}

# Função para teste completo de áudio
test_audio_complete() {
    print_step "Teste completo de áudio"
    
    # Testar microfone
    print_info "Testando microfone (gravando 3 segundos)..."
    if arecord -D hw:1,0 -d 3 -f cd /tmp/test_mic.wav 2>/dev/null; then
        print_success "Gravação OK"
        
        # Testar reprodução
        print_info "Testando reprodução..."
        if aplay /tmp/test_mic.wav 2>/dev/null; then
            print_success "Reprodução OK"
            rm -f /tmp/test_mic.wav
            return 0
        else
            print_error "Erro na reprodução"
        fi
        
        rm -f /tmp/test_mic.wav
    else
        print_error "Erro na gravação do microfone"
        print_info "Verifique se o microfone USB está conectado"
    fi
    
    return 1
}

# Função para exibir status completo do sistema
show_system_status() {
    print_step "Status do Sistema"
    
    # Status do serviço
    echo "🔧 Serviço do Assistente:"
    local status=$(service_status)
    case $status in
        "running") print_success "  Rodando" ;;
        "stopped") print_warning "  Parado" ;;
        "not_installed") print_error "  Não instalado" ;;
    esac
    
    # Recursos do sistema
    echo ""
    echo "🔋 Recursos:"
    echo "  Temperatura: $(get_cpu_temp)°C"
    echo "  Memória: $(get_memory_usage)"
    echo "  SD Card: $(get_disk_usage) usado"
    echo "  Uptime: $(get_uptime)"
    
    # Hardware de áudio
    echo ""
    echo "🎤 Dispositivos de Áudio:"
    if check_microphone; then
        print_success "  Microfone USB detectado"
    else
        print_error "  Microfone USB não encontrado"
    fi
    
    # Conectividade
    echo ""
    echo "📶 Conectividade:"
    if check_internet; then
        print_success "  Internet OK"
    else
        print_error "  Sem conexão com internet"
    fi
    
    # WiFi atual
    local current_wifi=$(iwconfig 2>/dev/null | grep ESSID | cut -d'"' -f2)
    if [ -n "$current_wifi" ]; then
        echo "  WiFi: $current_wifi"
    else
        echo "  WiFi: Não conectado"
    fi
}
