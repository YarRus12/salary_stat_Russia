import streamlit as st
import altair as alt
from prepare_data import main, extra_metrics, previous_year_inflation, real_salary, real_salary_delta
import numpy as np

CHOSEN_ACTIVITY = ['добыча полезных ископаемых', 'обрабатывающие производства', 'строительство',
                   'деятельность гостиниц и предприятий общественного питания', 'образование',
                   'деятельность в области здравоохранения и социальных услуг']
EXTRA_METRICS = ['ВВП', 'ВВП на душу населения']


@st.cache_data(ttl=60 * 60 * 24)
def create_schedule_main(dataframe) -> None:
    """
    Публикует графики с заработной платой отрасли и накладывает на графики линии роста реальной ЗП и инфляции

    :param dataframe: Объединенный dataframe со всеми данными
    :return:
    """
    bar_chart = alt.Chart(dataframe).mark_bar().encode(
        x=alt.X('year:O', axis=alt.Axis(format='')),
        y=real_salary,
        color='Вид деятельности'
    ).properties(
        width=1000,
        height=400
    )

    # Создание линии инфляции на уровне инфляции предшествующего года
    inflation_chart = alt.Chart(dataframe).mark_line(color='red').encode(
        y=alt.Y(previous_year_inflation, axis=alt.Axis(titleColor='white', labelColor='red')),
        # Настройка цвета текста по оси Y
        x=alt.X('year:O', axis=alt.Axis(format='')),
        size=alt.value(5)  # Настройка цвета текста по оси X
    ).properties(
        width=1000,
        height=400,
    )

    # Создание линии изменения реальной заработной платы (%) в сравнении с предыдущим периодом
    line_delta_salary = alt.Chart(dataframe).mark_line(color='green').encode(
        y=alt.Y(real_salary_delta, axis=alt.Axis(titleColor='white', labelColor='green')),
        x=alt.Y('year:O', axis=alt.Axis(titleColor='white')),
        size=alt.value(5)
    ).properties(
        width=1000,
        height=400
    )

    # Объединяем линию инфляции и линию % изменний заработной платы
    inflation_delta_salary_line = alt.layer(inflation_chart, line_delta_salary)

    # Соединяем линии с барелями заработной платы без привязки - так нагляднее представлена тенденция
    combined_chart = alt.layer(bar_chart, inflation_delta_salary_line).resolve_scale(y='independent')
    st.altair_chart(combined_chart, use_container_width=True)


def create_schedule_vvp(df_general, df_vvp, extra_column):
    merged = df_general.merge(df_vvp, on='year')

    bar_chart = alt.Chart(merged).mark_bar().encode(
        x=alt.X('year:O', axis=alt.Axis(title='Год', labelAngle=0, tickMinStep=1)),  # Ось x - годы
        y=alt.Y(f'{extra_column}:Q', axis=alt.Axis(title=extra_column, tickMinStep=5))  # Ось y - ВВП в трлн руб.
    ).properties(
        width=1000,  # Ширина графика
        height=400  # Высота графика
    )

    # Создание линии % изменения реальной заработной платы в сравнении с предыдущим периодом
    line_delta_salary = alt.Chart(df_general).mark_line(color='green').encode(
        y=alt.Y(real_salary_delta, axis=alt.Axis(titleColor='white', labelColor='green')),
        x=alt.Y('year:O', axis=alt.Axis(titleColor='white')),
        size=alt.value(5)
    ).properties(
        width=1000,
        height=400
    )
    combined_chart = alt.layer(bar_chart, line_delta_salary)
    st.altair_chart(combined_chart, use_container_width=True)


def corr_coefficient_extra(df_general, df_vvp, extra_column, general_column='изменением реальной заработной платы'):
    filled_length = len(df_general.merge(df_vvp, on='year')) - 2
    delta_salary_list = df_general[real_salary_delta].tolist()[
                        -filled_length:]  # Первое число всегда nan - его мы удаляем
    extra_column_list = df_vvp[extra_column].tolist()[
                        -filled_length:]  # не длиннее delta зп

    st.info(f"Коэффициент корреляции Пирсона между {extra_column} и {general_column} "
            f"в сфере - {activity.capitalize()}: "
            f"{str(np.corrcoef(extra_column_list, delta_salary_list)[0, 1])}")


def corr_coefficient_main(dataframe):
    delta_salary_list = dataframe[real_salary_delta].tolist()[1:]  # Первое число всегда nan - его мы удаляем
    inflation_last_year_list = dataframe[previous_year_inflation].tolist()[
                               :len(delta_salary_list)]  # не длиннее delta зп
    st.write("")

    st.info(f"Коэффициент корреляции Пирсона между инфляцией прошлого года и изменением реальной заработной платы "
            f"в сфере - {activity.capitalize()}: "
            f"{str(np.corrcoef(inflation_last_year_list, delta_salary_list)[0, 1])}")


if __name__ == '__main__':
    st.set_page_config(layout="centered", page_icon="💬", page_title="Анализ номинальных заработных плат в России")

    st.title('Анализ зарплат в России')

    # Load data
    res = main(chosen_activity=CHOSEN_ACTIVITY)
    res.year = res.year.astype('int')
    min_value = res['year'].min()
    max_value = res['year'].max()
    activity = res['Вид деятельности'].unique()

    st.write("")

    selected_activity = st.multiselect(
        'Какие виды экономической деятельности Вас интересуют?',
        options=activity, default=CHOSEN_ACTIVITY
    )
    st.write("")
    from_year, to_year = st.slider(
        'Какой промежуток времени Вас интересует?',
        min_value=min_value,
        max_value=max_value,
        value=[min_value, max_value])
    st.write("")

    selected_extra = st.multiselect(
        'Посмотрим дополнительные макроэкономические показатели для выбранных отраслей?',
        EXTRA_METRICS, EXTRA_METRICS)

    filtered_df = res[
        (res['Вид деятельности'].isin(selected_activity))
        & (res['year'] <= to_year)
        & (from_year <= res['year'])
        ]

    st.write("")
    st.write("")

    for activity in selected_activity:

        st.title(activity.capitalize())
        # Создаем график для каждой сферы
        df = filtered_df[filtered_df['Вид деятельности'] == activity]

        # Расчет коэффициента корреляции для каждой сферы
        corr_coefficient_main(dataframe=df)
        st.write("")

        create_schedule_main(dataframe=df)
        st.write("")
        st.write("")

        df_dict = extra_metrics(selected_extra)
        if 'ВВП' in selected_extra:
            vvp_dt = df_dict['ВВП']
            corr_coefficient_extra(df_general=df, df_vvp=vvp_dt['dataframe'], extra_column=vvp_dt['column'])
            create_schedule_vvp(df_general=df, df_vvp=vvp_dt['dataframe'], extra_column=vvp_dt['column'])

        if 'ВВП на душу населения' in selected_extra:
            vvp_dt_per = df_dict['ВВП на душу населения']
            corr_coefficient_extra(df_general=df, df_vvp=vvp_dt_per['dataframe'], extra_column=vvp_dt_per['column'])
            create_schedule_vvp(df_general=df, df_vvp=vvp_dt_per['dataframe'], extra_column=vvp_dt_per['column'])

    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.write("")

    st.sidebar.title("Этот sidebar немного расскажет о результатах реализации проекта :thought_balloon:")

    st.sidebar.markdown(
        """
        ![Altair Logo](https://i.pinimg.com/originals/3e/69/33/3e6933f1430c178465f64df11671c0e9.jpg)
        """
    )
    st.sidebar.info(

        """
         Основные выводы исследования: 
         - Все виды экономической деятельности имеют высокий уровень зависимости между ростом заработной платы и уровнем инфляции в прошлом году
         - Изменение ВВП и ВВП на душу население для отрасли Строительства имеет высокую зависимость с изменением уровня заработной платы
         - Изменение ВВП и ВВП на душу население для отрасли Образования имеет низкую зависимость с изменением уровня заработной платы
         - При работе со статистической информацией в указанной сфере следует учитывать как макроэкономические обстоятельства (2008-2008), так и неконтролируемые изменения выборки при смене методологии (2017)
         
         ПЫСЫ: Вроде получилось неплохо, техническая часть проекта понравилась больше, чем исследовательская
         
        """
    )
