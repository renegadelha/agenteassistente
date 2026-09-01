import os
import subprocess

# Caminho para o modelo ONNX baixado
MODELO_PATH = "voices/pt_BR-faber-medium.onnx"

def gerar_audio_piper(texto, arquivo_saida="resposta.wav"):
    """Gera o arquivo WAV usando o Piper via linha de comando"""
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

def tocar_audio_nativo(caminho_arquivo):
    """Reproduz o arquivo WAV usando o reprodutor nativo do Linux (aplay)"""
    try:
        # Toca o áudio bloqueando a execução até terminar (comportamento desejado)
        subprocess.run(["aplay", "-q", caminho_arquivo], check=True)

    except Exception as e:
        print(f"[ERRO NO ÁUDIO]: Falha ao tocar com aplay -> {e}")
    finally:
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
    tocar_audio_nativo(arquivo_wav)