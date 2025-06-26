# 🚗 Assistente de Voz para Carro

Um sistema de assistente de voz inteligente desenvolvido para uso automotivo, com comandos em português brasileiro. O objetivo é permitir controle por voz de funções do carro ou de sistemas embarcados, tornando a experiência de direção mais segura e prática.

## Funcionalidades
- **Reconhecimento de voz**: Ativado por wake word (ex: "ok google", "assistente", "carro").
- **Respostas por voz**: Utiliza síntese de voz natural (TTS).
- **Comandos otimizados para carro**: Foco em comandos úteis durante a direção.
- **Fácil instalação**: Scripts automáticos para configuração e execução.

## Estrutura do Projeto
```
Sistem-mic/
├── requirements.txt        # Dependências Python
├── run.sh                 # Inicialização rápida do assistente
├── setup.sh               # Configuração completa do ambiente
└── voice_assistant.py      # Código principal do assistente de voz
```

## Instalação e Uso

1. **Configuração inicial**
   ```bash
   cd Sistem-mic
   ./setup.sh
   ```
   O script `setup.sh` instala dependências do sistema, Python, bibliotecas de áudio e prepara o ambiente virtual.

2. **Executar o assistente**
   ```bash
   ./run.sh
   ```
   O script ativa o ambiente virtual e inicia o assistente de voz.

## Dependências
- Python 3.8+
- [SpeechRecognition](https://pypi.org/project/SpeechRecognition/)
- [PyAudio](https://pypi.org/project/PyAudio/)
- [pyttsx3](https://pypi.org/project/pyttsx3/)

## Inicialização automática como serviço (systemd)

Para que o assistente inicie automaticamente ao ligar o sistema (ex: Google Dev Board ou Linux embarcado):

1. Copie o arquivo `voice-assistant.service` para o diretório de serviços do systemd:
   ```bash
   sudo nano /etc/systemd/system/voice-assistant.service
   # Cole o conteúdo do arquivo e salve
   ```
2. Ative o serviço para inicializar automaticamente:
   ```bash
   sudo systemctl enable voice-assistant.service
   sudo systemctl start voice-assistant.service
   ```

Assim, o assistente será iniciado automaticamente após o boot.

## Opção 2: Usando Arduino Nano 2040 Connect como Microfone

Agora o projeto também suporta o uso de dois Arduinos Nano 2040 Connect como microfones remotos. O áudio capturado pelo Arduino é enviado para o Dev Board (ou outro sistema Linux), que executa todo o processamento de voz normalmente.

### Estrutura da solução Arduino
```
Sytem-arduino/
├── arduino-microphone.ino         # Código para Arduino Nano 2040 Connect (envio de áudio)
├── requirements_arduino.txt       # Dependências Python para integração
├── setup_arduino.sh               # Script de configuração para uso com Arduino
└── voice_assistent_arduino.py     # Código Python para receber/processar áudio do Arduino
```

### Como usar com Arduino
1. Grave o `arduino-microphone.ino` nos Arduinos Nano 2040 Connect.
2. No Dev Board/Linux, execute:
   ```bash
   cd Sytem-arduino
   ./setup_arduino.sh
   ```
3. Siga o menu para testar a conexão e rodar o assistente usando o áudio vindo do Arduino (por WiFi ou Serial).

> O restante do processamento de voz, comandos e respostas continua igual ao modo tradicional.

## Observações
- Recomendado para sistemas Linux (testado em Ubuntu/Debian).
- Otimizado para Google Dev Board (AA1) com microfone M-305, mas funciona em qualquer PC Linux com microfone.

## Licença
Consulte o arquivo LICENSE para detalhes.


