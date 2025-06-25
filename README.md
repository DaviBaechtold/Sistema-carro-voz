# 🚗 Assistente de Voz para Carro

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg## 🛠️ Configuração Avançada

### Instalação de Vozes Naturais
Para melhorar a qualidade da síntese de voz:
```bash
./setup.sh
# Escolha opção 2 para instalar vozes TTS de melhor qualidade
```

### Teste do Sistema
Para verificar microfone e vozes:
```bash
./setup.sh
# Escolha opção 3 para testar microfone e vozes
```

### Execução Manual
Se preferir executar diretamente:
```bash
source venv/bin/activate
python3 voice_assistant.py
```https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-linux-lightgrey.svg)

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

## 📁 Estrutura do Projeto

```
assistente-voz-carro/
├── voice_assistant.py      # 🎯 Código principal do assistente
├── setup.sh               # ⚙️ Script de configuração completa
├── run.sh                 # 🚀 Script de execução rápida
├── requirements.txt       # 📦 Dependências Python
├── README.md              # 📚 Documentação
├── LICENSE                # 📄 Licença MIT
└── .gitignore            # 🧹 Configuração Git
```

### Scripts Principais

- **`run.sh`** - Execução rápida do assistente (após configuração inicial)
- **`setup.sh`** - Menu completo com configuração, testes e execução
- **`voice_assistant.py`** - Código principal (pode ser executado diretamente)

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


