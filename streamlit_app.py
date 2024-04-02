import subprocess
import requests
import pandas as pd
import os
import streamlit as st
import streamlit as st
import numpy as np
import pandas as pd
import altair as alt

choosen_activity = ['добыча полезных ископаемых', 'обрабатывающие производства', 'строительство']


def pygraph(df):
    import pandas as pd
    import matplotlib.pyplot as plt

    # Создание графика
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()

    # Барельеф с заработной платой
    df.plot(x='Вид деятельности', y='Средняя заработная плата', kind='bar', ax=ax1, color='blue')

    # Линия с инфляцией
    df.plot(x='Вид деятельности', y='inflation_rate_previous_year', kind='line', marker='o', ax=ax2,
                     color='red')

    # Настройка графика
    ax1.set_ylabel('Средняя заработная плата', color='blue')
    ax2.set_ylabel('Инфляция', color='red')
    plt.title('Заработная плата и инфляция по виду деятельности')
    plt.xticks(rotation=45)

    # Отображение графика в Streamlit
    st.pyplot(fig)


@st.cache_data
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

    # Дополняем словарь с названием колонок через увеличение года на индекс колонки
    [rename_dict.update({df_2017.columns[x]: f"{2016 + x}"}) for x in range(1, len(df_2017.columns))]
    df_2017.rename(columns=rename_dict, inplace=True)
    # Колонка "вид деятельности" очищается от регистрозависимости и пробелов
    df_2017['Вид деятельности'] = df_2017['Вид деятельности'].str.lower().str.strip()
    return (pd.merge(df_2016[df_2016['Вид деятельности'].str.lower().str.strip().isin(choosen_activity)],
                     df_2017[df_2017['Вид деятельности'].str.lower().str.strip().isin(choosen_activity)],
                     on='Вид деятельности')
            .melt(id_vars='Вид деятельности', var_name='year', value_name='Средняя заработная плата')
            )

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
    year_inf = [{'year': record['month'][:4], 'inflation_rate': record['rate']} for record in inflation_list if
                record['month'][5:7] == '12']
    inflation = pd.DataFrame(year_inf, columns=['year', 'inflation_rate'])
    inflation['inflation_rate_previous_year'] = inflation['inflation_rate'].shift(1)
    return inflation

@st.cache_data
def main():
    # удалим старый файл с данными
    [os.remove(x) for x in os.listdir() if x.endswith('.xlsx')]
    # скачиваем xlsx файл с данными
    stat_url = 'https://rosstat.gov.ru/storage/mediabank/tab3-zpl_2023.xlsx'
    wget_command = ['wget', '--limit-rate=100k', stat_url]
    subprocess.run(wget_command)
    # готовим данные
    economy_df = economy_actvity_data()
    inflation_df = infliation_data()
    result = economy_df.merge(inflation_df, on='year')
    return result[['year', 'Вид деятельности', 'Средняя заработная плата', 'inflation_rate_previous_year']]

@st.cache_data(ttl=60 * 60 * 24)
def get_chart(data):
    hover = alt.selection_single(
        fields=["date"],
        nearest=True,
        on="mouseover",
        empty="none",
    )

    lines = (
        alt.Chart(data, height=500, title="Средняя номинальная заработная плата в России")
        .mark_line()
        .encode(
            x=alt.X("date", title="Date"),
            y=alt.Y("price", title="Price"),
            color="symbol",
        )
    )
    # Draw points on the line, and highlight based on selection
    points = lines.transform_filter(hover).mark_circle(size=65)

    # Draw a rule at the location of the selection
    tooltips = (
        alt.Chart(data)
        .mark_rule()
        .encode(
            x="year",
            y="Средняя заработная плата",
            opacity=alt.condition(hover, alt.value(0.3), alt.value(0)),
            tooltip=[
                alt.Tooltip("year", title="year"),
                alt.Tooltip("ЗП", title="ЗП (РУБ)"),
            ],
        )
        .add_selection(hover)
    )

    return (lines + points + tooltips).interactive()


if __name__ == '__main__':
    st.set_page_config(layout="centered", page_icon="💬", page_title="Анализ номинальных заработных плат в России")
    st.title('Анализ зарплат в России')

    # Load data
    res = main()
    res.year = res.year.astype('int')
    min_value = res['year'].min()
    max_value = res['year'].max()
    activity = res['Вид деятельности'].unique()

    # static table
    #st.table(res)

    selected_activity = st.multiselect(
        'Выберите интересующий вас вид экономической деятельности',
        activity, choosen_activity)

    from_year, to_year = st.slider(
        'Which years are you interested in?',
        min_value=min_value,
        max_value=max_value,
        value=[min_value, max_value])

    filtered_df = res[
        (res['Вид деятельности'].isin(selected_activity))
        & (res['year'] <= to_year)
        & (from_year <= res['year'])
        ]
    #st.table(filtered_df)

    st.write("")
    st.write("")
    st.write("")

    pygraph(filtered_df)


    #st.line_chart(new_df.set_index('year'), use_container_width=True).write('График продаж по годам')

    # Create a chart with annotations
    #annotations_df = pd.DataFrame(ANNOTATIONS, columns=["date", "event"])
    #annotations_df.date = pd.to_datetime(annotations_df.date)
    #annotations_df["y"] = 0
    #annotation_layer = (
    #     alt.Chart(annotations_df)
    #     .mark_text(size=15, text=ticker, dx=ticker_dx, dy=ticker_dy, align="center")
    #     .encode(
    #         x="date:T",
    #         y=alt.Y("y:Q"),
    #         tooltip=["event"],
    #     )
    #     .interactive()
    # )
    #
    # # Display both charts together
    # st.altair_chart((chart + annotation_layer).interactive(), use_container_width=True)
