import subprocess

MODELO_PATH = "voices/pt_BR-faber-medium.onnx"


def falar_resposta(texto):
    """Gera o áudio e toca simultaneamente via pipeline, sem salvar em disco"""
    if not texto or not texto.strip():
        return

    print("[TTS]: Sintetizando e reproduzindo áudio em tempo real...")

    # O traço '-' no output diz ao Piper para jogar o áudio direto na memória
    comando_piper = [
        "python3", "-m", "piper",
        "--model", MODELO_PATH,
        "--output_file", "-"
    ]

    # O aplay recebe o áudio da memória e toca imediatamente
    comando_aplay = ["aplay", "-q", "-"]

    try:
        # Abre o processo do Piper
        piper_proc = subprocess.Popen(
            comando_piper,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL
        )

        # Abre o processo do aplay conectado à saída do Piper
        aplay_proc = subprocess.Popen(
            comando_aplay,
            stdin=piper_proc.stdout,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        # Envia a resposta da IA para o Piper
        piper_proc.stdin.write(texto.encode("utf-8"))
        piper_proc.stdin.close()  # Avisa que o texto acabou

        # Aguarda a caixa de som terminar de tocar
        aplay_proc.wait()

    except Exception as e:
        print(f"[ERRO NO ÁUDIO]: {e}")