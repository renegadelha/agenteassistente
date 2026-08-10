import subprocess
import os
import sys

# Caminho para o modelo baixado do Piper
MODELO_PATH = "voices/pt_BR-faber-medium.onnx"


def falar_texto(texto):
    """Gera o áudio usando o Piper TTS e reproduz usando o ffplay"""
    if not texto.strip():
        return

    print(f"[JARVIS FALANDO]: {texto}")

    arquivo_audio = "resposta.wav"

    try:
        # 1. Gera o arquivo WAV via Piper
        comando_piper = f"echo '{texto}' | python3 -m piper --model {MODELO_PATH} --output_file {arquivo_audio}"
        subprocess.run(comando_piper, shell=True, check=True)

        # 2. Reproduz o áudio usando ffplay de forma limpa e silenciosa
        subprocess.run(
            ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", arquivo_audio],
            check=True
        )

    except Exception as e:
        print(f"[ERRO NO TTS]: Falha ao sintetizar ou reproduzir voz -> {e}")
    finally:
        # Limpa o arquivo temporário de áudio
        if os.path.exists(arquivo_audio):
            os.remove(arquivo_audio)

if __name__ == "__main__":
    nome = sys.argv[1]
    falar_texto(nome)