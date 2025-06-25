#!/bin/bash

# Script de verificação final do projeto
echo "🔍 Verificação Final - Assistente de Voz para Carro"
echo "================================================="

# Verificar arquivos essenciais
echo "📁 Verificando arquivos essenciais..."
files=(
    "voice_assistant.py"
    "voice_assistant_devboard.py"
    "setup.sh"
    "run.sh"
    "deploy_devboard.sh"
    "setup_network.sh" 
    "remote_manager.sh"
    "requirements.txt"
    "README.md"
    "DEVBOARD_DEPLOY.md"
    "CHANGELOG.md"
    "LICENSE"
    ".gitignore"
)

missing_files=()
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file - FALTANDO"
        missing_files+=("$file")
    fi
done

# Verificar permissões dos scripts
echo ""
echo "🔐 Verificando permissões dos scripts..."
scripts=("setup.sh" "run.sh" "deploy_devboard.sh" "setup_network.sh" "remote_manager.sh")
for script in "${scripts[@]}"; do
    if [ -x "$script" ]; then
        echo "✅ $script - executável"
    else
        echo "⚠️  $script - sem permissão de execução"
        chmod +x "$script" 2>/dev/null && echo "   🔧 Permissão corrigida"
    fi
done

# Verificar dependências Python
echo ""
echo "🐍 Verificando dependências Python..."
if [ -f "requirements.txt" ]; then
    echo "📦 Dependências em requirements.txt:"
    cat requirements.txt | grep -v "^#" | grep -v "^$"
else
    echo "❌ requirements.txt não encontrado"
fi

# Verificar venv se existir
if [ -d "venv" ]; then
    echo ""
    echo "🔍 Verificando ambiente virtual..."
    source venv/bin/activate 2>/dev/null && {
        echo "✅ Ambiente virtual ativado"
        python3 -c "
import sys
print(f'Python: {sys.version}')
try:
    import speech_recognition
    print('✅ SpeechRecognition: OK')
except ImportError:
    print('❌ SpeechRecognition: FALTANDO')

try:
    import pyttsx3
    print('✅ pyttsx3: OK')
except ImportError:
    print('❌ pyttsx3: FALTANDO')

try:
    import pyaudio
    print('✅ pyaudio: OK')
except ImportError:
    print('❌ pyaudio: FALTANDO')
" 2>/dev/null
        deactivate
    } || echo "⚠️  Problema ao ativar ambiente virtual"
fi

# Verificar sintaxe dos arquivos Python
echo ""
echo "🔍 Verificando sintaxe dos arquivos Python..."
python_files=("voice_assistant.py" "voice_assistant_devboard.py")
for py_file in "${python_files[@]}"; do
    if [ -f "$py_file" ]; then
        python3 -m py_compile "$py_file" 2>/dev/null && {
            echo "✅ $py_file - sintaxe OK"
        } || {
            echo "❌ $py_file - erro de sintaxe"
        }
    fi
done

# Verificar tamanhos dos arquivos
echo ""
echo "📊 Tamanhos dos arquivos principais:"
ls -lh voice_assistant*.py setup.sh deploy_devboard.sh README.md 2>/dev/null | awk '{print $5 "\t" $9}' | grep -v "^$"

# Verificar se está em repositório Git
echo ""
echo "🔄 Status do Git:"
if [ -d ".git" ]; then
    echo "✅ Repositório Git inicializado"
    git status --porcelain | head -5
    if [ $? -eq 0 ]; then
        echo "📊 Arquivos não commitados: $(git status --porcelain | wc -l)"
    fi
else
    echo "⚠️  Repositório Git não inicializado"
fi

# Resumo final
echo ""
echo "📋 RESUMO FINAL"
echo "==============="

if [ ${#missing_files[@]} -eq 0 ]; then
    echo "✅ Todos os arquivos essenciais estão presentes"
else
    echo "❌ Arquivos faltando: ${missing_files[*]}"
fi

echo ""
echo "🚀 PRÓXIMOS PASSOS PARA DEPLOY NO DEV BOARD:"
echo "1. Fazer commit e push das mudanças:"
echo "   git add ."
echo "   git commit -m 'Add Dev Board deployment scripts'"
echo "   git push origin main"
echo ""
echo "2. No Google Dev Board (AA1):"
echo "   ssh mendel@IP_DO_DEVBOARD"
echo "   git clone https://github.com/DaviBaechtold/Sistema-carro-voz.git"
echo "   cd Sistema-carro-voz"
echo "   ./deploy_devboard.sh"
echo ""
echo "3. Para gerenciamento remoto:"
echo "   ./remote_manager.sh"
echo ""
echo "🎯 Projeto pronto para deployment no carro! 🚗"
