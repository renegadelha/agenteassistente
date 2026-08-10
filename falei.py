import os
import sys
from piper.voice import Voice

# Caminho para o modelo baixado
MODELO_PATH = "voices/pt_BR-faber-medium.onnx"
CONFIG_PATH = "voices/pt_BR-faber-medium.onnx.json"

# Carrega a voz do Piper diretamente na memória (muito mais rápido e sem problemas de shell)
print("[INFO] Carregando modelo do Piper TTS...")
voz_piper = Voice.load(MODELO_PATH, config_path=CONFIG_PATH)


def falar_texto(texto):
    """Gera o áudio usando a API nativa do Piper e reproduz via ffplay"""
    if not texto.strip():
        return

    print(f"[JARVIS FALANDO]: {texto}")

    arquivo_audio = "resposta.wav"

    try:
        # 1. Usa a API do Piper para sintetizar o texto diretamente para um arquivo WAV
        import wave
        with wave.open(arquivo_audio, "wb") as wav_file:
            voz_piper.synthesize(texto, wav_file)

        # 2. Reproduz o áudio limpo usando o ffplay
        import subprocess
        subprocess.run(
            ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", arquivo_audio],
            check=True
        )

    except Exception as e:
        print(f"[ERRO NO TTS]: Falha ao sintetizar ou reproduzir voz -> {e}")
    finally:
        # Remove o arquivo temporário
        if os.path.exists(arquivo_audio):
            os.remove(arquivo_audio)

if __name__ == "__main__":
    nome = sys.argv[1]
    falar_texto(nome)