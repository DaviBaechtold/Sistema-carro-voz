#!/bin/bash

# Script para gerenciar localmente o assistente no Dev Board AA1
# Execute este script diretamente no Dev Board para administração local

set -e

# Carregar funções utilitárias
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/utils.sh"

echo "🚗 Gerenciamento Local - Assistente de Voz"
echo "=========================================="

# Verificar se está no Dev Board
check_devboard

# Verificar se o serviço existe
if ! check_service; then
    print_error "Serviço não encontrado. Execute primeiro: ./install.sh"
    exit 1
fi

# Funções auxiliares (agora usa utils.sh para as principais)
show_logs() {
    print_step "Logs do Assistente (últimas 50 linhas)"
    sudo journalctl -u $SERVICE_NAME -n 50 --no-pager
}

follow_logs() {
    print_step "Logs em tempo real (Ctrl+C para sair)"
    sudo journalctl -u $SERVICE_NAME -f
}

restart_service() {
    print_info "Reiniciando assistente..."
    sudo systemctl restart $SERVICE_NAME
    sleep 2
    if systemctl is-active --quiet $SERVICE_NAME; then
        print_success "Assistente reiniciado com sucesso"
    else
        print_error "Falha ao reiniciar. Verifique os logs."
    fi
}

stop_service() {
    print_info "Parando assistente..."
    sudo systemctl stop $SERVICE_NAME
    print_success "Assistente parado"
}

start_service() {
    print_info "Iniciando assistente..."
    sudo systemctl start $SERVICE_NAME
    sleep 2
    if systemctl is-active --quiet $SERVICE_NAME; then
        print_success "Assistente iniciado com sucesso"
    else
        print_error "Falha ao iniciar. Verifique os logs."
    fi
}

configure_wifi() {
    print_step "Configuração WiFi"
    
    print_info "Redes disponíveis:"
    scan_wifi_networks
    
    echo ""
    read -p "Digite o nome da rede WiFi: " ssid
    read -s -p "Digite a senha: " password
    echo ""
    
    configure_wifi_network "$ssid" "$password" "wpa_passphrase"
}

update_code() {
    print_step "Atualizando código"
    
    cd $PROJECT_DIR
    
    # Fazer backup das configurações locais
    if [ -f "config.local" ]; then
        cp config.local config.local.bak
    fi
    
    # Atualizar código
    print_info "Baixando atualizações..."
    git pull origin main
    
    # Restaurar configurações
    if [ -f "config.local.bak" ]; then
        mv config.local.bak config.local
    fi
    
    print_info "Reiniciando serviço..."
    restart_service
    
    print_success "Atualização concluída"
}

# Menu principal
if [ $# -eq 0 ]; then
    while true; do
        echo ""
        echo "Escolha uma opção:"
        echo "1) Status do sistema"
        echo "2) Ver logs (últimas 50 linhas)"
        echo "3) Logs em tempo real"
        echo "4) Reiniciar assistente"
        echo "5) Parar assistente"
        echo "6) Iniciar assistente"
        echo "7) Testar áudio"
        echo "8) Configurar WiFi"
        echo "9) Atualizar código"
        echo "0) Sair"
        echo
        read -p "Digite sua escolha (0-9): " choice
        
        case $choice in
            1) show_system_status ;;
            2) show_logs ;;
            3) follow_logs ;;
            4) restart_service ;;
            5) stop_service ;;
            6) start_service ;;
            7) test_audio_complete ;;
            8) configure_wifi ;;
            9) update_code ;;
            0) print_success "Até logo!"; exit 0 ;;
            *) print_error "Opção inválida" ;;
        esac
    done
else
    # Permitir execução direta de comandos
    case $1 in
        status) show_system_status ;;
        logs) show_logs ;;
        follow-logs) follow_logs ;;
        restart) restart_service ;;
        stop) stop_service ;;
        start) start_service ;;
        test-audio) test_audio_complete ;;
        wifi) configure_wifi ;;
        update) update_code ;;
        *) 
            echo "Uso: $0 [comando]"
            echo "Comandos disponíveis: status, logs, follow-logs, restart, stop, start, test-audio, wifi, update"
            echo "Ou execute sem parâmetros para o menu interativo"
            exit 1
            ;;
    esac
fi
