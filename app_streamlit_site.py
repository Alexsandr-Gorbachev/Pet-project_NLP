import streamlit as st
import pandas as pd
import Levenshtein
from tqdm import tqdm
from collections import Counter
import time

def process_data(clean_df, dirty_df):
    # Определяем порог для схожести строк
    similarity_threshold = 1.0

    # Определяем порог для низкочастотных встречаний
    frequency_threshold = 2

    # Создаем новую колонку для хранения результатов замен
    dirty_df['Адрес_результат'] = ""

    # Инициализируем прогресс-бар
    progress_bar = st.progress(0)

    # Создаем счетчик частотности адресов
    address_counter = Counter(dirty_df['Адрес'])

    # Сравниваем каждую строку из dirty_df['Адрес'] со всеми строками из clean_df['Адрес']
    start_time = time.time()
    for i, address in enumerate(dirty_df['Адрес']):
        best_match = ""
        max_similarity = 0.0

        for phrase in clean_df['Адрес']:
            similarity_ratio = Levenshtein.ratio(address, phrase)

            if similarity_ratio > max_similarity:
                max_similarity = similarity_ratio
                best_match = phrase

            if max_similarity >= similarity_threshold:
                break

        # Проверяем частотность адреса и применяем порог
        address_frequency = address_counter[address]
        if address_frequency < frequency_threshold:
            best_match = ""

        dirty_df.at[i, 'Адрес_результат'] = best_match

        # Обновляем прогресс-бар с эффектом отсчета времени
        progress = (i + 1) / len(dirty_df)
        elapsed_time = time.time() - start_time
        estimated_time = elapsed_time / progress - elapsed_time
        progress_bar.progress(progress, f"Осталось: {estimated_time:.2f} сек")

    # Завершаем прогресс-бар
    progress_bar.empty()

    end_time = time.time()
    execution_time = round(end_time - start_time, 2)

    return dirty_df, execution_time

def main():
    st.title("Сравнение списков")

    # Создание виджетов для загрузки файлов
    clean_list_file = st.file_uploader("Загрузите чистый список", type=["csv", "xlsx"])
    dirty_list_file = st.file_uploader("Загрузите грязный список", type=["csv", "xlsx"])

    # Чтение данных из загруженных файлов
    if clean_list_file and dirty_list_file:
        clean_df = pd.read_csv(clean_list_file) if clean_list_file.name.endswith(".csv") else pd.read_excel(clean_list_file)
        dirty_df = pd.read_csv(dirty_list_file) if dirty_list_file.name.endswith(".csv") else pd.read_excel(dirty_list_file)

        # Обработка списков при нажатии кнопки
        if st.button("Сравнить"):
            dirty_df_result, execution_time = process_data(clean_df, dirty_df)

            st.write("Оригинальные значения (грязный список):")
            st.dataframe(dirty_df['Адрес'], width=800)

            st.write("Замененные значения (грязный список):")
            st.dataframe(dirty_df_result['Адрес_результат'], width=800)

            # Вычисляем точность замен
            total_replacements = len(dirty_df[dirty_df['Адрес'] != dirty_df_result['Адрес_результат']])
            accuracy = 1 - (total_replacements / len(dirty_df)) * 100
            st.write("Точность замен (грязный список):", accuracy)

            st.write("Время выполнения:", execution_time, "секунд")

if __name__ == "__main__":
    main()