#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import speech_recognition as sr
import pyttsx3
import time
import threading
import os
import re
import sys
import socket
import serial
import numpy as np
import wave
import tempfile
import struct
import queue

# Configurações
USE_WIFI = True
WIFI_PORT = 5555
SERIAL_PORT = '/dev/ttyACM0'
SERIAL_BAUD = 115200

class ArduinoMicrophone:
    """Classe melhorada para receber áudio do Arduino"""
    def __init__(self, use_wifi=True):
        self.use_wifi = use_wifi
        self.audio_queue = queue.Queue()
        self.is_recording = False
        self.is_connected = False
        self.total_bytes = 0
        self.conn = None
        self.ser = None
        
        if use_wifi:
            self.setup_wifi()
        else:
            self.setup_serial()
    
    def setup_wifi(self):
        """Configura conexão WiFi"""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('0.0.0.0', WIFI_PORT))
        self.sock.listen(1)
        print(f"Aguardando Arduino na porta {WIFI_PORT}...")
        
        self.conn, self.addr = self.sock.accept()
        self.conn.settimeout(0.1)  # Non-blocking com timeout
        
        # Aguardar handshake
        try:
            data = self.conn.recv(1024).decode().strip()
            if "ARDUINO_READY" in data:
                print(f"Arduino conectado de {self.addr}")
                self.is_connected = True
            else:
                print(f"Handshake inválido: {data}")
        except:
            print("Erro no handshake WiFi")
    
    def setup_serial(self):
        """Configura conexão Serial"""
        try:
            self.ser = serial.Serial(SERIAL_PORT, SERIAL_BAUD, timeout=0.1)
            time.sleep(2)  # Arduino reset
            self.ser.reset_input_buffer()
            
            # Aguardar READY
            start_time = time.time()
            while time.time() - start_time < 5:
                if self.ser.in_waiting:
                    line = self.ser.readline().decode().strip()
                    print(f"Arduino: {line}")
                    if "READY" in line:
                        self.is_connected = True
                        print("Arduino pronto via Serial")
                        break
            
            if not self.is_connected:
                print("Timeout aguardando Arduino")
                
        except Exception as e:
            print(f"Erro Serial: {e}")
    
    def send_command(self, cmd):
        """Envia comando para Arduino"""
        if self.use_wifi and self.conn:
            try:
                self.conn.send(f"{cmd}\n".encode())
            except:
                pass
        elif not self.use_wifi and self.ser:
            self.ser.write(f"{cmd}\n".encode())
            time.sleep(0.05)
    
    def start_recording(self):
        """Inicia gravação com sincronização"""
        self.audio_queue.queue.clear()
        self.total_bytes = 0
        self.is_recording = True
        self.send_command("START")
        print("Gravação iniciada")
        
    def stop_recording(self):
        """Para gravação e processa áudio"""
        self.is_recording = False
        self.send_command("STOP")
        time.sleep(0.2)  # Aguardar últimos dados
        
        print(f"Total bytes recebidos: {self.total_bytes}")
        
        # Coletar todos os dados da fila
        audio_data = bytearray()
        while not self.audio_queue.empty():
            try:
                chunk = self.audio_queue.get_nowait()
                audio_data.extend(chunk)
            except:
                break
        
        if len(audio_data) < 1000:
            print("Dados insuficientes!")
            return None
        
        # Converter para numpy array
        samples = np.frombuffer(audio_data, dtype=np.int16)
        
        # Normalizar se necessário
        max_val = np.max(np.abs(samples))
        if max_val > 0:
            samples = samples.astype(np.float32) / max_val
            samples = (samples * 32767).astype(np.int16)
        
        # Criar WAV temporário
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            with wave.open(tmp_file.name, 'wb') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(16000)
                wav_file.writeframes(samples.tobytes())
            
            # Debug: salvar cópia para análise
            import shutil
            debug_file = f"debug_audio_{int(time.time())}.wav"
            shutil.copy(tmp_file.name, debug_file)
            print(f"Áudio salvo em: {debug_file}")
            
            # Ler como AudioData
            with sr.AudioFile(tmp_file.name) as source:
                audio = sr.Recognizer().record(source)
            
            os.unlink(tmp_file.name)
            return audio
    
    def receive_loop(self):
        """Loop melhorado para receber dados"""
        buffer = bytearray()
        
        while True:
            try:
                if self.use_wifi:
                    self.receive_wifi(buffer)
                else:
                    self.receive_serial(buffer)
                    
                time.sleep(0.001)  # Evitar CPU 100%
                
            except Exception as e:
                print(f"Erro receive_loop: {e}")
                self.is_connected = False
                time.sleep(1)
    
    def receive_wifi(self, buffer):
        """Recebe dados via WiFi com protocolo"""
        if not self.conn:
            return
            
        try:
            data = self.conn.recv(4096)
            if data and self.is_recording:
                buffer.extend(data)
                
                # Processar protocolo: 'A' + size(2 bytes) + data
                while len(buffer) >= 3:
                    if buffer[0] == ord('A'):
                        size = (buffer[1] << 8) | buffer[2]
                        if len(buffer) >= 3 + size:
                            audio_chunk = buffer[3:3+size]
                            self.audio_queue.put(bytes(audio_chunk))
                            self.total_bytes += len(audio_chunk)
                            buffer = buffer[3+size:]
                        else:
                            break
                    else:
                        # Procurar próximo marcador
                        idx = buffer.find(b'A', 1)
                        if idx > 0:
                            buffer = buffer[idx:]
                        else:
                            buffer.clear()
                            
        except socket.timeout:
            pass
        except Exception as e:
            if e.errno != 11:  # Ignorar EAGAIN
                print(f"Erro WiFi: {e}")
    
    def receive_serial(self, buffer):
        """Recebe dados via Serial com protocolo"""
        if not self.ser or not self.ser.is_open:
            return
            
        if self.ser.in_waiting:
            data = self.ser.read(self.ser.in_waiting)
            
            # Processar linhas de texto (comandos/status)
            if b'\n' in data:
                parts = data.split(b'\n')
                for part in parts[:-1]:
                    line = part.decode(errors='ignore').strip()
                    if line and not line.startswith(chr(0xFF)):
                        print(f"Arduino: {line}")
                
                # Manter último fragmento
                data = parts[-1]
            
            # Processar dados de áudio
            if self.is_recording:
                buffer.extend(data)
                
                # Protocolo: 0xFF 0xFE size(2) data
                while len(buffer) >= 4:
                    if buffer[0] == 0xFF and buffer[1] == 0xFE:
                        size = (buffer[2] << 8) | buffer[3]
                        if len(buffer) >= 4 + size:
                            audio_chunk = buffer[4:4+size]
                            self.audio_queue.put(bytes(audio_chunk))
                            self.total_bytes += len(audio_chunk)
                            buffer = buffer[4+size:]
                        else:
                            break
                    else:
                        # Procurar próximo marcador
                        found = False
                        for i in range(1, len(buffer)-1):
                            if buffer[i] == 0xFF and buffer[i+1] == 0xFE:
                                buffer = buffer[i:]
                                found = True
                                break
                        if not found:
                            buffer.clear()

class VoiceAssistant:
    def __init__(self):
        self.wake_words = ['ok google', 'hey google', 'assistente', 'carro']
        
        # Inicializar Arduino
        self.arduino_mic = ArduinoMicrophone(use_wifi=USE_WIFI)
        
        if not self.arduino_mic.is_connected:
            raise Exception("Arduino não conectado!")
        
        # Thread para receber dados
        self.receive_thread = threading.Thread(target=self.arduino_mic.receive_loop)
        self.receive_thread.daemon = True
        self.receive_thread.start()
        
        # Reconhecimento e síntese
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300  # Ajustar sensibilidade
        self.recognizer.dynamic_energy_threshold = False
        
        self.tts = pyttsx3.init()
        self.setup_tts()
        
        # Comandos (mantidos do original)
        self.commands = {
            'ligar para': self.make_call,
            'atender': self.answer_call,
            'desligar chamada': self.end_call,
            'discagem': self.speed_dial,
            'tocar música': self.play_music,
            'tocar': self.play_specific,
            'aumentar volume': self.volume_up,
            'diminuir volume': self.volume_down,
            'próxima': self.next_track,
            'anterior': self.previous_track,
            'navegar para': self.navigate_to,
            'rotas alternativas': self.alternative_routes,
            'onde estou': self.current_location,
            'cancelar rota': self.cancel_route,
            'enviar mensagem': self.send_message,
            'última mensagem': self.read_last_message,
            'ler mensagem': self.read_message,
            'ajuda': self.help,
            'status': self.status
        }
        
        self.is_listening = False
        
    def setup_tts(self):
        """Configura síntese de voz"""
        voices = self.tts.getProperty('voices')
        
        for voice in voices:
            if 'brazil' in voice.name.lower() or 'pt' in voice.name.lower():
                self.tts.setProperty('voice', voice.id)
                print(f"Voz PT-BR: {voice.name}")
                break
        
        self.tts.setProperty('rate', 160)
        self.tts.setProperty('volume', 0.85)
    
    def speak(self, text):
        """Fala o texto"""
        print(f"Assistente: {text}")
        self.tts.say(text)
        self.tts.runAndWait()
    
    def listen_for_wake_word_and_command(self):
        """Escuta comando com melhor tratamento de erros"""
        try:
            print("🎤 Escutando...")
            
            # Verificar conexão
            if not self.arduino_mic.is_connected:
                print("Arduino desconectado!")
                return None
            
            # Gravar áudio
            self.arduino_mic.start_recording()
            time.sleep(4)  # Reduzido de 5 para 4 segundos
            audio = self.arduino_mic.stop_recording()
            
            if audio is None:
                print("Nenhum áudio capturado")
                return None
            
            # Reconhecer
            try:
                full_command = self.recognizer.recognize_google(
                    audio, 
                    language='pt-BR',
                    show_all=False  # Retorna só o melhor resultado
                )
                full_command_lower = full_command.lower()
                print(f"Você disse: {full_command}")
                
                # Verificar wake word
                for wake_word in self.wake_words:
                    if wake_word in full_command_lower:
                        command = full_command_lower.replace(wake_word, '').strip()
                        command = re.sub(r'^[,.\s]+', '', command)
                        return command if command else None
                        
                return None
                
            except sr.UnknownValueError:
                print("Não entendi o áudio")
                return None
            except sr.RequestError as e:
                print(f"Erro na API: {e}")
                return None
                
        except Exception as e:
            print(f"Erro geral: {e}")
            return None
    
    def process_command(self, command):
        """Processa comando"""
        if not command:
            return
            
        for keyword, action in self.commands.items():
            if keyword in command:
                if keyword in ['ligar para', 'tocar', 'navegar para', 'enviar mensagem', 'discagem']:
                    action(command)
                else:
                    action()
                return
                
        self.speak("Comando não reconhecido.")
    
    # Comandos mantidos do original...
    def make_call(self, command):
        contact = command.replace('ligar para', '').strip()
        if contact:
            self.speak(f"Ligando para {contact}")
        else:
            self.speak("Para quem você quer ligar?")
    
    def answer_call(self):
        self.speak("Atendendo chamada")
    
    def end_call(self):
        self.speak("Chamada encerrada")
    
    def speed_dial(self, command):
        numbers = re.findall(r'\d+', command)
        if numbers:
            number = ''.join(numbers)
            self.speak(f"Discando para {number}")
        else:
            self.speak("Qual número você quer discar?")
    
    def play_music(self):
        self.speak("Reproduzindo música")
    
    def play_specific(self, command):
        content = command.replace('tocar', '').strip()
        if content:
            self.speak(f"Tocando {content}")
        else:
            self.speak("O que você quer ouvir?")
    
    def volume_up(self):
        self.speak("Aumentando volume")
    
    def volume_down(self):
        self.speak("Diminuindo volume")
    
    def next_track(self):
        self.speak("Próxima música")
    
    def previous_track(self):
        self.speak("Música anterior")
    
    def navigate_to(self, command):
        destination = command.replace('navegar para', '').strip()
        if destination:
            self.speak(f"Navegando para {destination}")
        else:
            self.speak("Para onde você quer ir?")
    
    def alternative_routes(self):
        self.speak("Mostrando rotas alternativas")
    
    def current_location(self):
        self.speak("Você está na Avenida Principal, número 123")
    
    def cancel_route(self):
        self.speak("Rota cancelada")
    
    def send_message(self, command):
        contact = command.replace('enviar mensagem para', '').strip()
        if contact:
            self.speak(f"Enviando mensagem para {contact}. Dite sua mensagem")
        else:
            self.speak("Para quem você quer enviar mensagem?")
    
    def read_last_message(self):
        self.speak("Última mensagem de João: Chegando em 10 minutos")
    
    def read_message(self):
        self.speak("Você tem 2 mensagens não lidas")
    
    def status(self):
        # Status detalhado
        mode = "WiFi" if USE_WIFI else "Serial"
        connected = "Sim" if self.arduino_mic.is_connected else "Não"
        self.speak(f"Sistema funcionando. Modo {mode}. Arduino conectado: {connected}")
        
        # Solicitar status do Arduino
        self.arduino_mic.send_command("STATUS")
    
    def help(self):
        self.speak("Diga 'Assistente' seguido de: tocar música, ligar para alguém, navegar para destino, ou ajuda.")
    
    def start_listening(self):
        """Loop principal melhorado"""
        self.speak("Assistente com Arduino iniciado.")
        self.is_listening = True
        
        consecutive_errors = 0
        
        while self.is_listening:
            try:
                print("\n⏳ Aguardando comando...")
                command = self.listen_for_wake_word_and_command()
                
                if command:
                    consecutive_errors = 0  # Reset contador
                    self.process_command(command)
                    
                    if any(word in command for word in ['tchau', 'parar', 'encerrar']):
                        break
                else:
                    consecutive_errors += 1
                    
                    # Verificar se há muitos erros consecutivos
                    if consecutive_errors > 5:
                        print("Muitos erros. Verificando conexão...")
                        self.arduino_mic.send_command("STATUS")
                        time.sleep(2)
                        consecutive_errors = 0
                        
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Erro no loop: {e}")
                time.sleep(1)

if __name__ == "__main__":
    print("=== Assistente de Voz com Arduino ===")
    print(f"Modo: {'WiFi' if USE_WIFI else 'Serial'}")
    
    try:
        assistant = VoiceAssistant()
        assistant.start_listening()
    except Exception as e:
        print(f"Erro fatal: {e}")
        print("\nVerifique:")
        print("- Arduino está conectado e com sketch carregado")
        print("- Credenciais WiFi estão corretas")
        print("- IP do Dev Board está correto")
        print("- Porta serial está correta (se usando Serial)")