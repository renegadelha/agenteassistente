import subprocess
import os

# Caminho para o modelo baixado
MODELO_PATH = "voices/pt_BR-faber-medium.onnx"


def falar_texto(texto):
    """Gera o áudio usando o Piper via linha de comando e reproduz no card 1 via aplay"""
    if not texto.strip():
        return

    print(f"[JARVIS FALANDO]: {texto}")

    arquivo_audio = "resposta.wav"

    try:
        # 1. Sintetiza o texto injetando via stdin de forma segura
        comando_piper = [
            "python3", "-m", "piper",
            "--model", MODELO_PATH,
            "--output_file", arquivo_audio
        ]

        subprocess.run(
            comando_piper,
            input=texto.encode("utf-8"),
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        # 2. Reproduz especificamente na placa analógica (card 1, device 0)
        subprocess.run(
            ["aplay", "-D", "plughw:1,0", arquivo_audio],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    except Exception as e:
        print(f"[ERRO NO TTS]: Falha ao sintetizar ou reproduzir voz -> {e}")
    finally:
        # Limpa o arquivo temporário com segurança
        if os.path.exists(arquivo_audio):
            try:
                os.remove(arquivo_audio)
            except:
                pass


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        falar_texto(" ".join(sys.argv[1:]))