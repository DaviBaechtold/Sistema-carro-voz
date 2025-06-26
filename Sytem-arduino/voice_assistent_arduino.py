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
import socket
import serial
import numpy as np
import io
import wave
import tempfile

# Configurações
USE_WIFI = True  # True=WiFi, False=Serial
WIFI_PORT = 5555
SERIAL_PORT = '/dev/ttyUSB0'  # Ajustar conforme necessário
SERIAL_BAUD = 115200

class ArduinoMicrophone:
    """Classe para receber áudio do Arduino"""
    def __init__(self, use_wifi=True):
        self.use_wifi = use_wifi
        self.buffer = bytearray()
        self.is_recording = False
        
        if use_wifi:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind(('0.0.0.0', WIFI_PORT))
            self.sock.listen(1)
            print(f"Aguardando Arduino na porta {WIFI_PORT}...")
            self.conn, self.addr = self.sock.accept()
            print(f"Arduino conectado de {self.addr}")
        else:
            self.ser = serial.Serial(SERIAL_PORT, SERIAL_BAUD)
            print(f"Serial conectada em {SERIAL_PORT}")
    
    def start_recording(self):
        """Inicia gravação"""
        self.buffer.clear()
        self.is_recording = True
        
    def stop_recording(self):
        """Para gravação e retorna áudio WAV"""
        self.is_recording = False
        time.sleep(0.1)  # Aguardar últimos dados
        
        # Converter buffer para WAV
        audio_data = np.frombuffer(self.buffer, dtype=np.int16)
        
        # Criar arquivo WAV temporário
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            with wave.open(tmp_file.name, 'wb') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(16000)
                wav_file.writeframes(audio_data.tobytes())
            
            # Ler como AudioData para speech_recognition
            with sr.AudioFile(tmp_file.name) as source:
                audio = sr.Recognizer().record(source)
            
            os.unlink(tmp_file.name)
            return audio
    
    def receive_loop(self):
        """Loop para receber dados continuamente"""
        while True:
            try:
                if self.use_wifi:
                    data = self.conn.recv(1024)
                else:
                    if self.ser.in_waiting:
                        data = self.ser.read(self.ser.in_waiting)
                    else:
                        time.sleep(0.01)
                        continue
                
                if self.is_recording and data:
                    self.buffer.extend(data)
                    
            except Exception as e:
                print(f"Erro na recepção: {e}")
                break

class VoiceAssistant:
    def __init__(self):
        # Wake words
        self.wake_words = ['ok google', 'hey google', 'assistente', 'carro']
        
        # Inicializar Arduino como microfone
        self.arduino_mic = ArduinoMicrophone(use_wifi=USE_WIFI)
        
        # Thread para receber dados
        self.receive_thread = threading.Thread(target=self.arduino_mic.receive_loop)
        self.receive_thread.daemon = True
        self.receive_thread.start()
        
        # Reconhecimento e síntese
        self.recognizer = sr.Recognizer()
        self.tts = pyttsx3.init()
        self.setup_tts()
        
        # Comandos
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
        
        # Procurar voz em português
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
        """Escuta comando via Arduino"""
        try:
            print("🎤 Escutando...")
            
            # Gravar por 5 segundos
            self.arduino_mic.start_recording()
            time.sleep(5)
            audio = self.arduino_mic.stop_recording()
            
            # Reconhecer
            full_command = self.recognizer.recognize_google(audio, language='pt-BR')
            full_command_lower = full_command.lower()
            print(f"Você disse: {full_command}")
            
            # Verificar wake word
            for wake_word in self.wake_words:
                if wake_word in full_command_lower:
                    command = full_command_lower.replace(wake_word, '').strip()
                    command = re.sub(r'^[,.\s]+', '', command)
                    return command if command else None
                    
            return None
            
        except Exception as e:
            print(f"Erro: {e}")
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
    
    # === COMANDOS (mesmo código do original) ===
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
        self.speak("Sistema funcionando. Arduino conectado.")
    
    def help(self):
        self.speak("Diga 'Assistente' seguido de: tocar música, ligar para alguém, navegar para destino, ou ajuda.")
    
    def start_listening(self):
        """Loop principal"""
        self.speak("Assistente com Arduino iniciado.")
        self.is_listening = True
        
        while self.is_listening:
            try:
                print("\n⏳ Aguardando comando...")
                command = self.listen_for_wake_word_and_command()
                
                if command:
                    self.process_command(command)
                    
                    if any(word in command for word in ['tchau', 'parar', 'encerrar']):
                        break
                        
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Erro: {e}")
                time.sleep(1)

if __name__ == "__main__":
    print("=== Assistente de Voz com Arduino ===")
    print(f"Modo: {'WiFi' if USE_WIFI else 'Serial'}")
    
    try:
        assistant = VoiceAssistant()
        assistant.start_listening()
    except Exception as e:
        print(f"Erro fatal: {e}")