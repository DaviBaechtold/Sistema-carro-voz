#!/bin/bash

# Script para gerenciar remotamente o assistente no Dev Board
# Execute este script do seu computador para gerenciar o Dev Board

DEV_BOARD_IP=""
DEV_BOARD_USER="mendel"

echo "🚗 Gerenciamento Remoto - Assistente de Voz"
echo "==========================================="

# Verificar se IP foi configurado
if [ -z "$DEV_BOARD_IP" ]; then
    read -p "Digite o IP do Dev Board: " DEV_BOARD_IP
fi

# Função para testar conexão
test_connection() {
    echo "🔌 Testando conexão com $DEV_BOARD_IP..."
    if ssh -o ConnectTimeout=5 $DEV_BOARD_USER@$DEV_BOARD_IP "echo 'Conexão OK'" 2>/dev/null; then
        echo "✅ Conexão estabelecida"
        return 0
    else
        echo "❌ Não foi possível conectar"
        return 1
    fi
}

# Função para ver status
check_status() {
    echo "📊 Verificando status do assistente..."
    ssh $DEV_BOARD_USER@$DEV_BOARD_IP << 'EOF'
echo "🔋 Status do Sistema:"
echo "Temperatura: $(cat /sys/class/thermal/thermal_zone0/temp | awk '{print $1/1000}')°C"
echo "Memória: $(free -h | awk 'NR==2{print $3"/"$2}')"
echo "SD Card: $(df -h / | awk 'NR==2{print $5" usado"}')"
echo ""
echo "📋 Status do Serviço:"
sudo systemctl status voice-assistant-car.service --no-pager -l
echo ""
echo "📝 Últimos logs:"
sudo journalctl -u voice-assistant-car.service --no-pager -n 5
EOF
}

# Função para atualizar código
update_code() {
    echo "🔄 Atualizando código do assistente..."
    ssh $DEV_BOARD_USER@$DEV_BOARD_IP << 'EOF'
cd Sistema-carro-voz
git pull origin main
sudo systemctl restart voice-assistant-car.service
echo "✅ Código atualizado e serviço reiniciado"
EOF
}

# Função para ver logs em tempo real
view_logs() {
    echo "📝 Visualizando logs em tempo real (Ctrl+C para sair)..."
    ssh $DEV_BOARD_USER@$DEV_BOARD_IP "sudo journalctl -u voice-assistant-car.service -f"
}

# Função para reiniciar serviço
restart_service() {
    echo "🔄 Reiniciando serviço do assistente..."
    ssh $DEV_BOARD_USER@$DEV_BOARD_IP << 'EOF'
sudo systemctl restart voice-assistant-car.service
echo "✅ Serviço reiniciado"
EOF
}

# Função para fazer backup
backup_config() {
    echo "💾 Fazendo backup das configurações..."
    timestamp=$(date +%Y%m%d_%H%M%S)
    mkdir -p backups
    
    ssh $DEV_BOARD_USER@$DEV_BOARD_IP "tar -czf /tmp/voice-assistant-backup-$timestamp.tar.gz Sistema-carro-voz/*.py Sistema-carro-voz/*.sh Sistema-carro-voz/*.txt /etc/systemd/system/voice-assistant-car.service /etc/asound.conf"
    
    scp $DEV_BOARD_USER@$DEV_BOARD_IP:/tmp/voice-assistant-backup-$timestamp.tar.gz backups/
    
    echo "✅ Backup salvo em backups/voice-assistant-backup-$timestamp.tar.gz"
}

# Função para monitorar temperatura
monitor_temperature() {
    echo "🌡️  Monitorando temperatura (Ctrl+C para sair)..."
    while true; do
        temp=$(ssh $DEV_BOARD_USER@$DEV_BOARD_IP "cat /sys/class/thermal/thermal_zone0/temp")
        temp_celsius=$((temp/1000))
        
        if [ $temp_celsius -gt 70 ]; then
            echo "$(date): ⚠️  TEMPERATURA ALTA: ${temp_celsius}°C"
        else
            echo "$(date): 🌡️  Temperatura OK: ${temp_celsius}°C"
        fi
        
        sleep 30
    done
}

# Função para executar comando personalizado
run_custom_command() {
    read -p "Digite o comando para executar no Dev Board: " command
    echo "🔧 Executando: $command"
    ssh $DEV_BOARD_USER@$DEV_BOARD_IP "$command"
}

# Menu principal
if ! test_connection; then
    echo "❌ Não foi possível conectar ao Dev Board"
    echo "Verifique:"
    echo "1. IP correto: $DEV_BOARD_IP"
    echo "2. SSH habilitado no Dev Board"
    echo "3. Conectividade de rede"
    exit 1
fi

while true; do
    echo ""
    echo "Escolha uma opção:"
    echo "1) Ver status do sistema"
    echo "2) Atualizar código"
    echo "3) Ver logs em tempo real"
    echo "4) Reiniciar serviço"
    echo "5) Fazer backup"
    echo "6) Monitorar temperatura"
    echo "7) Executar comando personalizado"
    echo "8) Sair"
    echo
    read -p "Digite sua escolha (1-8): " choice
    
    case $choice in
        1)
            check_status
            ;;
        2)
            update_code
            ;;
        3)
            view_logs
            ;;
        4)
            restart_service
            ;;
        5)
            backup_config
            ;;
        6)
            monitor_temperature
            ;;
        7)
            run_custom_command
            ;;
        8)
            echo "Saindo..."
            exit 0
            ;;
        *)
            echo "Opção inválida. Tente novamente."
            ;;
    esac
done
