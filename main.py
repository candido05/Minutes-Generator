from model_functions import (upload_file, criar_pastas, extract_and_split_audio_from_video, 
                       process_audio_mp3, process_audio_wav, process_audio,
                       transcribe_audio, split_text_by_length, summarize_text_as_minutes, 
                       read_meeting_parts_from_directory, combine_meeting_parts,
                       generate_full_summary, generate_aggregated_minutes)

from pdf_generator import gerar_pdf_resumo_ata
from folder_delete import  clean_folders_except_pdf
import os

def main():
    # Cria as pastas necessárias
    criar_pastas()

    print("### Upload do arquivo ###")
    file_name, file_type = upload_file()

    if not file_name:
        print("Nenhum arquivo válido foi carregado.")
        return

    if file_type == "video":
        print("Processando arquivo de vídeo...")
        segments = extract_and_split_audio_from_video(file_name)
    elif file_type == "mp3":
        print("Processando arquivo MP3...")
        output_dir = "audio_mp3_processado"
        cleaned_audio_path = process_audio_mp3(file_name, output_dir)
        segments = [cleaned_audio_path]  # Como é um arquivo único, não precisa dividir
    elif file_type == "wav":
        print("Processando arquivo WAV...")
        output_folder = "segmentos_audio"
        segments = process_audio_wav(file_name, output_folder)

    print(f"Total de arquivos a serem processados: {len(segments)}")

    cleaned_audio_dir = "audio_limpo"  # Pasta onde os áudios limpos serão salvos
    if not os.path.exists(cleaned_audio_dir):
        os.makedirs(cleaned_audio_dir)

    full_transcription = ""
    for idx, segment_path in enumerate(segments):
        print(f"Processando segmento {idx+1}/{len(segments)}...")
        cleaned_audio_path = process_audio(segment_path, cleaned_audio_dir)
        transcription = transcribe_audio(cleaned_audio_path)
        full_transcription += transcription + "\n"

    with open(os.path.join("transcricoes", "full_transcription.txt"), "w", encoding="utf-8") as f:
        f.write(full_transcription)

    print("Transcrição concluída e salva em 'transcricoes/full_transcription.txt'.")

    atas_dir = "atas_parciais"
    if not os.path.exists(atas_dir):
        os.makedirs(atas_dir)

    # Simulação de uma transcrição muito longa
    print("Verificando o tamanho da transcrição...")
    max_char_limit = 8000

    # Dividir a transcrição se necessário
    if len(full_transcription) > max_char_limit:
        transcription_parts = split_text_by_length(full_transcription, max_char_limit)
    else:
        transcription_parts = [full_transcription]

    final_summaries = []
    for i, part in enumerate(transcription_parts):
        print(f"Gerando a ata da Parte {i+1}/{len(transcription_parts)}...")
        summary = summarize_text_as_minutes(part, part_number=i+1)
        final_summaries.append(summary)
        print(f"Ata da Parte {i+1} concluída.\n")

    # Salvar as atas na pasta 'atas_parciais'
    for i, summary in enumerate(final_summaries):
        file_name = os.path.join(atas_dir, f"ata_parte_{i+1}.txt")
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(summary)
        print(f"Ata Parte {i+1} salva em '{file_name}'.")

    # Exibição das atas finais
    print("\n### Atas Finais da Reunião ###")
    for i, summary in enumerate(final_summaries):
        print(f"\n### Ata Parte {i+1} ###\n")
        print(summary)

    directory_path = "atas_parciais"

    print("Lendo arquivos do diretório...")
    meeting_parts = read_meeting_parts_from_directory(directory_path)

    print("Consolidando a ata final...")
    final_ata = combine_meeting_parts(meeting_parts)
    print("Gerando resumo extenso e detalhado...")
    full_summary = generate_full_summary("\n".join(meeting_parts))
    print("Gerando ata consolidada...")
    aggregated_minutes = generate_aggregated_minutes("\n".join(meeting_parts))

    with open(os.path.join("ata_final", "ata_final_completa.txt"), "w", encoding="utf-8") as f:
        f.write(final_ata)
    print("Ata final salva em 'ata_final/ata_final_completa.txt'.")

    with open(os.path.join("resumo_final", "resumo_extenso.txt"), "w", encoding="utf-8") as f:
        f.write(full_summary)
    print("Resumo extenso salvo em 'resumo_final/resumo_extenso.txt'.")

    with open(os.path.join("ata_final", "ata_consolidada.txt"), "w", encoding="utf-8") as f:
        f.write(aggregated_minutes)
    print("Ata consolidada salva em 'ata_final/ata_consolidada.txt'.")

    print("\n### Resumo Extenso e Detalhado ###\n")
    print(full_summary)

    print("\n### Ata Consolidada ###\n")
    print(aggregated_minutes)

    gerar_pdf_resumo_ata(full_summary, aggregated_minutes, "resumo_e_ata.pdf")

    clean_folders_except_pdf()
    
if __name__ == "__main__":
    main()