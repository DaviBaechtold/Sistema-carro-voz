#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Assistente de Voz para Carro - Versão Dev Board
Otimizado para Google Dev Board (AA1) com configurações específicas
"""

import speech_recognition as sr
import pyttsx3
import time
import threading
import os
import re
import warnings
import sys
import json
import logging
from datetime import datetime
import subprocess

# Configurar logging para o Dev Board
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/voice_assistant.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Configurações específicas do Dev Board
DEV_BOARD_CONFIG = {
    'cpu_temp_limit': 75,  # Limite de temperatura em Celsius
    'memory_limit': 80,    # Limite de uso de memória em %
    'auto_restart_on_error': True,
    'network_timeout': 30,
    'audio_retry_attempts': 3
}

# Redirecionar stderr do ALSA para /dev/null
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

# Suprimir logs do ALSA
os.environ['ALSA_PCM_CARD'] = '0'
os.environ['ALSA_PCM_DEVICE'] = '0'
warnings.filterwarnings("ignore")

class DevBoardVoiceAssistant:
    def __init__(self):
        logger.info("🚗 Iniciando Assistente de Voz - Dev Board")
        
        # Wake words
        self.wake_words = ['ok google', 'hey google', 'assistente', 'carro']
        self.is_listening = False
        
        # Configurações do Dev Board
        self.system_monitor = SystemMonitor()
        
        # Inicializar componentes
        self._init_speech_recognition()
        self._init_tts()
        self._setup_microphone()
        
        # Comandos
        self.commands = {
            'ligar para': self.make_call,
            'atender': self.answer_call,
            'desligar chamada': self.end_call,
            'tocar música': self.play_music,
            'tocar': self.play_specific,
            'aumentar volume': self.volume_up,
            'diminuir volume': self.volume_down,
            'próxima': self.next_track,
            'anterior': self.previous_track,
            'navegar para': self.navigate_to,
            'onde estou': self.current_location,
            'cancelar rota': self.cancel_route,
            'enviar mensagem': self.send_message,
            'última mensagem': self.read_last_message,
            'ajuda': self.help,
            'status do sistema': self.system_status,
            'temperatura': self.check_temperature
        }
        
    def _init_speech_recognition(self):
        """Inicializar reconhecimento de voz com retry"""
        for attempt in range(DEV_BOARD_CONFIG['audio_retry_attempts']):
            try:
                self.recognizer = sr.Recognizer()
                self.microphone = sr.Microphone()
                logger.info("✅ Reconhecimento de voz inicializado")
                return
            except Exception as e:
                logger.warning(f"Tentativa {attempt + 1} falhou: {e}")
                time.sleep(2)
        
        logger.error("❌ Falha ao inicializar reconhecimento de voz")
        raise Exception("Não foi possível inicializar o microfone")
    
    def _init_tts(self):
        """Inicializar TTS com configurações otimizadas"""
        try:
            with SuppressStderr():
                self.tts = pyttsx3.init()
            
            # Configurar voz
            voices = self.tts.getProperty('voices')
            if voices:
                # Procurar voz em português
                for voice in voices:
                    if any(keyword in voice.name.lower() for keyword in ['pt', 'brazil', 'portuguese', 'brasil']):
                        self.tts.setProperty('voice', voice.id)
                        logger.info(f"Voz portuguesa selecionada: {voice.name}")
                        break
            
            # Configurações otimizadas para carro
            self.tts.setProperty('rate', 150)    # Mais lento para ambiente ruidoso
            self.tts.setProperty('volume', 0.9)   # Volume alto para carro
            
            logger.info("✅ TTS configurado")
            
        except Exception as e:
            logger.error(f"Erro ao configurar TTS: {e}")
            raise
    
    def _setup_microphone(self):
        """Configurar microfone com ajuste automático"""
        try:
            with SuppressStderr():
                with self.microphone as source:
                    # Ajuste mais agressivo para ambiente de carro
                    self.recognizer.adjust_for_ambient_noise(source, duration=3)
                    # Configurar energia para ambiente ruidoso
                    self.recognizer.energy_threshold = max(self.recognizer.energy_threshold, 4000)
                    logger.info(f"Microfone configurado - Energia: {self.recognizer.energy_threshold}")
        except Exception as e:
            logger.error(f"Erro ao configurar microfone: {e}")
    
    def speak(self, text):
        """Falar com verificação de temperatura"""
        if self.system_monitor.is_overheating():
            logger.warning("🌡️ Sistema aquecido - reduzindo operações")
            return
            
        logger.info(f"Assistente: {text}")
        try:
            with SuppressStderr():
                self.tts.say(text)
                self.tts.runAndWait()
        except Exception as e:
            logger.error(f"Erro no TTS: {e}")
    
    def listen_for_wake_word_and_command(self):
        """Escutar comando com otimizações para carro"""
        try:
            with SuppressStderr():
                with self.microphone as source:
                    # Timeout mais curto para economia de energia
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=6)
            
            # Reconhecimento com timeout para evitar travamento
            full_command = self.recognizer.recognize_google(
                audio, 
                language='pt-BR',
                show_all=False
            )
            
            full_command_lower = full_command.lower()
            
            # Verificar wake word
            wake_word_found = None
            for wake_word in self.wake_words:
                if wake_word in full_command_lower:
                    wake_word_found = wake_word
                    break
            
            if wake_word_found:
                command = full_command_lower.replace(wake_word_found, '').strip()
                command = re.sub(r'^[,.\s]+', '', command)
                
                logger.info(f"Wake word '{wake_word_found}' - Comando: '{command}'")
                return command if command else None
                
            return None
            
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            logger.debug("Comando não compreendido")
            return None
        except sr.RequestError as e:
            logger.error(f"Erro no serviço de reconhecimento: {e}")
            return None
        except Exception as e:
            logger.error(f"Erro inesperado no reconhecimento: {e}")
            return None
    
    def process_command(self, command):
        """Processar comando com logging"""
        if not command:
            return
            
        logger.info(f"Processando comando: {command}")
        
        # Buscar comando
        for keyword, action in self.commands.items():
            if keyword in command:
                try:
                    if keyword in ['ligar para', 'tocar', 'navegar para', 'enviar mensagem']:
                        action(command)
                    else:
                        action()
                    return
                except Exception as e:
                    logger.error(f"Erro ao executar comando '{keyword}': {e}")
                    self.speak("Desculpe, ocorreu um erro ao executar o comando")
                    return
        
        # Comando não reconhecido
        logger.info(f"Comando não reconhecido: {command}")
        self.speak("Comando não reconhecido. Diga 'ajuda' para ver os comandos.")
    
    # === COMANDOS ESPECÍFICOS DO DEV BOARD ===
    def system_status(self):
        """Status do sistema Dev Board"""
        status = self.system_monitor.get_status()
        self.speak(f"Temperatura: {status['temperature']} graus. "
                  f"Memória: {status['memory_usage']} por cento usada. "
                  f"Sistema funcionando normalmente.")
    
    def check_temperature(self):
        """Verificar temperatura do sistema"""
        temp = self.system_monitor.get_temperature()
        if temp > 70:
            self.speak(f"Atenção: temperatura alta de {temp} graus celsius")
        else:
            self.speak(f"Temperatura normal: {temp} graus celsius")
    
    # === COMANDOS BÁSICOS (versões simplificadas) ===
    def make_call(self, command):
        contact = command.replace('ligar para', '').strip()
        if contact:
            self.speak(f"Simulando ligação para {contact}")
            logger.info(f"Comando de ligação para: {contact}")
        else:
            self.speak("Para quem você quer ligar?")
    
    def answer_call(self):
        self.speak("Simulando atendimento de chamada")
        logger.info("Comando: atender chamada")
    
    def end_call(self):
        self.speak("Simulando encerramento de chamada")
        logger.info("Comando: encerrar chamada")
    
    def play_music(self):
        self.speak("Simulando reprodução de música")
        logger.info("Comando: tocar música")
    
    def play_specific(self, command):
        content = command.replace('tocar', '').strip()
        if content:
            self.speak(f"Simulando reprodução de {content}")
            logger.info(f"Comando: tocar {content}")
        else:
            self.speak("O que você quer ouvir?")
    
    def volume_up(self):
        self.speak("Simulando aumento de volume")
        logger.info("Comando: aumentar volume")
    
    def volume_down(self):
        self.speak("Simulando diminuição de volume")
        logger.info("Comando: diminuir volume")
    
    def next_track(self):
        self.speak("Simulando próxima música")
        logger.info("Comando: próxima música")
    
    def previous_track(self):
        self.speak("Simulando música anterior")
        logger.info("Comando: música anterior")
    
    def navigate_to(self, command):
        destination = command.replace('navegar para', '').strip()
        if destination:
            self.speak(f"Simulando navegação para {destination}")
            logger.info(f"Comando: navegar para {destination}")
        else:
            self.speak("Para onde você quer ir?")
    
    def current_location(self):
        self.speak("Simulando localização atual")
        logger.info("Comando: onde estou")
    
    def cancel_route(self):
        self.speak("Simulando cancelamento de rota")
        logger.info("Comando: cancelar rota")
    
    def send_message(self, command):
        contact = command.replace('enviar mensagem para', '').strip()
        if contact:
            self.speak(f"Simulando envio de mensagem para {contact}")
            logger.info(f"Comando: enviar mensagem para {contact}")
        else:
            self.speak("Para quem você quer enviar mensagem?")
    
    def read_last_message(self):
        self.speak("Simulando leitura da última mensagem")
        logger.info("Comando: ler última mensagem")
    
    def help(self):
        help_text = ("Comandos disponíveis: ligar para, tocar música, navegar para, "
                    "aumentar volume, status do sistema, temperatura, ajuda")
        self.speak(help_text)
        logger.info("Comando: ajuda")
    
    def start_listening(self):
        """Loop principal otimizado para Dev Board"""
        logger.info("🎤 Assistente pronto - aguardando comandos")
        self.speak("Assistente de voz do carro iniciado")
        
        self.is_listening = True
        error_count = 0
        max_errors = 10
        
        while self.is_listening:
            try:
                # Verificar condições do sistema
                if self.system_monitor.should_throttle():
                    logger.warning("Sistema sobrecarregado - pausando")
                    time.sleep(5)
                    continue
                
                # Escutar comando
                command = self.listen_for_wake_word_and_command()
                if command:
                    error_count = 0  # Reset contador de erros
                    self.process_command(command)
                    
                    # Verificar comando de encerramento
                    if any(word in command for word in ['tchau', 'obrigado', 'até logo', 'pode parar', 'encerrar']):
                        logger.info("Comando de encerramento recebido")
                        break
                
                time.sleep(0.1)
                
            except KeyboardInterrupt:
                logger.info("Interrupção pelo usuário")
                break
            except Exception as e:
                error_count += 1
                logger.error(f"Erro no loop principal ({error_count}/{max_errors}): {e}")
                
                if error_count >= max_errors:
                    logger.critical("Muitos erros consecutivos - encerrando")
                    break
                    
                time.sleep(2)  # Pausa antes de tentar novamente
        
        logger.info("🔴 Assistente encerrado")
        self.speak("Assistente encerrado")

class SystemMonitor:
    """Monitor do sistema para Dev Board"""
    
    def get_temperature(self):
        """Obter temperatura do CPU"""
        try:
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                temp = int(f.read().strip()) / 1000
            return round(temp, 1)
        except:
            return 0
    
    def get_memory_usage(self):
        """Obter uso de memória"""
        try:
            with open('/proc/meminfo', 'r') as f:
                lines = f.readlines()
            
            total = int([l for l in lines if 'MemTotal' in l][0].split()[1])
            available = int([l for l in lines if 'MemAvailable' in l][0].split()[1])
            
            usage = ((total - available) / total) * 100
            return round(usage, 1)
        except:
            return 0
    
    def get_status(self):
        """Status completo do sistema"""
        return {
            'temperature': self.get_temperature(),
            'memory_usage': self.get_memory_usage(),
            'timestamp': datetime.now().isoformat()
        }
    
    def is_overheating(self):
        """Verificar se está superaquecendo"""
        return self.get_temperature() > DEV_BOARD_CONFIG['cpu_temp_limit']
    
    def should_throttle(self):
        """Verificar se deve reduzir operações"""
        temp = self.get_temperature()
        memory = self.get_memory_usage()
        
        return (temp > DEV_BOARD_CONFIG['cpu_temp_limit'] or 
                memory > DEV_BOARD_CONFIG['memory_limit'])

if __name__ == "__main__":
    try:
        logger.info("=== Assistente de Voz para Carro - Dev Board ===")
        assistant = DevBoardVoiceAssistant()
        assistant.start_listening()
    except Exception as e:
        logger.critical(f"Falha crítica: {e}")
        sys.exit(1)
