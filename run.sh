#!/bin/bash

# Script de inicialização rápida do Assistente de Voz
# Execute apenas: ./run.sh

echo "🚗 Assistente de Voz para Carro"
echo "================================"

# Verificar se ambiente virtual existe
if [ ! -d "venv" ]; then
    echo "❌ Ambiente não configurado. Execute './setup.sh' primeiro."
    exit 1
fi

# Ativar ambiente virtual
source venv/bin/activate

# Verificar dependências
python3 -c "import speech_recognition, pyttsx3, pyaudio" 2>/dev/null || {
    echo "❌ Dependências não instaladas. Execute './setup.sh' primeiro."
    exit 1
}

echo "🚀 Iniciando assistente..."
echo "💡 Dica: Diga 'Assistente, ajuda' para ver os comandos"
echo

# Executar assistente
python3 voice_assistant.py
