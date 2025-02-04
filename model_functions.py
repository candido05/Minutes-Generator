# -*- coding: utf-8 -*-
import os
from openai import OpenAI
import ffmpeg
import librosa
import noisereduce as nr
import soundfile as sf
from pydub import AudioSegment
import glob

# chave da API OpenAI
client = OpenAI(api_key="")  

def criar_pastas():
    """
    Cria todas as pastas necessárias para o processamento, organizadas por tipo de arquivo.
    """
    pastas = {
        "upload": "arquivos_upload",  # Pasta para o arquivo de upload (ex: video_teste_medio.mp4)
        "audio_segments": "segmentos_audio",  # Pasta para os segmentos de áudio
        "cleaned_audio": "audio_limpo",  # Pasta para os áudios limpos
        "cleaned_mp3": "audio_mp3_processado",  # Pasta para os áudios MP3 processados
        "transcricao": "transcricoes",  # Pasta para as transcrições de áudio
        "atas": "atas_parciais",  # Pasta para as atas parciais
        "ata_final": "ata_final",  # Pasta para a ata final consolidada
        "resumo_final": "resumo_final",  # Pasta para o resumo final
        "outros": "outros_arquivos"  # Pasta para outros arquivos gerados
    }

    for nome_pasta, caminho_pasta in pastas.items():
        if not os.path.exists(caminho_pasta):
            os.makedirs(caminho_pasta)
            print(f"Pasta '{caminho_pasta}' criada com sucesso para armazenar {nome_pasta}.")
        else:
            print(f"Pasta '{caminho_pasta}' já existe para armazenar {nome_pasta}.")

def upload_file(file_paths=None):
    """
    Permite o upload de arquivos manualmente ou processa arquivos já fornecidos.
    
    :param file_paths: Optional list of file paths to process directly.
    :return: tuple of file_path and file_type or (None, None) if no valid file.
    """
    if file_paths:
        for file_path in file_paths:
            if os.path.exists(file_path):
                file_ext = file_path.split('.')[-1].lower()
                if file_ext == "mp4":
                    return file_path, 'video'
                elif file_ext == "mp3":
                    return file_path, 'mp3'
                elif file_ext == "wav":
                    return file_path, 'wav'
            print(f"Arquivo {file_path} não encontrado ou não suportado.")
        return None, None
    else:
        # Original manual upload logic
        file_path = input("Digite o caminho completo do arquivo (MP4, MP3 ou WAV): ")
        if not os.path.exists(file_path):
            print("Arquivo não encontrado.")
            return None, None

        file_ext = file_path.split('.')[-1].lower()
        if file_ext == "mp4":
            return file_path, 'video'
        elif file_ext == "mp3":
            return file_path, 'mp3'
        elif file_ext == "wav":
            return file_path, 'wav'
        else:
            print("Tipo de arquivo não suportado.")
            return None, None

def check_file_size(audio_path, max_size_mb=25):
    """
    Verifica o tamanho do arquivo em MB.
    """
    file_size_mb = os.path.getsize(audio_path) / (1024 * 1024)  # Convertendo para MB
    print(f"Tamanho do arquivo: {file_size_mb:.2f} MB")
    return file_size_mb <= max_size_mb

def extract_and_split_audio_from_video(video_path, output_folder="segmentos_audio", max_segment_size_mb=24):
    """
    Extrai o áudio do vídeo e divide em segmentos menores que 24 MB.
    """
    #print("Extraindo áudio do vídeo...")
    audio_output_path = os.path.join(output_folder, "full_audio.wav")
    ffmpeg.input(video_path).output(audio_output_path, format='wav', acodec='pcm_s16le', ar='16000').run(quiet=True, overwrite_output=True)
    #print(f"Áudio extraído: {audio_output_path}")

    # Verificar e dividir o áudio
    return split_audio_into_segments(audio_output_path, output_folder, max_segment_size_mb)

def split_audio_into_segments(audio_path, output_folder, max_segment_size_mb):
    """
    Divide o áudio extraído em segmentos de até 24MB.
    """
    print(f"Dividindo áudio: {audio_path}")
    audio = AudioSegment.from_wav(audio_path)
    os.makedirs(output_folder, exist_ok=True)

    # Calcular a duração do segmento baseado no tamanho máximo
    bytes_per_second = len(audio.raw_data) / (len(audio) / 1000)
    max_duration_ms = (max_segment_size_mb * 1024 * 1024) / bytes_per_second * 1000

    segments = []
    for i, start_ms in enumerate(range(0, len(audio), int(max_duration_ms))):
        segment = audio[start_ms:start_ms + int(max_duration_ms)]
        segment_path = os.path.join(output_folder, f"segment_{i + 1}.wav")
        segment.export(segment_path, format="wav")
        segments.append(segment_path)
        print(f"Segmento criado: {segment_path} (Tamanho: {os.path.getsize(segment_path) / (1024 * 1024):.2f} MB)")

    return segments

def process_audio_mp3(mp3_path, output_dir):
    """
    Processa o áudio MP3, reduzindo ruído e salvando o arquivo limpo.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"Reduzindo ruído: {mp3_path}")
    audio_data, sr = librosa.load(mp3_path, sr=None)
    reduced_noise = nr.reduce_noise(y=audio_data, sr=sr)

    output_audio_path = os.path.join(output_dir, f"cleaned_{os.path.basename(mp3_path)}")
    sf.write(output_audio_path, reduced_noise, sr)
    print(f"Áudio limpo salvo em: {output_audio_path}")
    return output_audio_path

def process_audio_wav(wav_path, output_folder):
    """
    Processa o áudio WAV diretamente dividindo-o em segmentos menores de 24 MB.
    """
    print(f"Dividindo WAV diretamente: {wav_path}")
    return split_audio_into_segments(wav_path, output_folder, 24)

def process_audio(audio_path, output_dir):
    """
    Reduz ruído no áudio e salva em um diretório específico.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"Reduzindo ruído: {audio_path}")
    audio_data, sr = librosa.load(audio_path, sr=None)
    reduced_noise = nr.reduce_noise(y=audio_data, sr=sr)

    output_audio_path = os.path.join(output_dir, f"cleaned_{os.path.basename(audio_path)}")
    sf.write(output_audio_path, reduced_noise, sr)
    print(f"Áudio limpo salvo em: {output_audio_path}")
    return output_audio_path

def transcribe_audio(audio_path):
    """
    Transcreve o áudio usando a API Whisper da OpenAI.
    """
    print(f"Transcrevendo: {audio_path}")
    try:
        with open(audio_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="pt"
            )
        return transcript.text
    except Exception as e:
        print(f"Erro ao transcrever áudio: {e}")
        return None

def split_text_by_length(text, max_char_length=8000):
    """
    Divide o texto em partes menores para garantir que cada parte não ultrapasse o limite da API.
    """
    print("Texto muito longo. Dividindo em partes...")
    parts = []
    while len(text) > max_char_length:
        split_index = text[:max_char_length].rfind('.')  # Encontrar o último ponto para dividir de forma natural
        if split_index == -1:
            split_index = max_char_length  # Divisão forçada se não encontrar ponto
        parts.append(text[:split_index + 1])
        text = text[split_index + 1:].strip()
    parts.append(text)
    print(f"Texto dividido em {len(parts)} partes.")
    return parts

def summarize_text_as_minutes(text, part_number=1):
    """
    Gera uma ata de reunião no formato especificado usando GPT-4.
    """
    prompt = f"""
    Você é um assistente especializado em gerar atas de reuniões. A partir da transcrição a seguir, gere uma ata no formato:

    1. Principais Tópicos: Liste os principais assuntos discutidos.
    2. Ações e Responsáveis: Identifique ações importantes e quem são os responsáveis.
    3. Métricas e Decisões: Liste números, decisões e acordos feitos.

    A ata deve estar na norma culta da língua portuguesa e devidamente bem detalhada.

    Transcrição (Parte {part_number}):
    {text}
    """

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Você é um assistente especialista em atas de reuniões."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.5
    )
    return response.choices[0].message.content

def read_meeting_parts_from_directory(directory, file_pattern="*.txt"):
    """
    Lê automaticamente todos os arquivos de texto de um diretório e retorna o conteúdo como uma lista.
    """
    file_paths = glob.glob(os.path.join(directory, file_pattern))
    meeting_parts = []

    print(f"Encontrados {len(file_paths)} arquivos no diretório '{directory}'.")

    for file_path in sorted(file_paths):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            meeting_parts.append(content)
        print(f"Arquivo '{file_path}' lido com sucesso.")

    return meeting_parts

def combine_meeting_parts(meeting_parts):
    """
    Une todas as partes da ata em uma ata final coesa.
    """
    combined_text = "\n".join(meeting_parts)
    print("Todas as partes foram combinadas em uma única ata.")
    return combined_text

def generate_full_summary(meeting_parts):
    """
    Gera um resumo extenso e detalhado de todas as atas em um único parágrafo.
    """
    prompt = f"""
    Abaixo estão várias atas de uma reunião. Gere um resumo total, extenso e detalhado, contendo o máximo de informações possíveis,
    porém em um único parágrafo. O objetivo é criar um texto longo que resuma com precisão tudo que foi discutido.

    Atas:
    {meeting_parts}

    Resumo Extenso e Detalhado:
    """
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Você é um assistente especialista em criar resumos extensos e detalhados de atas."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.5
    )
    return response.choices[0].message.content

def generate_aggregated_minutes(meeting_parts):
    """
    Agrega todas as atas em uma só ata com um formato estruturado.
    """
    prompt = f"""
    Abaixo estão várias atas de uma reunião. Agrege todas em uma única ata, escolhendo as principais informações de cada uma.
    Use a norma culta da língua portuguesa e siga o formato abaixo:

    1. Principais Tópicos: Liste os principais assuntos discutidos.
    2. Ações e Responsáveis: Identifique ações importantes e quem são os responsáveis.
    3. Métricas e Decisões: Liste números, decisões e acordos feitos.

    Atas:
    {meeting_parts}

    Ata Consolidada:
    """
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Você é um assistente especialista em criar atas consolidadas e detalhadas."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.5
    )
    return response.choices[0].message.content