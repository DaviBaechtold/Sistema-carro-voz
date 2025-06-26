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

Todas as dependências Python estão listadas em `requirements.txt`.

## Observações
- Recomendado para sistemas Linux (testado em Ubuntu/Debian).
- Otimizado para Google Dev Board (AA1) com microfone M-305, mas funciona em qualquer PC Linux com microfone.

## Licença
Consulte o arquivo LICENSE para detalhes.


