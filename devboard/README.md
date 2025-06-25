# 📟 Google Dev Board (AA1) - Assistente de Voz para Carro

Scripts e configurações específicas para instalar o assistente de voz no Google Dev Board (AA1) para uso permanente no carro.

## 🎯 Por que Google Dev Board?

- ✅ **Linux embarcado** (Mendel Linux baseado em Debian)
- ✅ **Edge TPU** para IA/ML (futuras melhorias)
- ✅ **GPIO** para integração com sistemas do carro
- ✅ **WiFi/Bluetooth** integrados
- ✅ **Baixo consumo** de energia
- ✅ **Tamanho compacto** para instalação no carro
- ✅ **Confiável** para uso 24/7 no ambiente automotivo

## 🚀 Instalação Rápida

### 1. Conectar ao Dev Board
```bash
ssh mendel@IP_DO_DEVBOARD
```

### 2. Clonar e instalar
```bash
git clone https://github.com/DaviBaechtold/Sistema-carro-voz.git
cd Sistema-carro-voz/devboard
chmod +x *.sh
./install.sh
```

### 3. Reiniciar
```bash
sudo reboot
```

Pronto! O assistente iniciará automaticamente após o reboot.

## 📁 Estrutura da Pasta DevBoard

```
devboard/
├── README.md              # 📚 Este guia rápido
├── DEPLOY.md              # 📖 Guia detalhado de instalação
├── TROUBLESHOOTING.md     # 🔧 Solução de problemas
├── install.sh             # 🚀 Instalação completa automatizada
├── manage.sh              # 🔧 Gerenciamento local no Dev Board
├── remote.sh              # 📡 Gerenciamento remoto via SSH
├── utils.sh               # 🛠️ Funções utilitárias compartilhadas
└── voice_assistant_devboard.py # 📟 Versão otimizada para Dev Board
```

### 🔨 Scripts Principais

- **`install.sh`**: Instalação completa e automatizada
  - Configura dependências, áudio, rede, serviço systemd
  - Menu interativo para diferentes tipos de instalação
  
- **`manage.sh`**: Gerenciamento local (execute no Dev Board)
  - Status do sistema, logs, controle do serviço
  - Configuração WiFi, teste de áudio, atualizações
  
- **`remote.sh`**: Gerenciamento remoto (execute no seu PC)
  - Administração via SSH, deploy, monitoramento
  
- **`utils.sh`**: Funções compartilhadas
  - Evita duplicação de código entre scripts
  - Funções coloridas, checagem de sistema, WiFi, etc.

## 🔧 Gerenciamento

### No Dev Board
```bash
cd Sistema-carro-voz/devboard
./manage.sh
```

### Remotamente (do seu computador)
```bash
cd devboard
./remote.sh
```

## 📋 Funcionalidades Específicas

- ✅ **Auto-inicialização** com systemd service
- ✅ **Monitoramento térmico** (proteção contra superaquecimento)
- ✅ **Logs rotativos** (evita enchimento do SD card)
- ✅ **Recuperação automática** de falhas
- ✅ **Configuração de rede** (WiFi + hotspot)
- ✅ **Gerenciamento remoto** via SSH
- ✅ **Otimizações para carro** (inicialização inteligente, áudio adaptado)

## 🌡️ Monitoramento

O sistema monitora automaticamente:
- **Temperatura** do CPU (< 75°C)
- **Uso de memória** (< 80%)
- **Conectividade** de rede
- **Status dos serviços**

## 🔊 Configuração de Áudio

O sistema configura automaticamente:
- Microfone USB (M-305 ou similar)
- Saída de áudio para carro
- Ajuste de volume otimizado
- Supressão de ruído ambiente

## 📞 Suporte

- 📖 **Documentação completa**: `DEPLOY.md`
- 🔧 **Solução de problemas**: `TROUBLESHOOTING.md`
- 🐛 **Issues**: [GitHub Issues](https://github.com/DaviBaechtold/Sistema-carro-voz/issues)
- 📧 **Contato direto**: Para suporte específico do Dev Board
