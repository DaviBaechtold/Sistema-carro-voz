#!/bin/bash

# Script para gerenciar remotamente o Dev Board do seu computador
# Execute este script do seu computador para administrar o Dev Board via SSH

DEV_BOARD_IP=""
DEV_BOARD_USER="mendel"

echo "🚗 Gerenciamento Remoto - Dev Board AA1"
echo "======================================"

# Configurar IP se não definido
if [ -z "$DEV_BOARD_IP" ]; then
    read -p "Digite o IP do Dev Board: " DEV_BOARD_IP
fi

# Testar conexão
test_connection() {
    if ssh -o ConnectTimeout=5 $DEV_BOARD_USER@$DEV_BOARD_IP "echo 'OK'" 2>/dev/null; then
        return 0
    else
        return 1
    fi
}

echo "🔌 Testando conexão com $DEV_BOARD_IP..."
if ! test_connection; then
    echo "❌ Não foi possível conectar"
    echo "Verifique:"
    echo "1. IP correto: $DEV_BOARD_IP"
    echo "2. SSH habilitado no Dev Board"
    echo "3. Conectividade de rede"
    exit 1
fi

echo "✅ Conectado ao Dev Board"

# Menu principal
while true; do
    echo ""
    echo "Escolha uma opção:"
    echo "1) Status completo do sistema"
    echo "2) Ver logs em tempo real"
    echo "3) Reiniciar assistente"
    echo "4) Atualizar código"
    echo "5) Verificar temperatura"
    echo "6) Fazer backup"
    echo "7) Executar comando personalizado"
    echo "8) Conectar via SSH"
    echo "0) Sair"
    echo
    read -p "Digite sua escolha (0-8): " choice
    
    case $choice in
        1)
            echo "📊 Status do Dev Board:"
            ssh $DEV_BOARD_USER@$DEV_BOARD_IP << 'EOF'
echo "🔋 Sistema:"
echo "  Temperatura: $(cat /sys/class/thermal/thermal_zone0/temp | awk '{print $1/1000}')°C"
echo "  Memória: $(free -h | awk 'NR==2{print $3"/"$2}')"
echo "  SD Card: $(df -h / | awk 'NR==2{print $5" usado"}')"
echo "  Uptime: $(uptime -p)"
echo ""
echo "📋 Serviço do Assistente:"
sudo systemctl status voice-assistant-car.service --no-pager -l
echo ""
echo "🎤 Dispositivos de Áudio:"
arecord -l | grep -E "(card|USB)" || echo "  Nenhum encontrado"
echo ""
echo "📶 Conectividade:"
if ping -c 1 8.8.8.8 &> /dev/null; then
    echo "  ✅ Internet OK"
else
    echo "  ❌ Sem internet"
fi
EOF
            ;;
        2)
            echo "📝 Logs em tempo real (Ctrl+C para sair):"
            ssh $DEV_BOARD_USER@$DEV_BOARD_IP "sudo journalctl -u voice-assistant-car.service -f"
            ;;
        3)
            echo "🔄 Reiniciando assistente..."
            ssh $DEV_BOARD_USER@$DEV_BOARD_IP "sudo systemctl restart voice-assistant-car.service"
            echo "✅ Assistente reiniciado"
            ;;
        4)
            echo "🔄 Atualizando código..."
            ssh $DEV_BOARD_USER@$DEV_BOARD_IP << 'EOF'
cd Sistema-carro-voz
echo "📥 Baixando atualizações..."
git pull origin main
echo "🔄 Reiniciando serviço..."
sudo systemctl restart voice-assistant-car.service
echo "✅ Código atualizado"
EOF
            ;;
        5)
            echo "🌡️ Monitorando temperatura (Ctrl+C para sair):"
            while true; do
                temp=$(ssh $DEV_BOARD_USER@$DEV_BOARD_IP "cat /sys/class/thermal/thermal_zone0/temp")
                temp_c=$((temp/1000))
                
                if [ $temp_c -gt 70 ]; then
                    status="⚠️  ALTA"
                elif [ $temp_c -gt 60 ]; then
                    status="🔶 ELEVADA"
                else
                    status="✅ NORMAL"
                fi
                
                echo "$(date '+%H:%M:%S'): ${temp_c}°C - $status"
                sleep 10
            done
            ;;
        6)
            echo "💾 Fazendo backup..."
            timestamp=$(date +%Y%m%d_%H%M%S)
            mkdir -p backups
            
            ssh $DEV_BOARD_USER@$DEV_BOARD_IP "tar -czf /tmp/devboard-backup-$timestamp.tar.gz Sistema-carro-voz/ /etc/systemd/system/voice-assistant-car.service /etc/asound.conf"
            scp $DEV_BOARD_USER@$DEV_BOARD_IP:/tmp/devboard-backup-$timestamp.tar.gz backups/
            ssh $DEV_BOARD_USER@$DEV_BOARD_IP "rm /tmp/devboard-backup-$timestamp.tar.gz"
            
            echo "✅ Backup salvo em: backups/devboard-backup-$timestamp.tar.gz"
            ;;
        7)
            read -p "Digite o comando: " command
            echo "🔧 Executando: $command"
            ssh $DEV_BOARD_USER@$DEV_BOARD_IP "$command"
            ;;
        8)
            echo "🔐 Conectando via SSH..."
            ssh $DEV_BOARD_USER@$DEV_BOARD_IP
            ;;
        0)
            echo "👋 Saindo..."
            exit 0
            ;;
        *)
            echo "❌ Opção inválida"
            ;;
    esac
    
    if [ $choice != "2" ] && [ $choice != "5" ] && [ $choice != "8" ]; then
        read -p "Pressione Enter para continuar..."
    fi
done
