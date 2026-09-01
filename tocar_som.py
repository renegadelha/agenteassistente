import subprocess

#MODELO_PATH = "voices/pt_BR-faber-medium.onnx"
MODELO_PATH = "voices/pt_BR-edresson-low.onnx"




def falar_resposta(texto):
    """Gera e reproduz áudio via streaming em tempo real com alta performance"""
    if not texto or not texto.strip():
        return

    print("[TTS]: Sintetizando e reproduzindo áudio instantaneamente...")

    # --output-raw joga o fluxo de áudio puro direto na memória sem headers
    # --length-scale 0.9 (opcional) acelera levemente a velocidade da fala para dar mais agilidade
    comando_piper = [
        "python3", "-m", "piper",
        "--model", MODELO_PATH,
        "--output_raw",
        "--length-scale", "0.95"
    ]

    # Configuramos o aplay para o formato padrão do Piper (22050Hz, 16-bit, Mono)
    # Isso faz o som disparar de imediato na caixa USB
    comando_aplay = [
        "aplay", "-q",
        "-r", "22050",
        "-f", "S16_LE",
        "-c", "1"
    ]

    try:
        # Abre o processo do Piper
        piper_proc = subprocess.Popen(
            comando_piper,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL
        )

        # Abre o aplay conectado diretamente à saída do Piper
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


def falar_resposta2(texto):
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