import pyaudio
import numpy as np
import openwakeword
from openwakeword.model import Model
from openwakeword import get_pretrained_model_paths
import speech_recognition as sr  # Importamos o STT
import time

# 1. Configurações de Áudio
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 48000
CHUNK_SIZE_48K = 1280 * 3 
DEVICE_INDEX = 4   # Seu microfone USB Linux

# 2. Inicializar o modelo do Jarvis
print("[INFO] Buscando modelo 'hey_jarvis'...")
caminhos = get_pretrained_model_paths()
jarvis_paths = [p for p in caminhos if "hey_jarvis" in p.lower()]

if not jarvis_paths:
    raise ValueError("Modelo 'hey_jarvis' não foi encontrado.")

jarvis_path = jarvis_paths[0]
print(f"[INFO] Modelo carregado: {jarvis_path}")
oww_model = Model(wakeword_model_paths=[jarvis_path])

# Instancia o PyAudio uma única vez
audio = pyaudio.PyAudio()

def escutar_comando():
    """Abre o microfone, grava o áudio e converte em texto (STT)"""
    recognizer = sr.Recognizer()
    
    # Usamos a mesma taxa (48kHz) e o mesmo índice do microfone USB
    with sr.Microphone(device_index=DEVICE_INDEX, sample_rate=RATE) as source:
        print("\n[JARVIS]: Sou todo ouvidos! Pode falar...")
        
        # Ajusta silenciosamente o ruído de fundo (meio segundo)
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        
        try:
            # Escuta até você parar de falar
            audio_gravado = recognizer.listen(source, timeout=5, phrase_time_limit=15)
            print("[JARVIS]: Processando sua voz...")
            
            # Envia para a API gratuita do Google para converter em texto
            texto = recognizer.recognize_google(audio_gravado, language="pt-BR")
            return texto
            
        except sr.WaitTimeoutError:
            print("[ERRO]: Você demorou muito para falar.")
            return None
        except sr.UnknownValueError:
            print("[ERRO]: Não entendi o que você disse.")
            return None
        except Exception as e:
            print(f"[ERRO]: Falha no reconhecimento -> {e}")
            return None


try:
    # Loop principal (Orquestrador)
    while True:
        # Pausa dramática para o Linux finalizar processos anteriores do microfone
        time.sleep(0.5)
        
        # 1. ABRE o microfone para o Wake Word
        mic_stream = audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            input_device_index=DEVICE_INDEX,
            frames_per_buffer=CHUNK_SIZE_48K
        )
        
        # --- SOLUÇÃO DEFINITIVA: MEGA FLUSH NO BUFFER ---
        # 15 blocos de 48kHz = ~1.2 segundos de áudio antigo destruído
        for _ in range(15):
            mic_stream.read(CHUNK_SIZE_48K, exception_on_overflow=False)
            
        # Zera a memória de predição do Jarvis estritamente após a limpeza
        oww_model.reset() 
        
        print("\n🎙️ Aguardando... Diga 'Hey Jarvis'")
        
        # Loop secundário (Escuta contínua do Wake Word)
        while True:
            raw_data = mic_stream.read(CHUNK_SIZE_48K, exception_on_overflow=False)
            audio_frame_48k = np.frombuffer(raw_data, dtype=np.int16)
            
            # Downsample para 16kHz
            audio_frame_16k = audio_frame_48k[::3]
            
            # Amplificação
            audio_frame_16k = np.clip(audio_frame_16k * 3.0, -32768, 32767).astype(np.int16)
            
            oww_model.predict(audio_frame_16k)
            
            model_key = list(oww_model.prediction_buffer.keys())[0]
            scores = list(oww_model.prediction_buffer[model_key])
            
            if scores:
                if scores[-1] > 0.7 and not perguntei:
                    print("\n JARVIS DETECTADO!")
                    perguntei = True
                    break 
        
        # 2. FECHA o microfone do Wake Word 
        mic_stream.stop_stream()
        mic_stream.close()
        
        # 3. ESCUTA A PERGUNTA (STT)
        comando_texto = escutar_comando()
        
        if comando_texto:
            print("\n" + "="*40)
            print(f"🗣️ PRONTO PARA ENVIAR À IA: '{comando_texto}'")
            print("="*40 + "\n")

except KeyboardInterrupt:
    print("\nEncerrando o assistente...")
finally:
    if 'mic_stream' in locals() and mic_stream.is_active():
        mic_stream.stop_stream()
        mic_stream.close()
    audio.terminate()