#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import speech_recognition as sr
import pyttsx3
import time
import threading
import os
import re
import warnings
import sys

# Redirecionar stderr do ALSA para /dev/null ANTES de qualquer importação de áudio
class SuppressStderr:
    def __init__(self):
        self.null_fd = os.open(os.devnull, os.O_RDWR)
        self.save_fd = os.dup(2)
        
    def __enter__(self):
        os.dup2(self.null_fd, 2)
        
    def __exit__(self, *args):
        os.dup2(self.save_fd, 2)
        os.close(self.null_fd)
        os.close(self.save_fd)

# Suprimir todos os logs do ALSA
os.environ['ALSA_PCM_CARD'] = '2'
os.environ['ALSA_PCM_DEVICE'] = '0'
warnings.filterwarnings("ignore")

class VoiceAssistant:
    def __init__(self):
        # Wake word para ativação
        self.wake_words = ['ok google', 'hey google', 'assistente', 'carro']
        self.is_awake = False
        self.awake_timeout = 10  # segundos para voltar a dormir
        self.last_command_time = 0
        self.always_require_wake_word = True  # Sempre exigir wake word
        
        # Detectar microfone M-305 especificamente
        self.microphone_index = self.find_m305_microphone()
        
        # Inicializar reconhecimento de voz
        self.recognizer = sr.Recognizer()
        if self.microphone_index is not None:
            self.microphone = sr.Microphone(device_index=self.microphone_index)
        else:
            print("⚠️ M-305 não encontrado, usando microfone padrão")
            self.microphone = sr.Microphone()
        
        # Inicializar síntese de voz
        with SuppressStderr():
            self.tts = pyttsx3.init()
        self.setup_tts()
        
        # Configurar microfone
        self.setup_microphone()
        
        # Comandos para carro - organizados por categoria
        self.commands = {
            # Chamadas
            'ligar para': self.make_call,
            'atender': self.answer_call,
            'desligar chamada': self.end_call,
            'discagem': self.speed_dial,
            
            # Música e Mídia
            'tocar música': self.play_music,
            'tocar': self.play_specific,
            'aumentar volume': self.volume_up,
            'diminuir volume': self.volume_down,
            'próxima': self.next_track,
            'anterior': self.previous_track,
            
            # Navegação
            'navegar para': self.navigate_to,
            'rotas alternativas': self.alternative_routes,
            'onde estou': self.current_location,
            'cancelar rota': self.cancel_route,
            
            # Mensagens
            'enviar mensagem': self.send_message,
            'última mensagem': self.read_last_message,
            'ler mensagem': self.read_message,
            
            # Sistema
            'ajuda': self.help,
            'status': self.status
        }
        
        self.is_listening = False
        
    def setup_tts(self):
        """Configura síntese de voz"""
        voices = self.tts.getProperty('voices')
        
        # Procurar voz em português
        portuguese_voice = None
        if voices:
            for voice in voices:
                # Procurar vozes que contenham 'pt', 'brazil', 'portuguese' no nome
                if any(keyword in voice.name.lower() for keyword in ['pt', 'brazil', 'portuguese', 'brasil']):
                    portuguese_voice = voice.id
                    print(f"Voz em português encontrada: {voice.name}")
                    break
        
        # Se encontrou voz em português, usar ela; senão usar a primeira
        if portuguese_voice:
            self.tts.setProperty('voice', portuguese_voice)
        elif voices:
            self.tts.setProperty('voice', voices[0].id)
            print("Usando voz padrão (pode estar em inglês)")
        
        # Configurar velocidade e volume para voz mais natural
        self.tts.setProperty('rate', 160)  # Velocidade mais lenta para soar mais natural
        self.tts.setProperty('volume', 0.85)  # Volume um pouco menor
        
        # Tentar usar voz feminina se disponível (geralmente mais natural)
        if voices:
            for voice in voices:
                voice_name = voice.name.lower()
                # Procurar vozes femininas brasileiras/portuguesas
                if any(keyword in voice_name for keyword in ['female', 'feminina', 'woman', 'maria', 'ana', 'lucia']):
                    if any(lang in voice_name for lang in ['pt', 'brazil', 'portuguese', 'brasil']):
                        self.tts.setProperty('voice', voice.id)
                        print(f"Voz feminina brasileira encontrada: {voice.name}")
                        break
        
    def find_m305_microphone(self):
        """Encontra o microfone M-305 especificamente"""
        print("🔍 Procurando microfone M-305...")
        
        with SuppressStderr():
            microphones = sr.Microphone.list_microphone_names()
        
        # Procurar por palavras-chave do M-305
        m305_keywords = ['USB PnP Sound Device', 'M-305', 'USB Audio', 'Sound Device']
        
        for index, name in enumerate(microphones):
            print(f"  {index}: {name}")
            for keyword in m305_keywords:
                if keyword.lower() in name.lower():
                    print(f"✅ M-305 encontrado no índice {index}: {name}")
                    return index
        
        print("❌ M-305 não encontrado automaticamente")
        return None
    
    def setup_microphone(self):
        """Configura e ajusta microfone"""
        if self.microphone_index is not None:
            print(f"Configurando microfone M-305 (índice {self.microphone_index})...")
        else:
            print("Configurando microfone padrão...")
            
        with SuppressStderr():
            with self.microphone as source:
                print("Ajustando para ruído ambiente... (aguarde 3 segundos)")
                # Aumentar tempo de ajuste e diminuir threshold para microfones USB
                self.recognizer.adjust_for_ambient_noise(source, duration=3)
                
                # Configurações específicas para microfone USB
                self.recognizer.energy_threshold = max(300, self.recognizer.energy_threshold)
                self.recognizer.dynamic_energy_threshold = True
                self.recognizer.pause_threshold = 0.8
                self.recognizer.phrase_threshold = 0.3
                
                print(f"Nível de ruído configurado: {self.recognizer.energy_threshold}")
    
    def speak(self, text):
        """Fala o texto usando TTS"""
        print(f"Assistente: {text}")
        with SuppressStderr():
            self.tts.say(text)
            self.tts.runAndWait()
    
    def listen_for_wake_word_and_command(self):
        """Escuta por wake word + comando na mesma frase"""
        try:
            with SuppressStderr():
                with self.microphone as source:
                    # Escuta mais longa para capturar wake word + comando
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                
                # Usar Google Speech Recognition
                full_command = self.recognizer.recognize_google(audio, language='pt-BR')
                full_command_lower = full_command.lower()
                
                # Verificar se contém wake word
                wake_word_found = None
                for wake_word in self.wake_words:
                    if wake_word in full_command_lower:
                        wake_word_found = wake_word
                        break
                
                if wake_word_found:
                    # Extrair comando removendo a wake word
                    command = full_command_lower.replace(wake_word_found, '').strip()
                    # Remover vírgulas e pontuações que podem aparecer após wake word
                    command = re.sub(r'^[,.\s]+', '', command)
                    
                    print(f"Wake word '{wake_word_found}' detectada. Comando: '{command}'")
                    return command if command else None
                        
                return None
                
        except (sr.WaitTimeoutError, sr.UnknownValueError, sr.RequestError):
            return None
    
    def process_command(self, command):
        """Processa comando recebido"""
        if not command:
            return
            
        # Buscar comando nas palavras-chave
        for keyword, action in self.commands.items():
            if keyword in command:
                if keyword in ['ligar para', 'tocar', 'navegar para', 'enviar mensagem', 'discagem']:
                    # Comandos que precisam de parâmetros
                    action(command)
                else:
                    action()
                return
                
        # Comando não reconhecido
        self.speak("Comando não reconhecido. Diga 'ajuda' para ver os comandos disponíveis.")
    
    # === COMANDOS DE CHAMADAS ===
    def make_call(self, command):
        """Ligar para contato"""
        # Extrair nome do contato
        contact = command.replace('ligar para', '').strip()
        if contact:
            self.speak(f"Ligando para {contact}")
        else:
            self.speak("Para quem você quer ligar?")
    
    def answer_call(self):
        """Atender chamada"""
        self.speak("Atendendo chamada")
    
    def end_call(self):
        """Desligar chamada"""
        self.speak("Chamada encerrada")
    
    def speed_dial(self, command):
        """Discagem rápida"""
        # Extrair número
        numbers = re.findall(r'\d+', command)
        if numbers:
            number = ''.join(numbers)
            self.speak(f"Discando para {number}")
        else:
            self.speak("Qual número você quer discar?")
    
    # === COMANDOS DE MÚSICA ===
    def play_music(self):
        """Tocar música"""
        self.speak("Reproduzindo música")
    
    def play_specific(self, command):
        """Tocar música específica"""
        # Extrair artista/música/álbum
        content = command.replace('tocar', '').strip()
        if content:
            self.speak(f"Tocando {content}")
        else:
            self.speak("O que você quer ouvir?")
    
    def volume_up(self):
        """Aumentar volume"""
        self.speak("Aumentando volume")
    
    def volume_down(self):
        """Diminuindo volume"""
        self.speak("Diminuindo volume")
    
    def next_track(self):
        """Próxima música"""
        self.speak("Próxima música")
    
    def previous_track(self):
        """Música anterior"""
        self.speak("Música anterior")
    
    # === COMANDOS DE NAVEGAÇÃO ===
    def navigate_to(self, command):
        """Navegar para endereço"""
        destination = command.replace('navegar para', '').strip()
        if destination:
            self.speak(f"Navegando para {destination}")
        else:
            self.speak("Para onde você quer ir?")
    
    def alternative_routes(self):
        """Mostrar rotas alternativas"""
        self.speak("Mostrando rotas alternativas")
    
    def current_location(self):
        """Localização atual"""
        self.speak("Você está na Avenida Principal, número 123")
    
    def cancel_route(self):
        """Cancelar rota"""
        self.speak("Rota cancelada")
    
    # === COMANDOS DE MENSAGENS ===
    def send_message(self, command):
        """Enviar mensagem"""
        # Extrair destinatário
        contact = command.replace('enviar mensagem para', '').strip()
        if contact:
            self.speak(f"Enviando mensagem para {contact}. Dite sua mensagem")
        else:
            self.speak("Para quem você quer enviar mensagem?")
    
    def read_last_message(self):
        """Ler última mensagem"""
        self.speak("Última mensagem de João: Chegando em 10 minutos")
    
    def read_message(self):
        """Ler mensagem"""
        self.speak("Você tem 2 mensagens não lidas")
    
    # === COMANDOS DO SISTEMA ===
    def status(self):
        """Status do sistema"""
        self.speak("Sistema funcionando. Bluetooth conectado. GPS ativo.")
    
    def help(self):
        """Lista de comandos"""
        help_text = """Para usar o assistente, diga a wake word seguida do comando:
        
        Exemplos:
        - 'Assistente, tocar música'
        - 'OK Google, ligar para João'
        - 'Carro, navegar para casa'
        
        Comandos disponíveis:
        Chamadas: ligar para, atender, desligar chamada, discagem rápida.
        Música: tocar música, aumentar volume, diminuir volume, próxima, anterior.
        Navegação: navegar para, rotas alternativas, onde estou, cancelar rota.
        Mensagens: enviar mensagem, última mensagem, ler mensagem.
        Sistema: ajuda, status.
        
        Para encerrar: 'Assistente, tchau' ou 'Assistente, pode parar'."""
        self.speak(help_text)
    
    def start_listening(self):
        """Inicia loop principal com wake word + comando"""
        self.speak("Assistente de voz iniciado. Diga 'Assistente' para começar.")
        self.is_listening = True
        
        while self.is_listening:
            try:
                # Sempre escutando por wake word + comando na mesma frase
                print("� Aguardando comando... (Ex: 'Assistente, tocar música')")
                
                command = self.listen_for_wake_word_and_command()
                if command:
                    self.process_command(command)
                    
                    # Verificar se comando é para encerrar
                    if any(word in command for word in ['tchau', 'obrigado', 'até logo', 'pode parar', 'encerrar']):
                        break
                
                time.sleep(0.1)  # Pequena pausa para evitar uso excessivo de CPU
                
            except KeyboardInterrupt:
                self.speak("Encerrando assistente")
                break
            except Exception as e:
                print(f"Erro: {e}")
                time.sleep(1)

def test_microphone():
    """Testa se o microfone está funcionando"""
    r = sr.Recognizer()
    
    print("Testando microfone M-305...")
    print("Microfones disponíveis:")
    
    # Encontrar M-305
    microphone_index = None
    m305_keywords = ['USB PnP Sound Device', 'M-305', 'USB Audio', 'Sound Device']
    
    with SuppressStderr():
        microphones = sr.Microphone.list_microphone_names()
        
    for index, name in enumerate(microphones):
        print(f"  {index}: {name}")
        for keyword in m305_keywords:
            if keyword.lower() in name.lower():
                microphone_index = index
                print(f"✅ M-305 encontrado no índice {index}")
                break
    
    if microphone_index is None:
        print("❌ M-305 não encontrado. Usando microfone padrão.")
        microphone = sr.Microphone()
    else:
        microphone = sr.Microphone(device_index=microphone_index)
    
    try:
        with SuppressStderr():
            with microphone as source:
                print("Ajustando para ruído ambiente... (3 segundos)")
                r.adjust_for_ambient_noise(source, duration=3)
                
                # Configurações otimizadas para USB
                r.energy_threshold = max(300, r.energy_threshold)
                r.dynamic_energy_threshold = True
                r.pause_threshold = 0.8
                r.phrase_threshold = 0.3
                
                print(f"Nível de ruído: {r.energy_threshold}")
                print("Fale algo para testar (você tem 10 segundos):")
                
                audio = r.listen(source, timeout=10, phrase_time_limit=5)
                
            print("Processando áudio...")
            text = r.recognize_google(audio, language='pt-BR')
            print(f"✅ Texto reconhecido: '{text}'")
            return True
        
    except sr.WaitTimeoutError:
        print("❌ Timeout: Nenhum áudio detectado. Verifique se o microfone está funcionando.")
        print("💡 Dicas:")
        print("   - Fale mais próximo do microfone")
        print("   - Verifique se o microfone não está mudo")
        print("   - Teste com: pulseaudio --check -v")
        return False
    except sr.UnknownValueError:
        print("❌ Áudio detectado mas não foi possível reconhecer a fala")
        print("💡 Dicas:")
        print("   - Fale mais claramente")
        print("   - Verifique se há muito ruído de fundo")
        return False
    except Exception as e:
        print(f"❌ Erro no teste do microfone: {e}")
        return False

def test_voices():
    """Testa vozes disponíveis no sistema"""
    print("Testando vozes TTS disponíveis...")
    
    with SuppressStderr():
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
    
    if not voices:
        print("Nenhuma voz TTS encontrada!")
        print("Execute './install_better_voices.sh' para instalar vozes mais naturais")
        return False
    
    print(f"Total de vozes encontradas: {len(voices)}")
    print("\nVozes disponíveis:")
    
    portuguese_voices = []
    for i, voice in enumerate(voices):
        print(f"  {i}: {voice.name} - {voice.id}")
        # Verificar se é voz em português
        if any(keyword in voice.name.lower() for keyword in ['pt', 'brazil', 'portuguese', 'brasil', 'br']):
            portuguese_voices.append((i, voice.name, voice.id))
    
    if portuguese_voices:
        print(f"\n✅ Vozes em português encontradas: {len(portuguese_voices)}")
        for i, name, id in portuguese_voices:
            print(f"  - {name}")
    else:
        print("\n⚠️  Nenhuma voz em português encontrada.")
        print("Execute './install_better_voices.sh' para instalar vozes em português mais naturais")
        
    # Testar uma voz portuguesa se disponível
    if portuguese_voices:
        test_voice_id = portuguese_voices[0][2]
        print(f"\nTestando voz: {portuguese_voices[0][1]}")
        with SuppressStderr():
            engine.setProperty('voice', test_voice_id)
            engine.setProperty('rate', 160)
            engine.setProperty('volume', 0.85)
            engine.say("Olá, esta é uma demonstração da minha voz.")
            engine.runAndWait()
        
    with SuppressStderr():
        engine.stop()
    return True

if __name__ == "__main__":
    print("=== Assistente de Voz para Carro ===")
    print("Google Dev Board (AA1) - Microfone M-305")
    print()
    
    # Testar vozes TTS primeiro
    print("1. Testando sistema de voz...")
    test_voices()
    print()
    
    # Testar microfone
    print("2. Testando microfone...")
    if test_microphone():
        print("\n✅ Microfone funcionando! Iniciando assistente...")
        assistant = VoiceAssistant()
        assistant.start_listening()
    else:
        print("\n❌ Problema com o microfone. Verifique a configuração.")
