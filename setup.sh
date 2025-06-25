#!/bin/bash

# Script completo de configuração do Assistente de Voz
# Para Google Dev Board (AA1) com Microfone M-305

set -e  # Parar se houver erro

echo "=== Assistente de Voz - Configuração Completa ==="
echo "Google Dev Board (AA1) + Microfone M-305"
echo

# Função para mostrar opções
show_menu() {
    echo "Escolha uma opção:"
    echo "1) Configuração inicial completa (primeira vez)"
    echo "2) Instalar/atualizar vozes TTS"
    echo "3) Testar sistema (microfone + vozes)"
    echo "4) Executar assistente"
    echo "5) Sair"
    echo
    read -p "Digite sua escolha (1-5): " choice
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
    sudo apt install -y portaudio19-dev
    sudo apt install -y alsa-utils pulseaudio
    
    # Configurar áudio
    echo "Configurando áudio..."
    sudo usermod -a -G audio $USER
    
    # Criar ambiente virtual se não existir
    if [ ! -d "venv" ]; then
        echo "Criando ambiente virtual..."
        python3 -m venv venv
    fi
    
    # Ativar ambiente virtual e instalar dependências
    echo "Instalando dependências Python..."
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    
    echo "✅ Configuração inicial concluída!"
    echo "⚠️  Pode ser necessário reiniciar para aplicar configurações de áudio"
}

# Instalar vozes
install_voices() {
    echo "🎤 Instalando vozes TTS mais naturais..."
    
    # Detectar distribuição
    if command -v apt-get &> /dev/null; then
        DISTRO="debian"
    elif command -v yum &> /dev/null; then
        DISTRO="redhat"
    elif command -v pacman &> /dev/null; then
        DISTRO="arch"
    else
        echo "❌ Distribuição não suportada automaticamente."
        echo "Por favor, instale manualmente os pacotes de voz TTS."
        return 1
    fi
    
    echo "📍 Distribuição detectada: $DISTRO"
    
    case $DISTRO in
        "debian")
            echo "Instalando vozes para Debian/Ubuntu..."
            sudo apt-get update
            sudo apt-get install -y espeak espeak-data espeak-data-pt
            sudo apt-get install -y festival festvox-br-cid
            sudo apt-get install -y mbrola mbrola-br1 mbrola-br3 2>/dev/null || echo "⚠️ MBROLA não encontrado no repositório"
            sudo apt-get install -y flite
            sudo apt-get install -y speech-dispatcher-espeak-ng 2>/dev/null || echo "⚠️ espeak-ng não encontrado"
            ;;
        "redhat"|"fedora")
            PKG_MANAGER=$(command -v dnf &> /dev/null && echo "dnf" || echo "yum")
            echo "Instalando vozes para RedHat/CentOS/Fedora..."
            sudo $PKG_MANAGER install -y espeak espeak-data festival flite
            ;;
        "arch")
            echo "Instalando vozes para Arch Linux..."
            sudo pacman -S --noconfirm espeak espeak-ng festival flite
            if command -v yay &> /dev/null; then
                yay -S --noconfirm mbrola-voices-br1 mbrola-voices-br3 2>/dev/null || echo "⚠️ Vozes MBROLA não encontradas no AUR"
            fi
            ;;
    esac
    
    echo "✅ Vozes instaladas! Reinicie o assistente para detectar as novas vozes."
}

# Testar sistema
test_system() {
    echo "🧪 Testando sistema..."
    
    # Ativar ambiente virtual
    source venv/bin/activate
    
    # Executar testes
    python3 -c "
import voice_assistant
print('Testando microfone e vozes...')
voice_assistant.test_voices()
print()
voice_assistant.test_microphone()
"
    echo "✅ Teste concluído!"
}

# Executar assistente
run_assistant() {
    echo "🚀 Iniciando assistente de voz..."
    echo
    echo "Como usar:"
    echo "- Diga: 'Assistente, tocar música'"
    echo "- Diga: 'OK Google, ligar para João'"
    echo "- Diga: 'Carro, navegar para casa'"
    echo "- Para encerrar: 'Assistente, tchau'"
    echo
    
    # Ativar ambiente virtual
    source venv/bin/activate
    
    # Executar assistente
    python3 voice_assistant.py
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
            test_system
            ;;
        4)
            run_assistant
            ;;
        5)
            echo "Saindo..."
            exit 0
            ;;
        *)
            echo "Opção inválida. Tente novamente."
            ;;
    esac
    
    echo
    read -p "Pressione Enter para continuar..."
    echo
done
