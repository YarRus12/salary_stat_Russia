import subprocess
import requests
import os
import streamlit as st
import pandas as pd

attributes = {
    'nominal_salary': 'Средняя заработная плата',
    'current_inflation': 'inflation_rate',
    'previous_year_inflation': 'Инфляция прошлого года',
    'real_salary': 'Реальный размер заработной платы',
    'real_salary_delta': 'Изменение реальной ЗП'
}
nominal_salary, current_inflation = attributes['nominal_salary'], attributes['current_inflation']
previous_year_inflation, real_salary = attributes['previous_year_inflation'], attributes['real_salary']
real_salary_delta = attributes['real_salary_delta']


@st.cache_data
def economy_actvity_data(choosen_activity):
    df_2016 = pd.read_excel("tab3-zpl_2023.xlsx", sheet_name='2000-2016 гг.', index_col=None)[
              2:]  # первые строки не несут информации для нас
    column_list = ['Вид деятельности', '2000', '2001', '2002', '2003', '2004', '2005', '2006', '2007', '2008', '2009',
                   '2010', '2011', '2012', '2013', '2014', '2015', '2016']
    rename_dict = {df_2016.columns[column_index]: column_list[column_index] for column_index in
                   range(len(df_2016.columns))}
    df_2016.rename(columns=rename_dict, inplace=True)

    # Переименование старых колонок с похожими сферами деятельности
    if 'деятельность гостиниц и предприятий общественного питания' in choosen_activity:
        df_2016['Вид деятельности'] = df_2016['Вид деятельности']\
            .replace('Операции с недвижимым имуществом, аренда и предоставление услуг',
                     'деятельность гостиниц и предприятий общественного питания')
    if 'деятельность в области здравоохранения и социальных услуг' in choosen_activity:
        df_2016['Вид деятельности'] = df_2016['Вид деятельности'] \
            .replace('Здравоохранение и предоставление социальных услуг',
                     'деятельность в области здравоохранения и социальных услуг')

    # Колонка вид деятельности очищается от регистрозависимости и пробелов
    df_2016['Вид деятельности'] = df_2016['Вид деятельности'].str.lower().str.strip()
    # Подготовка датафрейма с новым данными
    df_2017 = pd.read_excel("tab3-zpl_2023.xlsx", sheet_name='с 2017 г.')[4:]
    rename_dict = {'Unnamed: 0': 'Вид деятельности'}

    # Дополняем словарь с названием колонок через увеличение года на индекс колонки
    [rename_dict.update({df_2017.columns[x]: f"{2016 + x}"}) for x in range(1, len(df_2017.columns))]
    df_2017.rename(columns=rename_dict, inplace=True)
    # Колонка "вид деятельности" очищается от регистрозависимости и пробелов
    df_2017['Вид деятельности'] = df_2017['Вид деятельности'].str.lower().str.strip()
    merged = (pd.merge(df_2016[df_2016['Вид деятельности'].str.lower().str.strip().isin(choosen_activity)],
                     df_2017[df_2017['Вид деятельности'].str.lower().str.strip().isin(choosen_activity)],
                     on='Вид деятельности')
            .melt(id_vars='Вид деятельности', var_name='year', value_name=nominal_salary)
            )
    return merged

@st.cache_data
def infliation_data():
    url = 'https://xn----ctbjnaatncev9av3a8f8b.xn--p1ai/%D1%82%D0%B0%D0%B1%D0%BB%D0%B8%D1%86%D1%8B-%D0%B8%D0%BD%D1%84%D0%BB%D1%8F%D1%86%D0%B8%D0%B8'
    r = requests.get(url)
    if r.status_code == 200:
        html_content = r.text
    else:
        print('No connection')
        raise
    inflation_start_line = html_content[html_content.find('yoyInflationList') + len('yoyInflationList":'):]
    inflation_line = inflation_start_line[:inflation_start_line.find(']') + 1].replace('new Date(', '').replace(')', '')
    inflation_list = (eval(inflation_line))
    year_inf = [{'year': record['month'][:4], current_inflation: record['rate']} for record in inflation_list if
                record['month'][5:7] == '12']
    inflation = pd.DataFrame(year_inf, columns=['year', current_inflation])
    inflation[previous_year_inflation] = inflation[current_inflation].shift(1)
    return inflation

@st.cache_data
def main(choosen_activity):
    # удалим старый файл с данными
    [os.remove(x) for x in os.listdir() if x.endswith('.xlsx')]
    # скачиваем xlsx файл с данными
    stat_url = 'https://rosstat.gov.ru/storage/mediabank/tab3-zpl_2023.xlsx'
    wget_command = ['wget', '--limit-rate=100k', stat_url]
    subprocess.run(wget_command)
    # готовим данные
    economy_df = economy_actvity_data(choosen_activity)
    inflation_df = infliation_data()
    result = economy_df.merge(inflation_df, on='year')
    result[real_salary] = result[nominal_salary] * (
                (100 - result[previous_year_inflation]) / 100)
    result[real_salary_delta] = result.groupby('Вид деятельности')[
                                                       real_salary].pct_change() * 100
    return result[['year', 'Вид деятельности', real_salary,
                   previous_year_inflation, current_inflation, real_salary_delta]]


