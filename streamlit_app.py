import streamlit as st
import altair as alt
from prepare_data import main
import numpy as np

CHOSEN_ACTIVITY = ['добыча полезных ископаемых', 'обрабатывающие производства', 'строительство',
                   'деятельность гостиниц и предприятий общественного питания', 'образование',
                   'деятельность в области здравоохранения и социальных услуг']


@st.cache_data(ttl=60 * 60 * 24)
def create_schedule(dataframe):

    bar_chart = alt.Chart(dataframe).mark_bar().encode(
        x=alt.X('year:O', axis=alt.Axis(format='')),
        y='Средняя заработная плата',
        color='Вид деятельности'
    ).properties(
        width=1000,
        height=400
    )

    # Создание линии инфляции на уровне инфляции в прошлом году
    inflation_chart = alt.Chart(dataframe).mark_line(color='red').encode(
        y=alt.Y('Инфляция в прошлом году', axis=alt.Axis(titleColor='white', labelColor='red')),
        # Настройка цвета текста по оси Y
        x=alt.X('year:O', axis=alt.Axis(format='')),
        size=alt.value(5)  # Настройка цвета текста по оси X
    ).properties(
        width=1000,
        height=400,
    )

    # Создание линии % изменения реальной заработной платы в сравнении с предыдущим периодом
    line_delta_salary = alt.Chart(dataframe).mark_line(color='green').encode(
        y=alt.Y('Изменения реальной заработной платы', axis=alt.Axis(titleColor='white', labelColor='green')),
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


def corr_coefficient(dataframe):
    delta_salary_list = dataframe['Изменения реальной заработной платы'].tolist()[1:]  # Первое число всегда nan - его мы удаляем
    inflation_last_year_list = dataframe['Инфляция в прошлом году'].tolist()[
                               :len(delta_salary_list)]  # не длиннее delta зп
    st.write("")

    st.info(f"Коэффициент корреляции Пирсона между инфляцией прошлого года и изменением заработной платы "
            f"в сфере - {activity.capitalize()}: "
            f"{str(np.corrcoef(inflation_last_year_list, delta_salary_list)[0, 1])}")
    # inflation_curr_year_list = dataframe['inflation_rate'].tolist()[:len(delta_salary_list)]  # не длиннее delta зп
    # st.info(f"Коэффициент корреляции Пирсона между инфляцией текущего года и изменением заработной платы: "
    #         f"{str(np.corrcoef(inflation_curr_year_list, delta_salary_list)[0, 1])}")


if __name__ == '__main__':
    st.set_page_config(layout="centered", page_icon="💬", page_title="Анализ номинальных заработных плат в России")

    st.title('Анализ зарплат в России')

    # Load data
    res = main(choosen_activity=CHOSEN_ACTIVITY)
    res.year = res.year.astype('int')
    min_value = res['year'].min()
    max_value = res['year'].max()
    activity = res['Вид деятельности'].unique()

    st.write("")

    selected_activity = st.multiselect(
        'Какие виды экономической деятельности Вас интересуют?',
        activity, CHOSEN_ACTIVITY)
    st.write("")
    from_year, to_year = st.slider(
        'Какой промежуток времени Вас интересует?',
        min_value=min_value,
        max_value=max_value,
        value=[min_value, max_value])
    st.write("")
    filtered_df = res[
        (res['Вид деятельности'].isin(selected_activity))
        & (res['year'] <= to_year)
        & (from_year <= res['year'])
        ]

    st.write("")
    st.write("")

    for activity in selected_activity:
        # Создаем график для каждой сферы
        df = filtered_df[filtered_df['Вид деятельности'] == activity]
        corr_coefficient(dataframe=df)
        st.write("")
        create_schedule(dataframe=df)
        # Расчет коэффициента корреляции для каждой сферы

        st.write("")
        st.write("")
        st.write("")

    st.sidebar.title("About")
    st.sidebar.info(
        """
        This app is Open Source dashboard.
        """
    )
