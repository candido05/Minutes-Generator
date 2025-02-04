import streamlit as st
import os
from model_functions import (criar_pastas, extract_and_split_audio_from_video, 
                       process_audio_mp3, process_audio_wav, process_audio,
                       transcribe_audio, split_text_by_length, summarize_text_as_minutes, 
                       read_meeting_parts_from_directory, combine_meeting_parts,
                       generate_full_summary, generate_aggregated_minutes)

from pdf_generator import gerar_pdf_resumo_ata
from folder_delete import  clean_folders_except_pdf

# Título da aplicação
st.title("Geração de Atas")

# Upload do arquivo
uploaded_file = st.file_uploader("Faça o upload do arquivo (MP4, MP3 ou WAV)", type=["mp4", "mp3", "wav"])

if uploaded_file is not None:
    # Cria as pastas necessárias
    criar_pastas()

    # Salva o arquivo carregado na pasta de upload
    file_path = os.path.join("arquivos_upload", uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success(f"Arquivo {uploaded_file.name} carregado com sucesso!")

    # Inicia o processamento automaticamente
    with st.spinner("Processando arquivo..."):
        try:
            # Determina o tipo de arquivo
            file_ext = uploaded_file.name.split('.')[-1].lower()
            if file_ext == "mp4":
                st.write("Processando arquivo de vídeo...")
                segments = extract_and_split_audio_from_video(file_path)
            elif file_ext == "mp3":
                st.write("Processando arquivo MP3...")
                output_dir = "audio_mp3_processado"
                cleaned_audio_path = process_audio_mp3(file_path, output_dir)
                segments = [cleaned_audio_path]  # Como é um arquivo único, não precisa dividir
            elif file_ext == "wav":
                st.write("Processando arquivo WAV...")
                output_folder = "segmentos_audio"
                segments = process_audio_wav(file_path, output_folder)
            else:
                st.error("Tipo de arquivo não suportado.")
                st.stop()

            st.write(f"Total de arquivos a serem processados: {len(segments)}")

            cleaned_audio_dir = "audio_limpo"  # Pasta onde os áudios limpos serão salvos
            if not os.path.exists(cleaned_audio_dir):
                os.makedirs(cleaned_audio_dir)

            full_transcription = ""
            for idx, segment_path in enumerate(segments):
                st.write(f"Processando segmento {idx+1}/{len(segments)}...")
                cleaned_audio_path = process_audio(segment_path, cleaned_audio_dir)
                transcription = transcribe_audio(cleaned_audio_path)
                full_transcription += transcription + "\n"

            with open(os.path.join("transcricoes", "full_transcription.txt"), "w", encoding="utf-8") as f:
                f.write(full_transcription)

            st.write("Transcrição concluída e salva em 'transcricoes/full_transcription.txt'.")

            atas_dir = "atas_parciais"
            if not os.path.exists(atas_dir):
                os.makedirs(atas_dir)

            # Verifica o tamanho da transcrição
            max_char_limit = 8000
            if len(full_transcription) > max_char_limit:
                transcription_parts = split_text_by_length(full_transcription, max_char_limit)
            else:
                transcription_parts = [full_transcription]

            final_summaries = []
            for i, part in enumerate(transcription_parts):
                st.write(f"Gerando a ata da Parte {i+1}/{len(transcription_parts)}...")
                summary = summarize_text_as_minutes(part, part_number=i+1)
                final_summaries.append(summary)
                st.write(f"Ata da Parte {i+1} concluída.\n")

            # Salvar as atas na pasta 'atas_parciais'
            for i, summary in enumerate(final_summaries):
                file_name = os.path.join(atas_dir, f"ata_parte_{i+1}.txt")
                with open(file_name, "w", encoding="utf-8") as f:
                    f.write(summary)
                st.write(f"Ata Parte {i+1} salva em '{file_name}'.")

            # Lê as atas do diretório
            meeting_parts = read_meeting_parts_from_directory(atas_dir)

            # Consolida a ata final
            final_ata = combine_meeting_parts(meeting_parts)
            full_summary = generate_full_summary("\n".join(meeting_parts))
            aggregated_minutes = generate_aggregated_minutes("\n".join(meeting_parts))

            # Gera o PDF
            gerar_pdf_resumo_ata(full_summary, aggregated_minutes, "resumo_e_ata.pdf")

            # Verifica se o PDF foi gerado
            pdf_path = os.path.join("pdf", "resumo_e_ata.pdf")
            if os.path.exists(pdf_path):
                st.success("Processamento concluído com sucesso!")

                # Disponibiliza o download do PDF
                with open(pdf_path, "rb") as f:
                    st.download_button(
                        label="Baixar PDF",
                        data=f,
                        file_name="resumo_e_ata.pdf",
                        mime="application/pdf"
                    )

                # Limpa as pastas, exceto a pasta 'pdf'
                clean_folders_except_pdf()
            else:
                st.error("Ocorreu um erro ao gerar o PDF.")
        except Exception as e:
            st.error(f"Ocorreu um erro durante o processamento: {e}")