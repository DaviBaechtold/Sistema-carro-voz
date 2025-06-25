#!/bin/bash

# Script para configurar WiFi e rede no Google Dev Board
# Execute no Dev Board para configurar conectividade

echo "📶 Configuração de Rede - Google Dev Board"
echo "=========================================="

# Função para configurar WiFi
setup_wifi() {
    echo "📡 Configurando WiFi..."
    read -p "Nome da rede WiFi (SSID): " SSID
    read -s -p "Senha da rede WiFi: " PASSWORD
    echo
    
    # Criar configuração do wpa_supplicant
    sudo tee -a /etc/wpa_supplicant/wpa_supplicant.conf > /dev/null << EOF

network={
    ssid="$SSID"
    psk="$PASSWORD"
    key_mgmt=WPA-PSK
    priority=1
}
EOF
    
    echo "✅ WiFi configurado"
    sudo systemctl restart networking
    sleep 5
    
    if ping -c 3 8.8.8.8 &> /dev/null; then
        echo "✅ Conectividade testada com sucesso"
    else
        echo "❌ Problema de conectividade"
    fi
}

# Função para configurar hotspot (para configuração remota)
setup_hotspot() {
    echo "📶 Configurando Hotspot para configuração remota..."
    
    # Instalar dependências
    sudo apt install -y hostapd dnsmasq
    
    # Configurar hostapd
    sudo tee /etc/hostapd/hostapd.conf > /dev/null << EOF
interface=wlan1
driver=nl80211
ssid=CarAssistant-Config
hw_mode=g
channel=7
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=CarVoice2025
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
EOF
    
    # Configurar dnsmasq
    sudo tee -a /etc/dnsmasq.conf > /dev/null << EOF

# Configuração do Hotspot
interface=wlan1
dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h
EOF
    
    # Configurar interface
    sudo tee -a /etc/dhcpcd.conf > /dev/null << EOF

interface wlan1
    static ip_address=192.168.4.1/24
    nohook wpa_supplicant
EOF
    
    echo "✅ Hotspot configurado"
    echo "SSID: CarAssistant-Config"
    echo "Senha: CarVoice2025"
    echo "IP do Dev Board: 192.168.4.1"
}

# Função para configurar acesso SSH
setup_ssh() {
    echo "🔐 Configurando acesso SSH..."
    
    # Habilitar SSH
    sudo systemctl enable ssh
    sudo systemctl start ssh
    
    # Configurar chaves SSH se fornecidas
    if [ -f ~/.ssh/authorized_keys ]; then
        echo "✅ Chaves SSH já configuradas"
    else
        echo "📝 Para configurar acesso sem senha, adicione sua chave pública:"
        echo "No seu computador: ssh-copy-id mendel@IP_DO_DEVBOARD"
    fi
    
    # Configurar firewall básico
    sudo ufw allow ssh
    sudo ufw --force enable
    
    echo "✅ SSH configurado e protegido"
}

# Menu principal
while true; do
    echo ""
    echo "Escolha uma opção:"
    echo "1) Configurar WiFi"
    echo "2) Configurar Hotspot para configuração remota"
    echo "3) Configurar acesso SSH"
    echo "4) Verificar status da rede"
    echo "5) Sair"
    echo
    read -p "Digite sua escolha (1-5): " choice
    
    case $choice in
        1)
            setup_wifi
            ;;
        2)
            setup_hotspot
            ;;
        3)
            setup_ssh
            ;;
        4)
            echo "📊 Status da Rede:"
            echo "IP atual:"
            ip addr show | grep -E "inet.*wlan|inet.*eth" | awk '{print $2}'
            echo ""
            echo "Conectividade:"
            if ping -c 1 8.8.8.8 &> /dev/null; then
                echo "✅ Internet OK"
            else
                echo "❌ Sem internet"
            fi
            echo ""
            echo "Redes WiFi disponíveis:"
            sudo iwlist scan | grep ESSID | head -10
            ;;
        5)
            echo "Saindo..."
            exit 0
            ;;
        *)
            echo "Opção inválida. Tente novamente."
            ;;
    esac
done
