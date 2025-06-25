# Changelog

## [1.3.0] - 2025-06-25 - Limpeza Final e Consolidação

### 🧹 Limpeza Completa do Projeto
- ✅ **Arquivos obsoletos removidos**:
  - `voice_assistant_devboard.py` (duplicado da raiz)
  - `deploy_devboard.sh` (substituído por `devboard/install.sh`)
  - `setup_network.sh` (integrado no `devboard/install.sh`)
  - `remote_manager.sh` (substituído por `devboard/remote.sh`)
  - `check_project.sh` (funcionalidade desnecessária)

### 📝 Documentação Corrigida
- ✅ **README.md principal** - Estrutura corrompida corrigida
- ✅ **Badges organizados** - Headers e links corrigidos
- ✅ **Estrutura de projeto atualizada** - Reflete organização atual
- ✅ **Scripts documentados corretamente** - Separação clara entre desktop e Dev Board

### 🎯 Estrutura Final Consolidada
- ✅ **Raiz**: Apenas arquivos essenciais (`voice_assistant.py`, `setup.sh`, `run.sh`)
- ✅ **Pasta devboard/**: Todos os arquivos específicos do Dev Board organizados
- ✅ **Eliminação de redundâncias**: Código duplicado removido
- ✅ **Responsabilidades claras**: Cada script com função específica

## [1.2.0] - 2025-06-25 - Organização e Otimização

### �️ Reorganização do Projeto
- ✅ **Pasta devboard/**: Todos os arquivos relacionados ao Dev Board organizados
- ✅ **Scripts consolidados**: 
  - `devboard/install.sh` - Instalação completa e automatizada
  - `devboard/manage.sh` - Gerenciamento local no Dev Board
  - `devboard/remote.sh` - Gerenciamento remoto via SSH
- ✅ **Documentação modular**:
  - `devboard/README.md` - Guia rápido de uso
  - `devboard/DEPLOY.md` - Instalação detalhada  
  - `devboard/TROUBLESHOOTING.md` - Solução de problemas
- ✅ **Limpeza do projeto**: Removidos arquivos redundantes e duplicados
- ✅ **Estrutura clara**: Separação entre core do assistente e ambiente Dev Board

### 🔧 Melhorias dos Scripts
- ⚡ **install.sh**: Combina deploy, configuração de rede, setup de serviço
- 🔧 **manage.sh**: Menu interativo para gerenciamento local completo
- 📡 **remote.sh**: Administração remota via SSH com menu intuitivo
- 🧹 **Eliminação de redundâncias**: Funções duplicadas unificadas

## [1.1.0] - 2025-06-25 - Dev Board Release

### 🚀 Novas Funcionalidades - Google Dev Board (AA1)
- ✅ **Deploy automatizado**: Instalação no Dev Board
- ✅ **Versão otimizada**: `voice_assistant_devboard.py` com otimizações específicas
- ✅ **Auto-inicialização**: Serviço systemd para iniciar com o sistema
- ✅ **Monitoramento de temperatura**: Proteção contra superaquecimento
- ✅ **Configuração de rede**: Script `setup_network.sh` para WiFi/hotspot
- ✅ **Gerenciamento remoto**: Script `remote_manager.sh` para administração via SSH
- ✅ **Logs rotativos**: Prevenção de enchimento do SD card
- ✅ **Recuperação automática**: Reinício em caso de falhas

### 🔧 Melhorias do Sistema
- ⚡ **Performance otimizada**: Configurações específicas para ambiente embarcado
- 🌡️ **Monitoramento térmico**: Sistema de proteção contra superaquecimento
- 📊 **Logging avançado**: Sistema de logs estruturado com rotação
- 🔄 **Auto-recovery**: Sistema de recuperação automática de erros
- 📶 **Conectividade robusta**: Verificação e reestabelecimento de conexão

### 📋 Recursos para Carro
- 🚗 **Inicialização inteligente**: Aguarda estabilização do sistema no carro
- 🔊 **Áudio otimizado**: Configurações específicas para ambiente ruidoso
- ⚡ **Economia de energia**: Gerenciamento inteligente de recursos
- 🛡️ **Proteção de hardware**: Monitoramento de temperatura e memória

### 📚 Documentação
- 📖 **DEVBOARD_DEPLOY.md**: Guia completo de instalação no Dev Board
- 🔧 **Scripts de automação**: Deploy, configuração e gerenciamento
- 📊 **Monitoramento**: Ferramentas de status e diagnóstico

## [1.0.0] - 2025-06-25 - Release Inicial

### Funcionalidades
- ✅ Comando único: Wake word + comando na mesma frase
- ✅ Reconhecimento de voz em português brasileiro via Google Speech API
- ✅ Síntese de voz com vozes portuguesas naturais
- ✅ Comandos para chamadas, música, navegação, mensagens e sistema
- ✅ Suporte a múltiplas wake words: "Assistente", "OK Google", "Hey Google", "Carro"
- ✅ Instalação automatizada de dependências e vozes TTS
- ✅ Scripts de configuração e execução simplificados

### Comandos Disponíveis
- **Chamadas**: ligar, atender, desligar, discagem
- **Música**: tocar, controlar volume, mudar faixas
- **Navegação**: navegar para destino, rotas, localização
- **Mensagens**: enviar, ler mensagens
- **Sistema**: ajuda, status

### Compatibilidade
- Python 3.8+
- Linux (Ubuntu/Debian/Fedora/Arch)
- Microfones USB (testado com M-305)
- Google Dev Board (AA1)

### Estrutura
- `voice_assistant.py` - Código principal
- `setup.sh` - Configuração completa
- `run.sh` - Execução rápida
- `requirements.txt` - Dependências
- Documentação completa em README.md
