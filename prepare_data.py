import subprocess
import requests
import pandas as pd
import os


def economy_actvity_data():
    df_2016 = pd.read_excel("tab3-zpl_2023.xlsx", sheet_name='2000-2016 гг.', index_col=None)[
              2:]  # первые строки не несут информации для нас
    column_list = ['Вид деятельности', '2000', '2001', '2002', '2003', '2004', '2005', '2006', '2007', '2008', '2009',
                   '2010', '2011', '2012', '2013', '2014', '2015', '2016']
    rename_dict = {df_2016.columns[column_index]: column_list[column_index] for column_index in
                   range(len(df_2016.columns))}
    df_2016.rename(columns=rename_dict, inplace=True)
    # Колонка вид деятельности очищается от регистрозависимости и пробелов
    df_2016['Вид деятельности'] = df_2016['Вид деятельности'].str.lower().str.strip()
    # Подготовка датафрейма с новым данными
    df_2017 = pd.read_excel("tab3-zpl_2023.xlsx", sheet_name='с 2017 г.')[4:]
    rename_dict = {'Unnamed: 0': 'Вид деятельности'}
    # длина выгрузки может меняться в будущем, такой способ более универсален
    years = (2017, 2017 + len(df_2017.columns) - 2)
    # Дополняем словарь с названием колонок через увеличение года на индекс колонки
    [rename_dict.update({df_2017.columns[x]: f"{2016 + x}"}) for x in range(1, len(df_2017.columns))]
    df_2017.rename(columns=rename_dict, inplace=True)
    # Колонка "вид деятельности" очищается от регистрозависимости и пробелов
    df_2017['Вид деятельности'] = df_2017['Вид деятельности'].str.lower().str.strip()
    choosen_activity = ['добыча полезных ископаемых', 'обрабатывающие производства', 'строительство']
    return (pd.merge(df_2016[df_2016['Вид деятельности'].str.lower().str.strip().isin(choosen_activity)],
                     df_2017[df_2017['Вид деятельности'].str.lower().str.strip().isin(choosen_activity)],
                     on='Вид деятельности')
            .melt(id_vars='Вид деятельности', var_name='year', value_name='Средняя заработная плата')
            )


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
    year_inf = [{'year': record['month'][:4], 'inflation_rate': record['rate']} for record in inflation_list if
                record['month'][5:7] == '12']
    inflation = pd.DataFrame(year_inf, columns=['year', 'inflation_rate'])
    inflation['inflation_rate_previous_year'] = inflation['inflation_rate'].shift(1)
    return inflation


if __name__ == '__main__':
    # удалим старый файл с данными
    [os.remove(x) for x in os.listdir() if x.endswith('.xlsx')]
    # скачиваем xlsx файл с данными
    stat_url = 'https://rosstat.gov.ru/storage/mediabank/tab3-zpl_2023.xlsx'
    wget_command = ['wget', '--limit-rate=100k', stat_url]
    subprocess.run(wget_command)
    # готовим данные
    economy_df = economy_actvity_data()
    inflation_df = infliation_data()
    res = economy_df.merge(inflation_df, on='year')
