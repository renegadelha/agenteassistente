import subprocess

MODELO_PATH = "voices/pt_BR-edresson-low.onnx"

def falar_resposta(texto):
    """Gera e reproduz áudio via streaming em tempo real com alta performance"""
    if not texto or not texto.strip():
        return

    print("[TTS]: Sintetizando e reproduzindo áudio instantaneamente...")

    comando_piper = [
        "python3", "-m", "piper",
        "--model", MODELO_PATH,
        "--output_raw",
        "--length_scale", "1" # Ajustado para underline caso o traço falhe
    ]

    comando_aplay = [
        "aplay", "-q",
        "-t", "raw",      # AVISA O APLAY QUE É ÁUDIO BRUTO SEM CABEÇALHO WAV
        "-r", "16000",
        "-f", "S16_LE",
        "-c", "1",
        "-"               # FORÇA A LEITURA DO STDIN
    ]

    try:
        # ATENÇÃO: Removi o DEVNULL do stderr do Piper.
        # Se o Piper der erro (ex: falta do .json), ele vai gritar no terminal agora!
        piper_proc = subprocess.Popen(
            comando_piper,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE
        )

        aplay_proc = subprocess.Popen(
            comando_aplay,
            stdin=piper_proc.stdout,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        # Envia o texto e fecha o canal de entrada
        piper_proc.stdin.write(texto.encode("utf-8"))
        piper_proc.stdin.close()

        # Aguarda a reprodução terminar
        aplay_proc.wait()

    except Exception as e:
        print(f"[ERRO NO ÁUDIO]: {e}")