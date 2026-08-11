import subprocess
import os

# Força o pygame a utilizar o driver ALSA diretamente na Orange Pi
os.environ['SDL_AUDIODRIVER'] = 'alsa'
import pygame

# Caminho para o modelo baixado do Piper
MODELO_PATH = "voices/pt_BR-faber-medium.onnx"


def falar_texto(texto):
    """Gera o áudio usando o Piper e reproduz de forma confiável usando o Pygame"""
    if not texto.strip():
        return

    print(f"[JARVIS FALANDO]: {texto}")

    arquivo_audio = "resposta.wav"

    try:
        # 1. Sintetiza o texto para WAV usando o Piper via linha de comando
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

        # 2. Inicializa o mixer do Pygame para tocar o áudio gerado
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=2048)
        except pygame.error as e:
            print(f"[ERRO PYGAME]: Falha ao inicializar o mixer -> {e}")
            return

        # Carrega e reproduz o arquivo WAV
        pygame.mixer.music.load(arquivo_audio)
        pygame.mixer.music.play()

        # Mantém o script pausado até o som terminar de rodar
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

        # Fecha o mixer para liberar a placa de som para o microfone
        pygame.mixer.quit()

    except Exception as e:
        print(f"[ERRO NO TTS]: Falha na síntese ou reprodução -> {e}")
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
    else:
        falar_texto("Olá Renê, sistema de som integrado com Pygame funcionando com sucesso.")