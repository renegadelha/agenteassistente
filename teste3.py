import numpy as np
import openwakeword
from openwakeword.model import Model
from openwakeword import get_pretrained_model_paths
import speech_recognition as sr
import time
from pergunta_gemini import perguntar_ao_gemini

import os
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env local
load_dotenv()

# Puxa a chave com segurança para uma variável
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_KEY:
    raise ValueError("Atenção: A chave da API do Gemini não foi encontrada no arquivo .env!")

# 1. Configurações de Áudio
RATE = 48000
CHUNK_SIZE_48K = 1280 * 3
DEVICE_INDEX = 0  # Microfone na Orange Pi

# 2. Inicializar o modelo do Jarvis
print("[INFO] Buscando modelo 'hey_jarvis'...")
caminhos = get_pretrained_model_paths()
jarvis_paths = [p for p in caminhos if "hey_jarvis" in p.lower()]

if not jarvis_paths:
    raise ValueError("Modelo 'hey_jarvis' não foi encontrado.")

print(f"[INFO] Modelo carregado: {jarvis_paths[0]}")
oww_model = Model(wakeword_model_paths=[jarvis_paths[0]])

recognizer = sr.Recognizer()

# --- AJUSTES CRÍTICOS PARA NÃO CORTAR O FINAL DA FALA ---
recognizer.pause_threshold = 1.5  # Tempo de silêncio (em segundos) necessário para o Google entender que você terminou de falar (padrão é 0.8)
recognizer.non_speaking_duration = 0.8  # Tempo de áudio sem fala considerado antes de fechar a escuta

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
                    if perguntei:
                        print("\n[FANTASMA IGNORADO] Detecção falsa logo após a resposta.")
                        oww_model.reset()
                        continue

                    print("\n🔥 JARVIS DETECTADO!")
                    break

                    # --- TRANSIÇÃO PARA A ESCUTA DA FRASE ---
            print("[JARVIS]: Sou todo ouvidos! Pode falar...")

            perguntei = True
            time.sleep(0.3)

            try:
                # phrase_time_limit aumentado para 20 segundos para dar tempo de falar frases completas
                audio_gravado = recognizer.listen(source, timeout=5, phrase_time_limit=20)
                print("[JARVIS]: Processando sua voz...")

                texto = recognizer.recognize_google(audio_gravado, language="pt-BR")

                print("\n" + "=" * 40)
                print(f"🗣️ PRONTO PARA ENVIAR À IA: '{texto}'")
                print("=" * 40 + "\n")
                resposta_ia = perguntar_ao_gemini(texto)
                print(f"🗣️ A RESPOSTA FOI: '{resposta_ia}'")

            except sr.WaitTimeoutError:
                print("[ERRO]: Você demorou muito para falar.")
            except sr.UnknownValueError:
                print("[ERRO]: Não entendi o que você disse.")
            except Exception as e:
                print(f"[ERRO]: Falha no reconhecimento -> {e}")

            # --- FIM DO CICLO DE PERGUNTA (BLINDAGEM ANTI-ECO) ---
            print("[INFO] Entrando em modo de blindagem pós-resposta...")

            oww_model.reset()

            tempo_limpeza = time.time() + 2.5
            while time.time() < tempo_limpeza:
                try:
                    source.stream.read(CHUNK_SIZE_48K)
                except:
                    pass

            perguntei = False

except KeyboardInterrupt:
    print("\n[INFO] Encerrando o assistente pacificamente...")