#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import speech_recognition as sr
import pyttsx3
import time
import threading
import os
import socket
import serial
import numpy as np
import wave
import tempfile
import struct

# Configurações
USE_WIFI = True
WIFI_PORT = 5555
SERIAL_PORT = '/dev/ttyACM0'
SERIAL_BAUD = 115200
SAMPLE_RATE = 16000
CHANNELS = 1
SAMPLE_WIDTH = 2  # 16-bit

class ArduinoMicrophone:
    def __init__(self, use_wifi=True):
        self.use_wifi = use_wifi
        self.buffer = bytearray()
        self.is_recording = False
        self.lock = threading.Lock()
        
        if use_wifi:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind(('0.0.0.0', WIFI_PORT))
            self.sock.listen(1)
            print(f"Aguardando Arduino na porta {WIFI_PORT}...")
            self.conn, self.addr = self.sock.accept()
            print(f"Arduino conectado de {self.addr}")
        else:
            self.ser = serial.Serial(SERIAL_PORT, SERIAL_BAUD, timeout=0.1)
            self.ser.reset_input_buffer()
            print(f"Serial conectada em {SERIAL_PORT}")
            time.sleep(2)  # Aguardar Arduino inicializar
    
    def start_recording(self):
        with self.lock:
            self.buffer.clear()
            self.is_recording = True
        print("Gravação iniciada")
        
    def stop_recording(self):
        self.is_recording = False
        time.sleep(0.2)  # Aguardar últimos dados
        
        with self.lock:
            audio_data = self.buffer.copy()
        
        print(f"Buffer size: {len(audio_data)} bytes")
        
        if len(audio_data) < 1000:  # Mínimo de dados
            print("Erro: Buffer muito pequeno")
            return None
        
        # Garantir que temos número par de bytes
        if len(audio_data) % 2 != 0:
            audio_data = audio_data[:-1]
        
        try:
            # Converter para array numpy
            samples = np.frombuffer(audio_data, dtype=np.int16)
            
            # Amplificar sinal fraco do PDM
            samples = samples * 4
            
            # Verificar se há sinal
            if np.max(np.abs(samples)) < 100:
                print("Erro: Sem sinal de áudio")
                return None
            
            # Criar WAV temporário
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                with wave.open(tmp_file.name, 'wb') as wav_file:
                    wav_file.setnchannels(CHANNELS)
                    wav_file.setsampwidth(SAMPLE_WIDTH)
                    wav_file.setframerate(SAMPLE_RATE)
                    wav_file.writeframes(samples.tobytes())
                
                # Ler como AudioData
                with sr.AudioFile(tmp_file.name) as source:
                    audio = sr.Recognizer().record(source)
                
                os.unlink(tmp_file.name)
                return audio
                
        except Exception as e:
            print(f"Erro ao processar áudio: {e}")
            return None
    
    def receive_loop(self):
        print("Thread de recepção iniciada")
        while True:
            try:
                if self.use_wifi:
                    data = self.conn.recv(1024)
                    if not data:
                        print("Conexão WiFi perdida")
                        break
                else:
                    if self.ser.in_waiting > 0:
                        data = self.ser.read(self.ser.in_waiting)
                    else:
                        time.sleep(0.001)
                        continue
                
                if self.is_recording and data:
                    with self.lock:
                        self.buffer.extend(data)
                        # Debug: mostrar progresso
                        if len(self.buffer) % 16000 == 0:
                            print(f"Recebido: {len(self.buffer)} bytes")
                    
            except Exception as e:
                print(f"Erro na recepção: {e}")
                break

class VoiceAssistant:
    def __init__(self):
        self.wake_words = ['ok google', 'hey google', 'assistente', 'carro']
        
        # Inicializar Arduino
        self.arduino_mic = ArduinoMicrophone(use_wifi=USE_WIFI)
        
        # Thread para receber dados
        self.receive_thread = threading.Thread(target=self.arduino_mic.receive_loop)
        self.receive_thread.daemon = True
        self.receive_thread.start()
        
        # Reconhecimento e síntese
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 50  # Reduzir para PDM com baixa amplitude
        self.recognizer.pause_threshold = 0.8
        self.recognizer.dynamic_energy_threshold = False
        
        self.tts = pyttsx3.init()
        self.setup_tts()
        
        # Comandos (simplificado para teste)
        self.commands = {
            'teste': lambda: self.speak("Teste OK"),
            'status': lambda: self.speak("Sistema funcionando"),
        }
        
    def setup_tts(self):
        voices = self.tts.getProperty('voices')
        for voice in voices:
            if 'brazil' in voice.name.lower() or 'pt' in voice.name.lower():
                self.tts.setProperty('voice', voice.id)
                print(f"Voz PT-BR: {voice.name}")
                break
        
        self.tts.setProperty('rate', 160)
        self.tts.setProperty('volume', 0.85)
    
    def speak(self, text):
        print(f"Assistente: {text}")
        self.tts.say(text)
        self.tts.runAndWait()
    
    def listen_for_command(self):
        try:
            print("\n🎤 Escutando...")
            
            # Gravar por tempo fixo
            self.arduino_mic.start_recording()
            time.sleep(4)  # 4 segundos de gravação
            audio = self.arduino_mic.stop_recording()
            
            if audio is None:
                print("Erro: Sem áudio capturado")
                return None
            
            # Tentar reconhecer
            try:
                text = self.recognizer.recognize_google(audio, language='pt-BR')
                print(f"Você disse: {text}")
                return text.lower()
            except sr.UnknownValueError:
                print("Não entendi o áudio")
                return None
            except sr.RequestError as e:
                print(f"Erro no serviço: {e}")
                return None
                
        except Exception as e:
            print(f"Erro geral: {e}")
            return None
    
    def process_command(self, text):
        if not text:
            return
            
        # Verificar wake words
        for wake_word in self.wake_words:
            if wake_word in text:
                command = text.replace(wake_word, '').strip()
                
                # Processar comando
                for key, action in self.commands.items():
                    if key in command:
                        action()
                        return
                        
                self.speak("Comando não reconhecido")
                return
    
    def test_audio_input(self):
        """Teste básico de entrada de áudio"""
        print("\n=== TESTE DE ÁUDIO ===")
        print("Gravando 2 segundos de teste...")
        
        self.arduino_mic.start_recording()
        time.sleep(2)
        audio = self.arduino_mic.stop_recording()
        
        if audio:
            print("✅ Áudio capturado com sucesso")
            # Salvar para debug
            with open("test_audio.wav", "wb") as f:
                f.write(audio.get_wav_data())
            print("Áudio salvo em test_audio.wav")
        else:
            print("❌ Falha na captura de áudio")
    
    def start_listening(self):
        self.speak("Sistema iniciado")
        
        # Teste inicial
        self.test_audio_input()
        
        while True:
            try:
                text = self.listen_for_command()
                if text:
                    self.process_command(text)
                    
                    if any(word in text for word in ['sair', 'tchau', 'parar']):
                        self.speak("Encerrando")
                        break
                        
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
        import traceback
        traceback.print_exc()