import os
from google import genai
from dotenv import load_dotenv

# Carrega a chave do .env com segurança
load_dotenv()
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_KEY:
    raise ValueError("GEMINI_API_KEY não encontrada no arquivo .env!")

# Inicializa o novo cliente oficial do Google GenAI
client = genai.Client(api_key=GEMINI_KEY)

# Cria a sessão de chat com histórico e instruções de sistema (system instruction)
chat_sessao = client.chats.create(
    model="gemini-3.5-flash-lite",
    config={
        "system_instruction": "Você é o Jarvis, um assistente virtual inteligente, direto e conciso. Suas respostas serão lidas em voz alta por um sistema de áudio, portanto, seja breve e evite formatações complexas como listas longas ou markdown.",
        "temperature": 0.7,
        "thinking_level": "low"
    }
)

def perguntar_ao_gemini(texto_pergunta):
    """Envia o texto para a sessão de chat do Gemini mantendo o contexto com o novo SDK"""
    try:
        print("[JARVIS]: Consultando o Gemini...")
        # Envia a mensagem para o chat mantendo a memória local da sessão
        resposta = chat_sessao.send_message(texto_pergunta)
        return resposta.text
    except Exception as e:
        return f"Desculpe, ocorreu um erro ao consultar a inteligência artificial: {e}"