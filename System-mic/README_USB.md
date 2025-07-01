# 🎤 Assistente de Voz - Microfone USB M-305

Sistema de assistente de voz para carro usando Google Dev Board (AA1) com microfone USB M-305.

> **Este guia refere-se ao sistema USB. Execute todos os comandos dentro da pasta `System-mic/` do projeto.**

## 📋 Requisitos

- Google Dev Board (AA1)
- Microfone USB M-305 ou similar
- Conexão com internet (WiFi ou Ethernet)
- Python 3.7.3 (já instalado no Dev Board)

## 🚀 Instalação Rápida

1. **Conecte ao Dev Board via SSH:**
```bash
ssh mendel@IP_DO_DEVBOARD
```

2. **Clone o repositório:**
```bash
git clone https://github.com/DaviBaechtold/Sistema-carro-voz.git
cd Sistema-carro-voz/System-mic
```

3. **Execute o setup:**
```bash
chmod +x setup.sh
./setup.sh
```

4. **Escolha opção 1 (Configuração inicial completa)**

5. **Teste o sistema (opção 3)**

6. **Execute o assistente (opção 4)**

## 🔧 Configuração Detalhada

### Primeira Instalação

```bash
./setup.sh
# Escolha 1 - Instala todas as dependências
# Escolha 2 - Instala vozes em português
# Escolha 3 - Testa microfone e vozes
```

### Inicialização Automática

Para o assistente iniciar com o sistema:

```bash
sudo nano /etc/systemd/system/voice-assistant.service
```

Cole o conteúdo:
```ini
[Unit]
Description=Voice Assistant
After=network.target sound.target

[Service]
Type=simple
User=mendel
WorkingDirectory=/home/mendel/Sistema-carro-voz/System-mic
Environment="PATH=/home/mendel/Sistema-carro-voz/System-mic/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
ExecStart=/home/mendel/Sistema-carro-voz/System-mic/venv/bin/python /home/mendel/Sistema-carro-voz/System-mic/voice_assistant.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Ative o serviço:
```bash
sudo systemctl enable voice-assistant.service
sudo systemctl start voice-assistant.service
```

## 🎯 Como Usar

### Comandos de Voz

Fale a **wake word** + **comando** na mesma frase:

- "Assistente, tocar música"
- "OK Google, ligar para João"
- "Carro, navegar para casa"
- "Hey Google, aumentar volume"

### Wake Words Disponíveis
- Assistente
- OK Google  
- Hey Google
- Carro

### Comandos Suportados

**📞 Chamadas:**
- ligar para [nome]
- atender
- desligar chamada
- discagem [número]

**🎵 Música:**
- tocar música
- tocar [artista/música]
- aumentar/diminuir volume
- próxima/anterior

**🗺️ Navegação:**
- navegar para [destino]
- rotas alternativas
- onde estou
- cancelar rota

**💬 Mensagens:**
- enviar mensagem para [nome]
- última mensagem
- ler mensagem

**⚙️ Sistema:**
- ajuda
- status

## 🔍 Solução de Problemas

### Microfone não detectado
```bash
# Verificar se M-305 está conectado
lsusb | grep Audio

# Listar dispositivos de áudio
arecord -l
```

### Erro de FLAC
```bash
sudo apt install flac
```

### Verificar logs do serviço
```bash
sudo systemctl status voice-assistant
sudo journalctl -u voice-assistant -f
```

### Testar microfone manualmente
```bash
# Gravar 3 segundos
arecord -d 3 -f cd test.wav
# Reproduzir
aplay test.wav
```

## 📊 Monitoramento

### Status do serviço
```bash
sudo systemctl status voice-assistant
```

### Logs em tempo real
```bash
sudo journalctl -u voice-assistant -f
```

### Reiniciar serviço
```bash
sudo systemctl restart voice-assistant
```

## 🛠️ Manutenção

### Atualizar código
```bash
cd ~/Sistema-carro-voz/System-mic
git pull
sudo systemctl restart voice-assistant
```

### Limpar logs antigos
```bash
sudo journalctl --vacuum-time=7d
```

### Verificar uso de disco
```bash
df -h
```

## 📱 Acesso Remoto

Para gerenciar do seu computador:
```bash
ssh mendel@IP_DO_DEVBOARD
sudo systemctl status voice-assistant
```