import os
import time
import subprocess
import pygame

# Caminho para o modelo ONNX baixado
MODELO_PATH = "voices/pt_BR-faber-medium.onnx"


def gerar_audio_piper(texto, arquivo_saida="resposta.wav"):
    """Gera o arquivo WAV usando o Piper via linha de comando (sem erros de import)"""
    print(f"[TTS]: Sintetizando resposta...")

    comando = [
        "python3", "-m", "piper",
        "--model", MODELO_PATH,
        "--output_file", arquivo_saida
    ]

    # Envia o texto com segurança para a entrada padrão (stdin) do Piper
    subprocess.run(
        comando,
        input=texto.encode("utf-8"),
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    return arquivo_saida


def tocar_audio_pygame(caminho_arquivo):
    """Reproduz o arquivo WAV no Linux Mint usando o Pygame"""
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(caminho_arquivo)
        pygame.mixer.music.play()

        # Aguarda a reprodução terminar
        while pygame.mixer.music.get_busy():
            time.sleep(0.05)

    except Exception as e:
        print(f"[ERRO NO ÁUDIO]: {e}")
    finally:
        pygame.mixer.quit()
        # Remove o arquivo temporário após tocar
        if os.path.exists(caminho_arquivo):
            try:
                os.remove(caminho_arquivo)
            except OSError:
                pass


def falar_resposta(resposta_ia):
    """Função principal: recebe o texto do Gemini, gera o WAV e toca"""
    if not resposta_ia or not resposta_ia.strip():
        return

    arquivo_wav = gerar_audio_piper(resposta_ia)
    tocar_audio_pygame(arquivo_wav)