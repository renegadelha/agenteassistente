import os
import sys
import subprocess
import wave

from piper.voice import PiperVoice


MODELO_PATH = "voices/pt_BR-faber-medium.onnx"
CONFIG_PATH = "voices/pt_BR-faber-medium.onnx.json"

print("[INFO] Carregando modelo do Piper TTS...")

voz_piper = PiperVoice.load(
    MODELO_PATH,
    config_path=CONFIG_PATH
)

print("[INFO] Modelo carregado com sucesso!")


def falar_texto(texto):

    if not texto.strip():
        return

    print(f"[JARVIS FALANDO]: {texto}")

    arquivo_audio = "resposta.wav"

    try:

        # Gera o WAV
        with wave.open(arquivo_audio, "wb") as wav_file:
            voz_piper.synthesize(texto, wav_file)

        print("[INFO] Áudio gerado.")

        # Reproduz na saída analógica da Orange Pi
        subprocess.run(
            [
                "aplay",
                "-D",
                "plughw:CARD=ac200audio,DEV=0",
                arquivo_audio
            ],
            check=True
        )

        print("[INFO] Áudio reproduzido.")

    except Exception as e:

        print(f"[ERRO NO TTS]: {e}")

    finally:

        # Remove o arquivo mesmo se ocorrer erro
        if os.path.exists(arquivo_audio):
            try:
                #os.remove(arquivo_audio)
                print("[INFO] Arquivo temporário removido.")
            except Exception as e:
                print(f"[AVISO] Não foi possível remover {arquivo_audio}: {e}")


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Uso:")
        print('python3 falei.py "Texto para falar"')
        sys.exit(1)

    texto = " ".join(sys.argv[1:])

    falar_texto(texto)