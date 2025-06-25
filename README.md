# 🚗 Assistente de Voz para Carro

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)## 📁 Estrutura do Projeto

```
assistente-voz-carro/
├── voice_assistant.py          # 🎯 Código principal do assistente
├── setup.sh                   # ⚙️ Script de configuração completa
├── run.sh                     # 🚀 Script de execução rápida
├── requirements.txt           # 📦 Dependências Python
├── README.md                  # 📚 Documentação principal
├── CHANGELOG.md               # 📝 Histórico de versões
├── LICENSE                    # 📄 Licença MIT
├── .gitignore                # 🧹 Configuração Git
└── devboard/                  # 📟 Arquivos específicos do Dev Board
    ├── README.md              # 📚 Guia rápido Dev Board
    ├── DEPLOY.md              # 📟 Deploy detalhado
    ├── TROUBLESHOOTING.md     # 🔧 Solução de problemas
    ├── install.sh             # 🚀 Instalação automática
    ├── manage.sh              # 🔧 Gerenciamento local
    ├── remote.sh              # 📡 Gerenciamento remoto
    └── voice_assistant_devboard.py # 📟 Versão otimizada
```://img.shields.io/badge/platform-linux-lightgrey.svg)
![Dev Board](https://img.shields.io/badge/Google_Dev_Board-AA1-orange.svg)

Um assistente de voz inteligente desenvolvido para uso automotivo com comandos em português brasileiro. Projetado especificamente para Google Dev Board (AA1) com microfone M-305, mas compatível com qualquer sistema Linux.

## ✨ Características

- 🎯 **Comando único**: Fale wake word + comando na mesma frase
- 🇧🇷 **Português brasileiro**: Reconhecimento e síntese de voz nativos
- 🚗 **Focado em carro**: Comandos otimizados para uso durante direção
- 🔊 **Vozes naturais**: Suporte a múltiplas engines TTS
- ⚡ **Configuração fácil**: Script automatizado de instalação

## 🚀 Início Rápido

## 🚀 Início Rápido

### Pré-requisitos
- Python 3.8+
- Sistema Linux (Ubuntu/Debian recomendado)
- Microfone funcional
- Conexão com internet (para reconhecimento de voz)

### Instalação

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/seu-usuario/assistente-voz-carro.git
   cd assistente-voz-carro
   ```

2. **Configure o ambiente:**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   # Escolha opção 1 para configuração completa
   ```

3. **Execute o assistente:**
   ```bash
   ./run.sh  # Execução rápida
   # OU
   ./setup.sh  # Menu completo (opção 4)
   ```

## 🎯 Como Usar

### Comandos Básicos
Fale a **wake word** seguida do **comando** na mesma frase:

```
"Assistente, tocar música"
"OK Google, ligar para João"
"Carro, navegar para casa"
"Hey Google, aumentar volume"
```

### Wake Words Disponíveis
- `"Assistente"`
- `"OK Google"`
- `"Hey Google"`
- `"Carro"`

## 📋 Comandos Disponíveis

### 📞 Chamadas
- `"ligar para [nome]"` - Iniciar chamada
- `"atender"` - Atender chamada recebida
- `"desligar chamada"` - Encerrar chamada
- `"discagem [número]"` - Discagem rápida

### 🎵 Controle de Música
- `"tocar música"` - Reproduzir música
- `"tocar [artista/música]"` - Tocar conteúdo específico
- `"aumentar volume"` / `"diminuir volume"`
- `"próxima"` / `"anterior"` - Controlar faixas

### 🗺️ Navegação
- `"navegar para [destino]"` - Iniciar navegação
- `"rotas alternativas"` - Mostrar opções de rota
- `"onde estou"` - Localização atual
- `"cancelar rota"` - Parar navegação

### 💬 Mensagens
- `"enviar mensagem para [nome]"` - Enviar mensagem
- `"última mensagem"` - Ler última mensagem recebida
- `"ler mensagem"` - Verificar mensagens não lidas

### ⚙️ Sistema
- `"ajuda"` - Listar comandos disponíveis
- `"status"` - Status do sistema

## �️ Configuração Avançada

### Instalação de Vozes Naturais
```bash
./setup.sh
# Escolha opção 2 para instalar vozes TTS de melhor qualidade
```

### Teste do Sistema
```bash
./setup.sh
# Escolha opção 3 para testar microfone e vozes
```

## � Deploy para Google Dev Board (AA1)

### 🚀 Instalação Automática no Dev Board
Para instalar permanentemente no Google Dev Board para uso no carro:

1. **Conecte-se ao Dev Board:**
   ```bash
   ssh mendel@IP_DO_DEVBOARD
   ```

2. **Clone e execute o deploy:**
   ```bash
   git clone https://github.com/DaviBaechtold/Sistema-carro-voz.git
   cd Sistema-carro-voz/devboard
   chmod +x install.sh
   ./install.sh
   ```

3. **Gerenciar localmente (no Dev Board):**
   ```bash
   ./manage.sh
   ```

4. **Reinicie o Dev Board:**
   ```bash
   sudo reboot
   ```

### 🔧 Gerenciamento Remoto
Para gerenciar o assistente remotamente do seu computador:
```bash
cd devboard
./remote.sh
```

### 📋 Características do Deploy no Dev Board:
- ✅ **Auto-inicialização**: Inicia automaticamente com o sistema
- ✅ **Monitoramento de temperatura**: Proteção contra superaquecimento  
- ✅ **Logs rotativos**: Evita enchimento do SD card
- ✅ **Recuperação automática**: Reinicia em caso de erro
- ✅ **Otimizações para carro**: Configurações específicas para ambiente automotivo
- ✅ **Gerenciamento remoto**: Scripts para monitoramento via SSH

### 📖 Documentação Completa do Dev Board:
Veja a pasta `devboard/` para guias completos:
- [devboard/README.md](devboard/README.md) - Guia rápido de uso
- [devboard/DEPLOY.md](devboard/DEPLOY.md) - Instalação detalhada
- [devboard/TROUBLESHOOTING.md](devboard/TROUBLESHOOTING.md) - Solução de problemas

## �📁 Estrutura do Projeto

```
assistente-voz-carro/
├── voice_assistant.py          # 🎯 Código principal do assistente
├── voice_assistant_devboard.py # 📟 Versão otimizada para Dev Board
├── setup.sh                   # ⚙️ Script de configuração completa
├── run.sh                     # 🚀 Script de execução rápida
├── deploy_devboard.sh         # 📟 Deploy automatizado para Dev Board
├── setup_network.sh           # 📶 Configuração de rede do Dev Board
├── remote_manager.sh          # 🔧 Gerenciamento remoto via SSH
├── requirements.txt           # 📦 Dependências Python
├── README.md                  # 📚 Documentação principal
├── DEVBOARD_DEPLOY.md         # 📟 Guia completo do Dev Board
├── CHANGELOG.md               # 📝 Histórico de versões
├── LICENSE                    # 📄 Licença MIT
└── .gitignore                # 🧹 Configuração Git
```

### Scripts Principais

- **`run.sh`** - Execução rápida do assistente (após configuração inicial)
- **`setup.sh`** - Menu completo com configuração, testes e execução
- **`deploy_devboard.sh`** - Deploy automatizado para Google Dev Board (AA1)
- **`remote_manager.sh`** - Gerenciamento remoto do Dev Board via SSH
- **`setup_network.sh`** - Configuração de WiFi/rede no Dev Board

## 🔧 Dependências

- **SpeechRecognition** - Reconhecimento de voz via Google
- **pyttsx3** - Síntese de voz text-to-speech
- **pyaudio** - Captura de áudio do microfone

## 🐛 Solução de Problemas

### Microfone não detectado
```bash
# Listar dispositivos de áudio
arecord -l

# Testar gravação
arecord -d 3 test.wav && aplay test.wav
```

### Vozes robóticas
```bash
./setup.sh
# Escolha opção 2 para instalar vozes mais naturais
```

### Erro de permissão de áudio
```bash
sudo usermod -a -G audio $USER
# Reinicie a sessão após executar
```

## 🤝 Contribuindo

1. Fork o projeto
2. Crie sua feature branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## � Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🙏 Agradecimentos

- [SpeechRecognition](https://github.com/Uberi/speech_recognition) pela biblioteca de reconhecimento de voz
- [pyttsx3](https://github.com/nateshmbhat/pyttsx3) pela síntese de voz
- Comunidade Python pela excelente documentação

## 📞 Suporte

- 🐛 **Bugs**: Abra uma [issue](https://github.com/seu-usuario/assistente-voz-carro/issues)
- 💡 **Sugestões**: Use as [discussions](https://github.com/seu-usuario/assistente-voz-carro/discussions)
- 📧 **Contato**: [seu-email@exemplo.com](mailto:seu-email@exemplo.com)

## ⭐ Star o Projeto

Se este projeto te ajudou, considere dar uma ⭐! Isso ajuda outros desenvolvedores a encontrar o projeto.

---


