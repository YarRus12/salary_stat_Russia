import streamlit as st
import altair as alt
from prepare_data import main

CHOSEN_ACTIVITY = ['добыча полезных ископаемых', 'обрабатывающие производства', 'строительство']


@st.cache_data(ttl=60 * 60 * 24)
def create_schedule(df, action):
    df = df[filtered_df['Вид деятельности'] == action]

    bar_chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('year:O', axis=alt.Axis(format='')),
        y='Средняя заработная плата',
        color='Вид деятельности'
    ).properties(
        width=1000,
        height=400
    )

    # Создание линии инфляции на уровне инфляции в прошлом году
    inflation_chart = alt.Chart(df).mark_line(color='red').encode(
        y=alt.Y('Инфляция в прошлом году', axis=alt.Axis(titleColor='white', labelColor='red')),
        # Настройка цвета текста по оси Y
        x=alt.X('year:O', axis=alt.Axis(format='')),
        size=alt.value(5) # Настройка цвета текста по оси X
    ).properties(
        width=1000,
        height=400,
    )

    # Создание линии % изменения номинальной заработной платы в сравнении с предыдущим периодом
    line_delta_salary = alt.Chart(df).mark_line(color='green').encode(
        y=alt.Y('% Изменения зарплаты', axis=alt.Axis(titleColor='green', labelColor='green')),
        x=alt.Y('year:O', axis=alt.Axis(titleColor='white')),
        size=alt.value(5)
                ).properties(
        width=1000,
        height=400
    )

    # Объединяем линию инфляции и линию % изменний заработной платы
    inflation_delta_salary_line = alt.layer(inflation_chart, line_delta_salary)

    # Соединяем линии с барелями заработной платы
    combined_chart = alt.layer(bar_chart, inflation_delta_salary_line).resolve_scale(y='independent')
    st.altair_chart(combined_chart, use_container_width=True)


if __name__ == '__main__':
    st.set_page_config(layout="centered", page_icon="💬", page_title="Анализ номинальных заработных плат в России")
    st.title('Анализ зарплат в России')

    # Load data
    res = main(choosen_activity=CHOSEN_ACTIVITY)
    res.year = res.year.astype('int')
    min_value = res['year'].min()
    max_value = res['year'].max()
    activity = res['Вид деятельности'].unique()

    selected_activity = st.multiselect(
        'Выберите интересующий вас вид экономической деятельности',
        activity, CHOSEN_ACTIVITY)

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

    st.write("")
    st.write("")
    st.write("")

    for activity in selected_activity:
        create_schedule(df=filtered_df, action=activity)
