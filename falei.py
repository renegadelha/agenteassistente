import os
import sys
import subprocess
import wave

from piper.voice import PiperVoice


# Caminhos para o modelo
MODELO_PATH = "voices/pt_BR-faber-medium.onnx"
CONFIG_PATH = "voices/pt_BR-faber-medium.onnx.json"


# Carrega o modelo do Piper na memória
print("[INFO] Carregando modelo do Piper TTS...")

voz_piper = PiperVoice.load(
    MODELO_PATH,
    config_path=CONFIG_PATH
)

print("[INFO] Modelo carregado com sucesso!")


def falar_texto(texto):
    """Gera o áudio usando Piper TTS e reproduz pela caixa de som."""

    if not texto.strip():
        return

    print(f"[JARVIS FALANDO]: {texto}")

    arquivo_audio = "resposta.wav"

    try:

        # 1. Gera o arquivo WAV
        with wave.open(arquivo_audio, "wb") as wav_file:
            voz_piper.synthesize(texto, wav_file)

        print("[INFO] Áudio gerado.")

        # 2. Reproduz pela saída de áudio
        subprocess.run(
            [
                "ffplay",
                "-nodisp",
                "-autoexit",
                "-loglevel",
                "quiet",
                arquivo_audio
            ],
            check=True
        )

    except Exception as e:

        print(f"[ERRO NO TTS]: {e}")

    finally:

        # Remove o arquivo temporário
        if os.path.exists(arquivo_audio):
            print('falta remover o arquivo')
            #os.remove(arquivo_audio)


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Uso:")
        print("python3 falar.py \"Texto para falar\"")
        sys.exit(1)

    texto = " ".join(sys.argv[1:])

    falar_texto(texto)