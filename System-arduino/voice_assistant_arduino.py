#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Assistente de Voz com Arduino como Microfone Remoto
Recebe áudio do Arduino via WiFi/Serial e processa comandos de voz

Hardware: Google Dev Board (AA1) + Arduino Nano RP2040 Connect
Autor: Sistema Assistente de Voz para Carro
Versão: 1.0
"""

import speech_recognition as sr
import pyttsx3
import time
import threading
import os
import re
import warnings
import sys
import socket
import serial
import numpy as np
import io
import wave
import tempfile
import struct
from datetime import datetime

# ===== CONFIGURAÇÕES DO SISTEMA =====
USE_WIFI = True          # True = WiFi, False = Serial USB
WIFI_PORT = 5555         # Porta TCP para receber dados do Arduino
SERIAL_PORT = '/dev/ttyUSB0'  # Porta serial (ajustar conforme necessário)
SERIAL_BAUD = 115200     # Velocidade serial
SAMPLE_RATE = 16000      # Taxa de amostragem (deve ser igual ao Arduino)
RECORD_SECONDS = 5       # Tempo de gravação para cada comando
DEBUG = True             # Modo debug com mais informações

# Suprimir warnings do ALSA
warnings.filterwarnings("ignore")
os.environ['PYTHONWARNINGS'] = 'ignore'

class ArduinoMicrophone:
    """
    Classe para gerenciar a comunicação com o Arduino
    Recebe dados de áudio via WiFi ou Serial
    """
    
    def __init__(self, use_wifi=True):
        self.use_wifi = use_wifi
        self.buffer = bytearray()  # Buffer para armazenar áudio recebido
        self.is_recording = False  # Flag de controle de gravação
        self.connection_active = False
        self.debug = DEBUG
        
        # Estatísticas
        self.bytes_received = 0
        self.last_data_time = time.time()
        
        if use_wifi:
            self._setup_wifi()
        else:
            self._setup_serial()
    
    def _setup_wifi(self):
        """Configura servidor TCP para receber dados do Arduino"""
        try:
            # Criar socket TCP
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Bind na porta especificada
            self.sock.bind(('0.0.0.0', WIFI_PORT))
            self.sock.listen(1)
            
            print(f"📡 Servidor TCP iniciado na porta {WIFI_PORT}")
            print("⏳ Aguardando conexão do Arduino...")
            
            # Aceitar conexão (bloqueia até Arduino conectar)
            self.conn, self.addr = self.sock.accept()
            print(f"✅ Arduino conectado de {self.addr[0]}:{self.addr[1]}")
            
            # Aguardar mensagem de identificação
            self.conn.settimeout(5.0)
            try:
                ident = self.conn.recv(1024).decode().strip()
                if "ARDUINO_MIC_READY" in ident:
                    print("✅ Arduino identificado corretamente")
                    self.connection_active = True
            except:
                print("⚠️ Arduino conectado mas não identificado")
                self.connection_active = True
            
            # Remover timeout para operação normal
            self.conn.settimeout(None)
            
        except Exception as e:
            print(f"❌ Erro ao configurar WiFi: {e}")
            raise
    
    def _setup_serial(self):
        """Configura comunicação serial com Arduino"""
        try:
            print(f"🔌 Conectando na porta serial {SERIAL_PORT}...")
            self.ser = serial.Serial(SERIAL_PORT, SERIAL_BAUD, timeout=0.1)
            
            # Limpar buffer inicial
            self.ser.reset_input_buffer()
            time.sleep(2)  # Aguardar Arduino reiniciar
            
            print(f"✅ Serial conectada em {SERIAL_PORT} @ {SERIAL_BAUD} baud")
            self.connection_active = True
            
        except Exception as e:
            print(f"❌ Erro ao configurar Serial: {e}")
            print("💡 Dica: Verifique se a porta está correta com 'ls /dev/tty*'")
            raise
    
    def start_recording(self):
        """Inicia gravação de áudio"""
        self.buffer.clear()
        self.bytes_received = 0
        self.is_recording = True
        self.last_data_time = time.time()
        
        if self.debug:
            print(f"🔴 Gravação iniciada ({datetime.now().strftime('%H:%M:%S')})")
    
    def stop_recording(self):
        """
        Para gravação e converte buffer em AudioData
        Retorna objeto sr.AudioData para reconhecimento
        """
        self.is_recording = False
        time.sleep(0.2)  # Aguardar últimos dados
        
        if self.debug:
            print(f"⏹️ Gravação parada. Total: {len(self.buffer)} bytes")
        
        if len(self.buffer) == 0:
            print("⚠️ Nenhum dado de áudio recebido!")
            return None
        
        try:
            # Converter buffer para array numpy (16-bit signed)
            audio_data = np.frombuffer(self.buffer, dtype=np.int16)
            
            # Verificar se há áudio válido
            if np.max(np.abs(audio_data)) < 100:
                print("⚠️ Áudio muito baixo ou silencioso")
            
            # Normalizar áudio se necessário
            max_val = np.max(np.abs(audio_data))
            if max_val > 0:
                # Normalizar para 80% do range máximo
                audio_data = (audio_data * (32767 * 0.8 / max_val)).astype(np.int16)
            
            # Criar arquivo WAV temporário
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                temp_filename = tmp_file.name
                
                # Escrever WAV
                with wave.open(temp_filename, 'wb') as wav_file:
                    wav_file.setnchannels(1)  # Mono
                    wav_file.setsampwidth(2)  # 16 bits
                    wav_file.setframerate(SAMPLE_RATE)
                    wav_file.writeframes(audio_data.tobytes())
                
                if self.debug:
                    duration = len(audio_data) / SAMPLE_RATE
                    print(f"📊 Áudio: {duration:.1f}s, {max_val} amplitude máx")
                
                # Converter para sr.AudioData
                with sr.AudioFile(temp_filename) as source:
                    audio = sr.Recognizer().record(source)
                
                # Limpar arquivo temporário
                os.unlink(temp_filename)
                
                return audio
                
        except Exception as e:
            print(f"❌ Erro ao processar áudio: {e}")
            return None
    
    def receive_loop(self):
        """
        Loop principal para receber dados continuamente
        Deve rodar em thread separada
        """
        print("🔄 Loop de recepção iniciado")
        
        while self.connection_active:
            try:
                data = None
                
                if self.use_wifi:
                    # Receber via TCP
                    try:
                        data = self.conn.recv(4096)  # Buffer maior para eficiência
                        if not data:
                            # Conexão fechada
                            print("⚠️ Conexão WiFi perdida")
                            self.connection_active = False
                            break
                    except socket.timeout:
                        continue
                else:
                    # Receber via Serial
                    if self.ser.in_waiting > 0:
                        data = self.ser.read(self.ser.in_waiting)
                    else:
                        time.sleep(0.001)  # Pequena pausa para não usar 100% CPU
                        continue
                
                # Processar dados recebidos
                if data and self.is_recording:
                    self.buffer.extend(data)
                    self.bytes_received += len(data)
                    self.last_data_time = time.time()
                    
                    # Debug: mostrar progresso a cada 16KB
                    if self.debug and self.bytes_received % 16384 == 0:
                        print(f"📦 Recebido: {self.bytes_received // 1024}KB")
                
            except Exception as e:
                print(f"❌ Erro no loop de recepção: {e}")
                if self.use_wifi:
                    self.connection_active = False
                    break
                else:
                    # Para serial, tentar continuar
                    time.sleep(1)
        
        print("🔴 Loop de recepção encerrado")
    
    def check_connection(self):
        """Verifica se a conexão está ativa"""
        if not self.connection_active:
            return False
        
        # Verificar timeout de dados
        if self.is_recording and (time.time() - self.last_data_time) > 5:
            print("⚠️ Timeout: Nenhum dado recebido há 5 segundos")
            return False
        
        return True
    
    def close(self):
        """Fecha conexões"""
        self.connection_active = False
        
        try:
            if self.use_wifi:
                self.conn.close()
                self.sock.close()
            else:
                self.ser.close()
        except:
            pass

class VoiceAssistant:
    """
    Assistente de voz principal
    Processa comandos e executa ações
    """
    
    def __init__(self):
        print("\n🚗 Inicializando Assistente de Voz com Arduino...")
        
        # Wake words aceitas
        self.wake_words = ['ok google', 'hey google', 'assistente', 'carro']
        
        # Inicializar comunicação com Arduino
        self.arduino_mic = ArduinoMicrophone(use_wifi=USE_WIFI)
        
        # Thread para receber dados do Arduino
        self.receive_thread = threading.Thread(target=self.arduino_mic.receive_loop)
        self.receive_thread.daemon = True
        self.receive_thread.start()
        
        # Configurar reconhecimento de voz
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300  # Ajustar sensibilidade
        self.recognizer.dynamic_energy_threshold = True
        
        # Configurar síntese de voz
        self.tts = pyttsx3.init()
        self.setup_tts()
        
        # Mapear comandos para funções
        self.commands = {
            # Chamadas
            'ligar para': self.make_call,
            'atender': self.answer_call,
            'desligar chamada': self.end_call,
            'discagem': self.speed_dial,
            
            # Música
            'tocar música': self.play_music,
            'tocar': self.play_specific,
            'aumentar volume': self.volume_up,
            'diminuir volume': self.volume_down,
            'próxima': self.next_track,
            'anterior': self.previous_track,
            'pausar': self.pause_music,
            'continuar': self.resume_music,
            
            # Navegação
            'navegar para': self.navigate_to,
            'rotas alternativas': self.alternative_routes,
            'onde estou': self.current_location,
            'cancelar rota': self.cancel_route,
            'tempo até': self.time_to_destination,
            
            # Mensagens
            'enviar mensagem': self.send_message,
            'última mensagem': self.read_last_message,
            'ler mensagem': self.read_message,
            
            # Sistema
            'ajuda': self.help,
            'status': self.status,
            'que horas são': self.current_time,
            'data de hoje': self.current_date
        }
        
        self.is_listening = False
        
    def setup_tts(self):
        """Configura voz do sistema TTS"""
        voices = self.tts.getProperty('voices')
        
        # Procurar voz em português
        pt_voice = None
        for voice in voices:
            voice_name = voice.name.lower()
            # Procurar palavras-chave de português
            if any(keyword in voice_name for keyword in ['brazil', 'brasil', 'pt', 'portuguese']):
                pt_voice = voice.id
                print(f"🔊 Voz PT-BR encontrada: {voice.name}")
                break
        
        if pt_voice:
            self.tts.setProperty('voice', pt_voice)
        else:
            print("⚠️ Voz PT-BR não encontrada, usando padrão")
        
        # Ajustar propriedades da voz
        self.tts.setProperty('rate', 160)     # Velocidade (palavras/minuto)
        self.tts.setProperty('volume', 0.85)  # Volume (0.0 a 1.0)
    
    def speak(self, text):
        """Sintetiza e fala o texto"""
        print(f"🔊 Assistente: {text}")
        
        try:
            self.tts.say(text)
            self.tts.runAndWait()
        except Exception as e:
            print(f"❌ Erro ao falar: {e}")
    
    def listen_for_wake_word_and_command(self):
        """
        Escuta por wake word + comando via Arduino
        Retorna o comando sem a wake word ou None
        """
        try:
            # Verificar conexão
            if not self.arduino_mic.check_connection():
                print("❌ Conexão com Arduino perdida!")
                return None
            
            print("\n👂 Escutando... (fale após o bipe)")
            
            # Som de feedback (opcional)
            # self.speak("bip")  # Ou usar outro método de feedback
            
            # Gravar áudio por X segundos
            self.arduino_mic.start_recording()
            time.sleep(RECORD_SECONDS)
            audio = self.arduino_mic.stop_recording()
            
            if audio is None:
                return None
            
            # Reconhecer fala
            print("🧠 Processando áudio...")
            
            try:
                # Usar Google Speech Recognition
                full_command = self.recognizer.recognize_google(
                    audio, 
                    language='pt-BR',
                    show_all=False  # Retornar apenas melhor resultado
                )
                
                print(f"📝 Você disse: '{full_command}'")
                
                # Converter para minúsculas para comparação
                full_command_lower = full_command.lower()
                
                # Procurar wake word
                wake_word_found = None
                wake_word_position = -1
                
                for wake_word in self.wake_words:
                    if wake_word in full_command_lower:
                        wake_word_found = wake_word
                        wake_word_position = full_command_lower.find(wake_word)
                        break
                
                if wake_word_found:
                    # Extrair comando após wake word
                    command_start = wake_word_position + len(wake_word_found)
                    command = full_command_lower[command_start:].strip()
                    
                    # Limpar pontuação inicial
                    command = re.sub(r'^[,.\s]+', '', command)
                    
                    print(f"✅ Wake word: '{wake_word_found}' | Comando: '{command}'")
                    return command if command else None
                else:
                    print("⚠️ Nenhuma wake word detectada")
                    return None
                    
            except sr.UnknownValueError:
                print("❓ Não foi possível entender o áudio")
                return None
            except sr.RequestError as e:
                print(f"❌ Erro no serviço de reconhecimento: {e}")
                return None
                
        except Exception as e:
            print(f"❌ Erro ao escutar: {e}")
            return None
    
    def process_command(self, command):
        """
        Processa o comando e executa a ação correspondente
        """
        if not command:
            return
        
        print(f"⚙️ Processando comando: '{command}'")
        
        # Procurar comando no dicionário
        command_found = False
        
        for keyword, action in self.commands.items():
            if keyword in command:
                command_found = True
                
                # Comandos que precisam de parâmetros
                if keyword in ['ligar para', 'tocar', 'navegar para', 
                             'enviar mensagem', 'discagem', 'tempo até']:
                    action(command)
                else:
                    action()
                
                break
        
        if not command_found:
            self.speak("Desculpe, não entendi o comando. Diga 'ajuda' para ver os comandos disponíveis.")
    
    # ===== COMANDOS DE CHAMADAS =====
    
    def make_call(self, command):
        """Fazer ligação"""
        # Extrair nome do contato
        contact = command.replace('ligar para', '').strip()
        
        if contact:
            self.speak(f"Ligando para {contact}")
            # Aqui entraria integração com sistema de telefone do carro
        else:
            self.speak("Para quem você quer ligar?")
    
    def answer_call(self):
        """Atender chamada"""
        self.speak("Atendendo chamada")
        # Integração com sistema do carro
    
    def end_call(self):
        """Encerrar chamada"""
        self.speak("Chamada encerrada")
        # Integração com sistema do carro
    
    def speed_dial(self, command):
        """Discagem rápida"""
        # Extrair números do comando
        numbers = re.findall(r'\d+', command)
        
        if numbers:
            number = ''.join(numbers)
            self.speak(f"Discando {' '.join(number)}")  # Falar dígito por dígito
        else:
            self.speak("Qual número você quer discar?")
    
    # ===== COMANDOS DE MÚSICA =====
    
    def play_music(self):
        """Tocar música"""
        self.speak("Reproduzindo suas músicas")
        # Integração com player de música
    
    def play_specific(self, command):
        """Tocar música/artista específico"""
        # Remover 'tocar' do comando
        content = command.replace('tocar', '').strip()
        
        if content:
            self.speak(f"Tocando {content}")
            # Integração com player
        else:
            self.speak("O que você quer ouvir?")
    
    def volume_up(self):
        """Aumentar volume"""
        self.speak("Aumentando o volume")
        # Integração com sistema de áudio
    
    def volume_down(self):
        """Diminuir volume"""
        self.speak("Diminuindo o volume")
        # Integração com sistema de áudio
    
    def next_track(self):
        """Próxima música"""
        self.speak("Próxima música")
        # Integração com player
    
    def previous_track(self):
        """Música anterior"""
        self.speak("Música anterior")
        # Integração com player
    
    def pause_music(self):
        """Pausar música"""
        self.speak("Música pausada")
        # Integração com player
    
    def resume_music(self):
        """Continuar música"""
        self.speak("Continuando a reprodução")
        # Integração com player
    
    # ===== COMANDOS DE NAVEGAÇÃO =====
    
    def navigate_to(self, command):
        """Navegar para destino"""
        destination = command.replace('navegar para', '').strip()
        
        if destination:
            self.speak(f"Calculando rota para {destination}")
            # Integração com GPS
        else:
            self.speak("Para onde você quer ir?")
    
    def alternative_routes(self):
        """Mostrar rotas alternativas"""
        self.speak("Procurando rotas alternativas")
        # Integração com GPS
    
    def current_location(self):
        """Localização atual"""
        # Exemplo de resposta
        self.speak("Você está na Avenida Paulista, próximo ao número 1500")
        # Integração com GPS para localização real
    
    def cancel_route(self):
        """Cancelar navegação"""
        self.speak("Navegação cancelada")
        # Integração com GPS
    
    def time_to_destination(self, command):
        """Tempo até destino"""
        # Exemplo de resposta
        self.speak("Tempo estimado de chegada: 15 minutos")
        # Integração com GPS
    
    # ===== COMANDOS DE MENSAGENS =====
    
    def send_message(self, command):
        """Enviar mensagem"""
        # Extrair destinatário
        parts = command.replace('enviar mensagem para', '').strip()
        
        if parts:
            self.speak(f"Preparando mensagem para {parts}. O que você quer dizer?")
            # Aqui entraria um novo listen para capturar a mensagem
        else:
            self.speak("Para quem você quer enviar a mensagem?")
    
    def read_last_message(self):
        """Ler última mensagem"""
        # Exemplo de mensagem
        self.speak("Última mensagem de Maria: Estou chegando em 10 minutos")
        # Integração com sistema de mensagens
    
    def read_message(self):
        """Ler mensagens não lidas"""
        # Exemplo
        self.speak("Você tem 3 mensagens não lidas. Quer que eu leia?")
        # Integração com sistema de mensagens
    
    # ===== COMANDOS DO SISTEMA =====
    
    def status(self):
        """Status do sistema"""
        status_msg = "Sistema funcionando normalmente. "
        
        # Verificar conexão Arduino
        if self.arduino_mic.check_connection():
            status_msg += "Arduino conectado. "
        else:
            status_msg += "Arduino desconectado. "
        
        # Adicionar mais informações de status
        status_msg += f"Modo: {'WiFi' if USE_WIFI else 'Serial'}."
        
        self.speak(status_msg)
    
    def current_time(self):
        """Hora atual"""
        now = datetime.now()
        hour = now.strftime("%H")
        minute = now.strftime("%M")
        self.speak(f"São {hour} horas e {minute} minutos")
    
    def current_date(self):
        """Data atual"""
        now = datetime.now()
        # Formato brasileiro
        date_str = now.strftime("%d de %B de %Y")
        # Traduzir mês para português
        months = {
            'January': 'janeiro', 'February': 'fevereiro', 'March': 'março',
            'April': 'abril', 'May': 'maio', 'June': 'junho',
            'July': 'julho', 'August': 'agosto', 'September': 'setembro',
            'October': 'outubro', 'November': 'novembro', 'December': 'dezembro'
        }
        for en, pt in months.items():
            date_str = date_str.replace(en, pt)
        
        self.speak(f"Hoje é {date_str}")
    
    def help(self):
        """Lista comandos disponíveis"""
        help_text = """
        Comandos disponíveis:
        
        Para chamadas: ligar para alguém, atender, desligar chamada.
        Para música: tocar música, aumentar ou diminuir volume, próxima, anterior.
        Para navegação: navegar para destino, onde estou, cancelar rota.
        Para mensagens: enviar mensagem, ler última mensagem.
        
        Sempre comece com uma wake word como 'Assistente' ou 'OK Google'.
        """
        
        self.speak(help_text)
    
    def start_listening(self):
        """
        Loop principal do assistente
        Fica escutando por comandos continuamente
        """
        # Mensagem de boas-vindas
        self.speak("Assistente de voz com Arduino iniciado. Diga 'Assistente ajuda' para ver os comandos.")
        
        self.is_listening = True
        consecutive_errors = 0
        
        while self.is_listening:
            try:
                # Indicador visual/sonoro de que está pronto
                print("\n" + "="*50)
                print("👂 Pronto para comandos...")
                print("💡 Exemplo: 'Assistente, tocar música'")
                print("="*50)
                
                # Escutar por comando
                command = self.listen_for_wake_word_and_command()
                
                if command:
                    # Reset contador de erros
                    consecutive_errors = 0
                    
                    # Processar comando
                    self.process_command(command)
                    
                    # Verificar comandos de saída
                    exit_words = ['tchau', 'até logo', 'parar assistente', 
                                 'encerrar', 'desligar assistente']
                    if any(word in command for word in exit_words):
                        self.speak("Até logo! Encerrando assistente.")
                        break
                else:
                    # Não detectou comando válido
                    consecutive_errors += 1
                    
                    # Se muitos erros consecutivos, verificar conexão
                    if consecutive_errors > 5:
                        print("⚠️ Muitos erros consecutivos, verificando sistema...")
                        self.status()
                        consecutive_errors = 0
                
                # Pequena pausa entre comandos
                time.sleep(0.5)
                
            except KeyboardInterrupt:
                print("\n⛔ Interrompido pelo usuário")
                self.speak("Encerrando assistente")
                break
                
            except Exception as e:
                print(f"❌ Erro no loop principal: {e}")
                consecutive_errors += 1
                
                if consecutive_errors > 10:
                    self.speak("Muitos erros detectados. Reinicie o sistema.")
                    break
                
                time.sleep(2)
        
        # Limpeza ao sair
        self.cleanup()
    
    def cleanup(self):
        """Limpa recursos ao encerrar"""
        print("\n🧹 Limpando recursos...")
        
        try:
            self.arduino_mic.close()
            self.tts.stop()
        except:
            pass
        
        print("✅ Assistente encerrado")

def test_connection():
    """Função para testar conexão com Arduino"""
    print("\n🧪 Teste de Conexão com Arduino")
    print("="*50)
    
    try:
        # Tentar criar conexão
        arduino = ArduinoMicrophone(use_wifi=USE_WIFI)
        
        print("✅ Conexão estabelecida!")
        print(f"Modo: {'WiFi' if USE_WIFI else 'Serial'}")
        
        # Testar recepção de dados
        print("\n📡 Testando recepção de dados por 3 segundos...")
        
        receive_thread = threading.Thread(target=arduino.receive_loop)
        receive_thread.daemon = True
        receive_thread.start()
        
        arduino.start_recording()
        time.sleep(3)
        arduino.stop_recording()
        
        if arduino.bytes_received > 0:
            print(f"✅ Dados recebidos: {arduino.bytes_received} bytes")
        else:
            print("❌ Nenhum dado recebido do Arduino")
            print("Verifique se o Arduino está enviando dados")
        
        arduino.close()
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")

# ===== PONTO DE ENTRADA =====
if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════════╗
    ║   Assistente de Voz com Arduino Microfone    ║
    ║          Google Dev Board (AA1)               ║
    ╚═══════════════════════════════════════════════╝
    """)
    
    print(f"📡 Modo: {'WiFi' if USE_WIFI else 'Serial'}")
    print(f"🎤 Taxa de amostragem: {SAMPLE_RATE} Hz")
    print(f"⏱️ Tempo de gravação: {RECORD_SECONDS} segundos")
    
    # Verificar argumentos de linha de comando
    if len(sys.argv) > 1:
        if sys.argv[1] == '--test':
            test_connection()
            sys.exit(0)
        elif sys.argv[1] == '--help':
            print("\nUso: python3 voice_assistant_arduino.py [opções]")
            print("Opções:")
            print("  --test    Testar conexão com Arduino")
            print("  --help    Mostrar esta ajuda")
            sys.exit(0)
    
    try:
        # Criar e iniciar assistente
        assistant = VoiceAssistant()
        assistant.start_listening()
        
    except KeyboardInterrupt:
        print("\n⛔ Programa interrompido")
        
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")
        print("💡 Dicas:")
        print("  - Verifique se o Arduino está conectado e rodando")
        print("  - Para WiFi: Confirme IP e porta")
        print("  - Para Serial: Confirme porta USB")
        print("  - Execute com --test para diagnosticar")