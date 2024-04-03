import requests
import streamlit as st
import pandas as pd

attributes = {
    'nominal_salary': 'Средняя заработная плата',
    'current_inflation': 'Текущий уровень инфляции',
    'previous_year_inflation': 'Инфляция прошлого года',
    'real_salary': 'Реальный размер заработной платы',
    'real_salary_delta': 'Изменение реальной ЗП'
}
nominal_salary, current_inflation = attributes['nominal_salary'], attributes['current_inflation']
previous_year_inflation, real_salary = attributes['previous_year_inflation'], attributes['real_salary']
real_salary_delta = attributes['real_salary_delta']


def clean_numeric_column(value: str):
    """
    Небольшая функция для преобразования числовых значений с запятой в качестве разделителя в стандартный формат
    и для очистки числовых колонок датафреймов от лишних символов
    :param value:
    :return:
    """
    if ',' in value:
        value = value.replace(',', '.')
    value = ''.join(filter(lambda x: x in '1234567890.', value))
    return value


def main_inflation_data() -> pd.DataFrame:
    """
    функция получает данные из основного источника, и распарсевает их как текст
    и возвращает обработанный датафрейм
    :return: датафрейм с данным по инфляции
    """
    url = """https://xn----ctbjnaatncev9av3a8f8b.xn--p1ai/%D1%82%D0%B0%D0%B1%D0%BB%D0%B8%D1%86%D1%8B-%D0%B8%D0%BD%D1%84%D0%BB%D1%8F%D1%86%D0%B8%D0%B8"""
    r = requests.get(url)
    if r.status_code == 200:
        html_content = r.text
    else:
        print('No connection')
        raise
    # Обработка html до словаря
    inflation_start_line = html_content[html_content.find('yoyInflationList') + len('yoyInflationList":'):]
    inflation_line = inflation_start_line[:inflation_start_line.find(']') + 1].replace('new Date(', '').replace(')', '')
    inflation_list = (eval(inflation_line))

    year_inf = [{'year': record['month'][:4], current_inflation: record['rate']} for record in inflation_list if
                record['month'][5:7] == '12']
    return pd.DataFrame(year_inf, columns=['year', current_inflation])


def alternative_inflation_data() -> pd.DataFrame:
    """
    Альтернативная функция получения данных об инфляции,
    вычитываются сведения об изменении индекса потребительских цен, как самого крупного компонента инфляции
    работает в случае недоступности первого источника
    :return: датафрейм с данным по инфляции
    """
    df = pd.read_excel("https://rosstat.gov.ru/storage/mediabank/ipc_mes_02-2024.xlsx",
                       sheet_name='01', index_col=None)[
         2:18]

    new_df = pd.concat([df.iloc[[0]], df.iloc[[-1]]], ignore_index=True).T

    new_df.reset_index(drop=True, inplace=True)
    new_df.rename(columns={0: 'year', 1: current_inflation}, inplace=True)

    new_df = new_df.dropna(subset=['year'])
    new_df = new_df[['year', current_inflation]].astype(str)
    new_df['year'] = new_df['year'].str.slice(0, 4)
    new_df[current_inflation] = new_df[current_inflation].apply(clean_numeric_column).astype(float) - 100
    return new_df


@st.cache_data
def economy_activity_data(chosen_activity) -> pd.DataFrame:
    """
    Функция вычитывает данные Росстата о номинальной заработной плате и формирует исторический датафрейм
    :param chosen_activity: список видов эклономической деятельности, выбранных пользователем из доступных
    :return: Датафрейм с данными о номинальных заработных платах по видам экономической деятельнсоти
    """
    df_2016 = pd.read_excel("https://rosstat.gov.ru/storage/mediabank/tab3-zpl_2023.xlsx",
                            sheet_name='2000-2016 гг.', index_col=None)[
              2:]  # первые строки не несут информации для нас
    column_list = ['Вид деятельности', '2000', '2001', '2002', '2003', '2004', '2005', '2006', '2007', '2008', '2009',
                   '2010', '2011', '2012', '2013', '2014', '2015', '2016']
    rename_dict = {df_2016.columns[column_index]: column_list[column_index] for column_index in
                   range(len(df_2016.columns))}
    df_2016.rename(columns=rename_dict, inplace=True)

    # Переименование старых колонок с похожими сферами деятельности
    if 'деятельность гостиниц и предприятий общественного питания' in chosen_activity:
        df_2016['Вид деятельности'] = df_2016['Вид деятельности'] \
            .replace('Операции с недвижимым имуществом, аренда и предоставление услуг',
                     'деятельность гостиниц и предприятий общественного питания')
    if 'деятельность в области здравоохранения и социальных услуг' in chosen_activity:
        df_2016['Вид деятельности'] = df_2016['Вид деятельности'] \
            .replace('Здравоохранение и предоставление социальных услуг',
                     'деятельность в области здравоохранения и социальных услуг')

    # Колонка вид деятельности очищается от регистрозависимости и пробелов
    df_2016['Вид деятельности'] = df_2016['Вид деятельности'].str.lower().str.strip()
    # Подготовка датафрейма с новым данными
    df_2017 = pd.read_excel("https://rosstat.gov.ru/storage/mediabank/tab3-zpl_2023.xlsx", sheet_name='с 2017 г.')[4:]
    rename_dict = {'Unnamed: 0': 'Вид деятельности'}

    # Дополняем словарь с названием колонок через увеличение года на индекс колонки
    [rename_dict.update({df_2017.columns[x]: f"{2016 + x}"}) for x in range(1, len(df_2017.columns))]
    df_2017.rename(columns=rename_dict, inplace=True)
    # Колонка "вид деятельности" очищается от регистрозависимости и пробелов
    df_2017['Вид деятельности'] = df_2017['Вид деятельности'].str.lower().str.strip()
    # Объединяем df и преобразуем годы из столбцов в колонки для удобства соединения с инфляцией
    merged = (pd.merge(df_2016[df_2016['Вид деятельности'].str.lower().str.strip().isin(chosen_activity)],
                       df_2017[df_2017['Вид деятельности'].str.lower().str.strip().isin(chosen_activity)],
                       on='Вид деятельности')
              .melt(id_vars='Вид деятельности', var_name='year', value_name=nominal_salary)
              )
    return merged


@st.cache_data
def inflation_data() -> pd.DataFrame:
    """
    Функция получает данные об инфляции из основного или альтернативного источника,
    создает колонку с данными об инфляции за предыдущий период

    :return: Датафрейм с данными об инфляции
    """
    try:
        inflation = main_inflation_data()
    except Exception as e:
        inflation = alternative_inflation_data()
    inflation[previous_year_inflation] = inflation[current_inflation].shift(1)
    return inflation


@st.cache_data
def gross_domestic_product(file_name, result_column) -> pd.DataFrame:
    """
    Функция подготовливает данные о ВВП или данные о ВВП на чел - работает универсально

    :param result_column: Имя колонки в которую будут сохранены результаты подготовки данных
    :param file_name: Название файла на сайте Росстата с выбранным показателем
    :return:
    """
    url = f"https://rosstat.gov.ru/storage/mediabank/{file_name}"

    vvp_old = pd.read_excel(url,
                            sheet_name='1', index_col=None)[1:].T
    vvp_old.rename(columns={1: 'year', 2: 'ВВП в трлн руб.'}, inplace=True)
    vvp_old['year'] = vvp_old['year'].astype(int)
    vvp_old['ВВП в трлн руб.'] = vvp_old['ВВП в трлн руб.'].astype(float)
    vvp_old.reset_index(drop=True, inplace=True)

    vvp = pd.read_excel(url,
                        sheet_name='2', index_col=None)[2:4].T
    vvp.rename(columns={2: 'year', 3: 'ВВП в трлн руб.'}, inplace=True)
    if result_column == 'Изменение ВВП на чел %':
        vvp = pd.read_excel(url, sheet_name='2', index_col=None)[1:3].T
        vvp.rename(columns={1: 'year', 2: 'ВВП в трлн руб.'}, inplace=True)

    vvp = vvp[['year', 'ВВП в трлн руб.']].astype(str)
    vvp['year'] = vvp['year'].str.slice(0, 4)
    vvp['year'] = vvp['year'].astype(int)
    vvp['ВВП в трлн руб.'] = vvp['ВВП в трлн руб.'].astype(float)
    vvp.reset_index(drop=True, inplace=True)

    merged_df = pd.merge(vvp_old, vvp, on=['year', 'ВВП в трлн руб.'], how='outer') \
        .drop_duplicates(subset=['year'], keep='first')  # 2011 расчитывался по обеим методологиями, оставляю первый
    merged_df[result_column] = (merged_df['ВВП в трлн руб.'] - merged_df['ВВП в трлн руб.'].shift(1)) / merged_df[
        'ВВП в трлн руб.'] * 100
    return merged_df


@st.cache_data
def main(chosen_activity: list) -> pd.DataFrame:
    """
    Основная функция подготовки данных о заработной плате и инфляции

    :param chosen_activity: список видов эклономической деятельности, выбранных пользователем из доступных
    :return: pandas.DataFrame с данными о видах деятельности, номинальную и реальную заработную плату
    """

    # готовим данные
    economy_df = economy_activity_data(chosen_activity)
    inflation_df = inflation_data()
    result = economy_df.merge(inflation_df, on='year')

    # Расчитываем реальную заработную плату
    result[real_salary] = result[nominal_salary] * (
            (100 - result[previous_year_inflation]) / 100)
    # Расчитываем изменение реальной заработной платы во времени
    result[real_salary_delta] = result.groupby('Вид деятельности')[
                                    real_salary].pct_change() * 100
    return result[['year', 'Вид деятельности', real_salary,
                   previous_year_inflation, current_inflation, real_salary_delta]]


def extra_metrics(extra: list) -> dict:
    """
    Функция собирает дополнительные данные из выбранных пользователем показателей

    :param extra: список, выбранных пользователем показателей
    :return: словарь с датафреймом и результирующей колонкой
    """
    result_extra_dict = {}
    if 'ВВП' in extra:
        col = 'Изменение ВВП %'
        result_extra_dict['ВВП'] = {'dataframe': gross_domestic_product(
            file_name="VVP_god_s_1995.xlsx",
            result_column=col),
            'column': col
        }

    if 'ВВП на душу населения' in extra:
        col = 'Изменение ВВП на чел %'
        result_extra_dict['ВВП на душу населения'] = {'dataframe': gross_domestic_product(
            file_name="VVP_na_dushu_s_1995.xlsx",
            result_column=col),
            'column': col
        }
    return result_extra_dict
