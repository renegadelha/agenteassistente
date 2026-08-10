import numpy as np
import openwakeword
from openwakeword.model import Model
from openwakeword import get_pretrained_model_paths
import speech_recognition as sr
import time

# 1. Configurações de Áudio
RATE = 48000
CHUNK_SIZE_48K = 1280 * 3 
DEVICE_INDEX = 0   # Seu microfone USB Linux

# 2. Inicializar o modelo do Jarvis
print("[INFO] Buscando modelo 'hey_jarvis'...")
caminhos = get_pretrained_model_paths()
jarvis_paths = [p for p in caminhos if "hey_jarvis" in p.lower()]

if not jarvis_paths:
    raise ValueError("Modelo 'hey_jarvis' não foi encontrado.")

print(f"[INFO] Modelo carregado: {jarvis_paths[0]}")
oww_model = Model(wakeword_model_paths=[jarvis_paths[0]])
recognizer = sr.Recognizer()
recognizer.pause_threshold = 2
recognizer.non_speaking_duration = 0.5

# 3. Inicializar o Microfone ÚNICO
print("\n[INFO] Conectando ao microfone...")
mic = sr.Microphone(device_index=DEVICE_INDEX, sample_rate=RATE, chunk_size=CHUNK_SIZE_48K)

# Flag booleana de estado inicial
perguntei = False

try:
    with mic as source:
        print("[INFO] Calibrando ruído ambiente...")
        recognizer.adjust_for_ambient_noise(source, duration=1.0)
        
        while True:
            # Zera completamente a memória de predição do modelo
            oww_model.reset()
                
            print("\n🎙️ Aguardando... Diga 'Hey Jarvis'")
            
            # Loop secundário (Procurando o Wake Word)
            while True:
                raw_data = source.stream.read(CHUNK_SIZE_48K)
                audio_frame_48k = np.frombuffer(raw_data, dtype=np.int16)
                
                audio_frame_16k = audio_frame_48k[::3]
                audio_frame_16k = np.clip(audio_frame_16k * 3.0, -32768, 32767).astype(np.int16)
                
                oww_model.predict(audio_frame_16k)
                
                model_key = list(oww_model.prediction_buffer.keys())[0]
                scores = list(oww_model.prediction_buffer[model_key])
                
                if scores and scores[-1] > 0.7:
                    # Se a detecção ocorreu logo após termos terminado de perguntar E a flag ainda está ativa, ignoramos!
                    if perguntei:
                        print("\n[FANTASMA IGNORADO] Detecção falsa logo após a resposta.")
                        oww_model.reset()
                        continue
                    
                    print("\n🔥 JARVIS DETECTADO!")
                    break 
            
            # --- TRANSIÇÃO PARA A ESCUTA DA FRASE ---
            print("[JARVIS]: Sou todo ouvidos! Pode falar...")
            
            # Marcamos como True porque entramos em uma interação real gerada por voz
            perguntei = True
            
            try:
                # O usuário fala a frase aqui
                audio_gravado = recognizer.listen(source, timeout=5, phrase_time_limit=15)
                print("[JARVIS]: Processando sua voz...")
                
                texto = recognizer.recognize_google(audio_gravado, language="pt-BR")
                
                print("\n" + "="*40)
                print(f"🗣️ PRONTO PARA ENVIAR À IA: '{texto}'")
                print("="*40 + "\n")
                
            except sr.WaitTimeoutError:
                print("[ERRO]: Você demorou muito para falar.")
            except sr.UnknownValueError:
                print("[ERRO]: Não entendi o que você disse.")
            except Exception as e:
                print(f"[ERRO]: Falha no reconhecimento -> {e}")
            
            # --- FIM DO CICLO DE PERGUNTA (BLINDAGEM ANTI-ECO) ---
            print("[INFO] Entrando em modo de blindagem pós-resposta...")
            
            # 1. Reseta o modelo da IA
            oww_model.reset()
            
            # 2. Drena ativamente o buffer do microfone por 2.5 segundos jogando o lixo fora
            tempo_limpeza = time.time() + 2.5
            while time.time() < tempo_limpeza:
                try:
                    source.stream.read(CHUNK_SIZE_48K)
                except:
                    pass
            
            perguntei = False  # Libera a flag apenas após a limpeza física do buffer

except KeyboardInterrupt:
    print("\n[INFO] Encerrando o assistente pacificamente...")