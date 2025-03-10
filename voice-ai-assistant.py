import sounddevice as sd
import soundfile as sf
import speech_recognition as sr
import openai
import os
from playsound import playsound  # Biblioteca para tocar áudio bloqueando execução

# Configuração da chave da API da OpenAI como variável de ambiente
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Parâmetros de gravação
DURATION = 3  # Tempo de gravação em segundos
SAMPLE_RATE = 44100  # Taxa de amostragem
AUDIO_FILE = "user_audio.wav"

# Função para tocar áudio e esperar até terminar
def tocar_audio(nome_arquivo):
    if os.path.exists(nome_arquivo):
        print(f"Tocando: {nome_arquivo}...")
        playsound(nome_arquivo)  # Bloqueia até o áudio finalizar
    else:
        print(f"Arquivo {nome_arquivo} não encontrado!")

# Gravar áudio do usuário
def gravar_audio():
    print("Fale agora...")
    audio = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype="int16")
    sd.wait()
    sf.write(AUDIO_FILE, audio, SAMPLE_RATE)
    print("Áudio gravado!")

# Reconhecer fala usando SpeechRecognition
def reconhecer_audio():
    recognizer = sr.Recognizer()
    with sr.AudioFile(AUDIO_FILE) as source:
        audio_data = recognizer.record(source)
        try:
            texto = recognizer.recognize_google(audio_data, language="pt-BR").strip().lower()
            print(f'Você disse: "{texto}"')
            return texto
        except sr.UnknownValueError:
            print("Não foi possível entender.")
            return None
        except sr.RequestError as e:
            print(f"Erro no serviço de reconhecimento: {e}")
            return None

# Função para identificar a intenção usando a API OpenAI
def identificar_intencao(frase):
    if not OPENAI_API_KEY:
        print("Erro: Chave da OpenAI não configurada.")
        return "desconhecido"

    prompt = f"""
    Identifique a intenção do usuário com base na frase abaixo. Responda apenas com uma única palavra, entre:
    - saldo
    - simulação
    - atendente
    - sair
    - desconhecido (se a intenção não for clara)

    Frase do usuário: "{frase}"
    """

    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        resposta = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "Você é um assistente que identifica intenções de atendimento bancário."},
                {"role": "user", "content": prompt}
            ]
        )

        intencao = resposta.choices[0].message.content.strip().lower()
        print(f"Intenção detectada: {intencao}")
        return intencao
    except Exception as e:
        print(f"Erro ao conectar com a API da OpenAI: {e}")
        return "desconhecido"

# Fluxo principal do atendimento eletrônico
def atendimento_eletronico():
    print("Atendimento eletrônico iniciado.")
    tocar_audio("boas_vindas.mp3")  # Mensagem de boas-vindas
    
    while True:
        print("\nDiga uma frase completa, como: 'Quero saber meu saldo', 'Preciso falar com um atendente' ou 'Quero fazer uma simulação'.")
        gravar_audio()
        resposta = reconhecer_audio()

        if not resposta:
            print("Nenhuma resposta reconhecida. Tente novamente.")
            tocar_audio("nao_reconhecido.mp3")
            continue  # Volta para o início do loop

        intencao = identificar_intencao(resposta)

        opcoes = {
            "saldo": "saldo.mp3",
            "simulação": "simulacao.mp3",
            "simulacao": "simulacao.mp3",
            "atendente": "atendente.mp3",
            "sair": "sair.mp3"
        }

        if intencao in opcoes:
            tocar_audio(opcoes[intencao])  # Reproduzir o áudio correspondente
            print("Atendimento encerrado.")
            break  # Encerra o atendimento após tocar o áudio

        else:
            print("Opção não reconhecida. Tente novamente.")
            tocar_audio("nao_reconhecido.mp3")
            # Continua no loop até o usuário fornecer uma opção válida

# Executar o atendimento eletrônico
if __name__ == "__main__":
    atendimento_eletronico()
