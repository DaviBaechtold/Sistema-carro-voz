# 🛠️ Troubleshooting - Google Dev Board (AA1)

Soluções para problemas comuns na instalação e uso do assistente de voz no Dev Board.

## 🚨 Problemas de Instalação

### ❌ "Não é um Dev Board"
```bash
# Erro: Script detecta que não está em um Dev Board
# Solução: Execute apenas no Google Dev Board (AA1)
ssh mendel@IP_DO_DEVBOARD
cd Sistema-carro-voz/devboard
./install.sh
```

### ❌ Falha na instalação de dependências
```bash
# Erro: apt install falha
# Solução: Verificar conectividade e espaço em disco
ping google.com
df -h
sudo apt update --fix-missing
```

### ❌ Erro de permissões
```bash
# Erro: Permission denied
# Solução: Verificar usuário e grupos
whoami  # deve ser 'mendel'
groups  # deve incluir 'audio'
sudo usermod -a -G audio,plugdev mendel
```

## 🎤 Problemas de Áudio

### ❌ Microfone não detectado
```bash
# Verificar dispositivos USB
lsusb | grep -i audio

# Verificar dispositivos ALSA
arecord -l

# Se não aparecer:
# 1. Reconecte o microfone USB
# 2. Teste em outra porta USB
# 3. Verifique se o microfone funciona em outro dispositivo
```

### ❌ Erro "No such device"
```bash
# Reconfigurar ALSA
sudo rm /etc/asound.conf
cd Sistema-carro-voz/devboard
./manage.sh
# Escolha opção para reconfigurar áudio
```

### ❌ TTS sem som
```bash
# Testar TTS manualmente
espeak -v pt-br "teste de voz"

# Se não funcionar:
sudo apt install --reinstall espeak espeak-data

# Verificar saída de áudio
aplay /usr/share/sounds/alsa/Front_Left.wav
```

## 🌐 Problemas de Rede

### ❌ WiFi não conecta
```bash
# Verificar status WiFi
iwconfig
sudo systemctl status networking

# Reconfigurar WiFi
sudo nano /etc/wpa_supplicant/wpa_supplicant.conf
sudo systemctl restart networking

# Verificar conectividade
ping -c 3 8.8.8.8
```

### ❌ Reconhecimento de voz falha
```bash
# Erro: No internet connection
# O reconhecimento de voz precisa de internet

# Verificar:
curl -I https://www.google.com

# Se falhar, reconfigurar rede:
./manage.sh  # Opção 6 - Configurar WiFi
```

## 🔧 Problemas do Serviço

### ❌ Serviço não inicia
```bash
# Verificar status detalhado
sudo systemctl status voice-assistant-car.service -l

# Ver logs completos
sudo journalctl -u voice-assistant-car.service --no-pager

# Reiniciar serviço
sudo systemctl restart voice-assistant-car.service
```

### ❌ Serviço trava ou para
```bash
# Verificar se está rodando
sudo systemctl is-active voice-assistant-car.service

# Se inativo, verificar logs:
sudo journalctl -u voice-assistant-car.service -n 50

# Reiniciar manualmente:
sudo systemctl restart voice-assistant-car.service
```

### ❌ Auto-inicialização não funciona
```bash
# Verificar se está habilitado
sudo systemctl is-enabled voice-assistant-car.service

# Se não estiver habilitado:
sudo systemctl enable voice-assistant-car.service

# Testar boot:
sudo reboot
```

## 🌡️ Problemas de Performance

### ⚠️ Temperatura alta
```bash
# Verificar temperatura
cat /sys/class/thermal/thermal_zone0/temp | awk '{print $1/1000}'

# Se > 70°C:
# 1. Verificar ventilação do Dev Board
# 2. Reduzir carga (fechar apps desnecessários)
# 3. O sistema se protege automaticamente

# Monitorar:
watch -n 5 'cat /sys/class/thermal/thermal_zone0/temp | awk "{print \$1/1000\"°C\"}"'
```

### 🐌 Performance lenta
```bash
# Verificar uso de CPU/memória
htop

# Verificar espaço em disco
df -h

# Verificar processos:
ps aux | grep python

# Se necessário, reiniciar:
sudo reboot
```

## 📊 Problemas de Logs

### 📝 SD Card cheio
```bash
# Verificar espaço
df -h

# Limpar logs antigos
sudo journalctl --vacuum-time=7d

# Verificar logrotate
sudo logrotate -f /etc/logrotate.d/voice-assistant
```

### 📄 Logs não aparecem
```bash
# Verificar se serviço está logando
sudo journalctl -u voice-assistant-car.service -f

# Se vazio, verificar configuração:
sudo systemctl cat voice-assistant-car.service

# Reiniciar logging:
sudo systemctl restart systemd-journald
```

## 🔐 Problemas de Conexão Remota

### ❌ SSH não conecta
```bash
# Do seu computador:
ping IP_DO_DEVBOARD

# Se ping OK mas SSH falha:
# No Dev Board (via monitor/teclado):
sudo systemctl status ssh
sudo systemctl restart ssh

# Verificar firewall:
sudo ufw status
```

### 🔑 Acesso negado
```bash
# Verificar usuário correto:
ssh mendel@IP_DO_DEVBOARD

# Se ainda falhar, verificar chaves SSH:
ssh-keygen -R IP_DO_DEVBOARD  # Remove chave antiga
ssh mendel@IP_DO_DEVBOARD     # Reconecta
```

## 🆘 Recuperação de Emergência

### 💾 Restaurar backup
```bash
# Se você fez backup:
scp backup.tar.gz mendel@IP_DO_DEVBOARD:/home/mendel/
ssh mendel@IP_DO_DEVBOARD
tar -xzf backup.tar.gz
sudo systemctl restart voice-assistant-car.service
```

### 🔄 Reinstalação completa
```bash
# Em caso de problemas graves:
ssh mendel@IP_DO_DEVBOARD
cd Sistema-carro-voz

# Parar serviço
sudo systemctl stop voice-assistant-car.service
sudo systemctl disable voice-assistant-car.service

# Limpar instalação anterior
sudo rm /etc/systemd/system/voice-assistant-car.service
sudo rm /etc/asound.conf
rm -rf venv/

# Reinstalar
git pull origin main
cd devboard
./install.sh
```

### 🏭 Reset de fábrica (último recurso)
```bash
# ATENÇÃO: Isso apaga TUDO do Dev Board
# Use apenas em casos extremos

# Reflash do sistema Mendel Linux
# Siga: https://coral.ai/docs/dev-board/reflash/
```

## 📞 Ainda com problemas?

1. **Verificar logs detalhados:**
   ```bash
   ./manage.sh  # Opção 1 - Status completo
   ```

2. **Coletar informações para suporte:**
   ```bash
   # Executar no Dev Board
   uname -a > debug_info.txt
   lsusb >> debug_info.txt
   arecord -l >> debug_info.txt
   sudo systemctl status voice-assistant-car.service >> debug_info.txt
   sudo journalctl -u voice-assistant-car.service -n 50 >> debug_info.txt
   ```

3. **Abrir issue no GitHub:**
   - Anexar arquivo `debug_info.txt`
   - Descrever o problema em detalhes
   - Mencionar quando o problema começou

4. **Suporte da comunidade Coral:**
   - [Coral Community Forum](https://groups.google.com/forum/#!forum/coral-support)
   - [Documentação Oficial](https://coral.ai/docs/dev-board/)
