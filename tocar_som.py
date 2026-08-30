from gtts import gTTS
import os


def falar_resposta(texto):
    """Converte o texto da IA em áudio MP3 e reproduz na saída padrão"""
    try:
        print("[ÁUDIO]: Convertendo texto em voz...")
        # Cria o áudio em português
        tts = gTTS(text=texto, lang='pt-br', slow=False)
        arquivo_audio = "resposta.mp3"
        tts.save(arquivo_audio)

        print("[ÁUDIO]: Reproduzindo na caixa P2...")
        # Usa o mpg123 para tocar o mp3 silenciosamente (-q)
        os.system(f"mpg123 -q {arquivo_audio}")

        # Apaga o arquivo após tocar para não lotar o cartão SD
        os.remove(arquivo_audio)

    except Exception as e:
        print(f"[ERRO]: Falha na reprodução de áudio -> {e}")