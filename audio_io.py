import os
import pyaudio
import numpy as np
import speech_recognition as sr
from gtts import gTTS
import openwakeword
from openwakeword.model import Model

class AudioHandler:
    def __init__(self):
        # Não precisamos mais de chave de API
        self.recognizer = sr.Recognizer()
        
        # Carrega o modelo de wake word (vamos usar 'alexa' que já vem nativo)
        print("[INFO] Carregando modelo openWakeWord...")
        openwakeword.utils.download_models() # Garante que os modelos padrão estão baixados
        self.oww_model = Model(wakeword_models=['hey_jarvis'])
        
    def wait_for_wake_word(self):
        """
        Fica em loop ouvindo a palavra de ativação usando openWakeWord.
        """
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000 # Taxa exigida pelo openWakeWord
        CHUNK = 1280 # Tamanho do bloco de áudio
        
        pa = pyaudio.PyAudio()
        audio_stream = pa.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK
        )
        
        print("[INFO] Aguardando a palavra mágica ('Alexa')...")
        
        try:
            while True:
                # Lê o áudio do microfone
                pcm = audio_stream.read(CHUNK, exception_on_overflow=False)
                # Converte para array do numpy para a rede neural processar
                audio_data = np.frombuffer(pcm, dtype=np.int16)
                
                # O modelo retorna um dicionário com a pontuação de confiança
                prediction = self.oww_model.predict(audio_data)
                
                # Verifica se a confiança passou do limiar (threshold de 0.5)
                for mdl in prediction.keys():
                    if prediction[mdl] > 0.5:
                        print(f"\n[INFO] Wake word detectada! (Score: {prediction[mdl]:.2f})")
                        return # Sai do loop para iniciar a gravação do comando
                        
        finally:
            audio_stream.stop_stream()
            audio_stream.close()
            pa.terminate()

    def record_command(self):
        """
        Grava o comando de voz após o wake word e converte em texto.
        """
        with sr.Microphone() as source:
            print("[INFO] Ouvindo o seu comando...")
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5) 
            try:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=15)
                print("[INFO] Processando áudio...")
                text = self.recognizer.recognize_google(audio, language="pt-BR")
                print(f"[VOCÊ]: {text}")
                return text
            except sr.WaitTimeoutError:
                print("[ERRO] Tempo esgotado. Nenhum comando detectado.")
                return None
            except sr.UnknownValueError:
                print("[ERRO] Não entendi o que foi dito.")
                return None
            except Exception as e:
                print(f"[ERRO] Falha no reconhecimento: {e}")
                return None

    def speak(self, text):
        """
        Gera o áudio usando gTTS e reproduz via mpg123 no Linux.
        """
        if not text:
            return
            
        print(f"[ASSISTENTE]: {text}")
        try:
            tts = gTTS(text=text, lang="pt-br")
            audio_file = "resposta.mp3"
            tts.save(audio_file)
            
            os.system(f"mpg123 -q {audio_file}")
            
            if os.path.exists(audio_file):
                os.remove(audio_file)
        except Exception as e:
            print(f"[ERRO] Falha ao reproduzir áudio: {e}")