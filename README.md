# Salary statistic in Russia

### Описание
- Репозиторий для проекта Start в DS


### Структура репозитория
* JupyterNotebook.ipynb - ноутбук с результатами исследования
* streamlit_app.py - основное приложение, в которым выполняется вызов вспомогательных модулей, расчет корреляции и визуализация
* prepare_data.py - вспомогательынй модуль подготовки данных
* requirements.txt
* .gitignore
* LICENSE


### Источники данных
    
#### Данные о номинальной заработной плате
*Описание*: 
Датасет разделен на 2 листа
На листе "2000-2016 гг." содержатся данные о номинальной заработной плате по ранее действовавшим кодам экономической деятельности, данные представлены по годам и сгруппированы в укрупненные сферы экономической деятельности
На листе "с 2017 г." содержатся данные о номинальной заработной плате по действующим кодам экономической деятельности, данные представлены по годам и сгруппированы в укрупненные сферы экономической деятельности  
состав групп до и после 2017 года может очень существенно отличасться  

*Источник данных* - сайт Федеральной службы государственной статистики  
*Cсылка на датасет* -  https://rosstat.gov.ru/storage/mediabank/tab3-zpl_2023.xlsx  
    
#### Данные об инфляции
*Описание основного источника*:  
Сведения об инфляции представлены таблицей с разбиением по месяцам, и накопительным итогом, столбец всего и декабрь совпадают  
*Источник данных* - сайт "Уровень инфляции.рф" Вкладка - таблицы  

*Описание альтернативного источника*:  
Сведения об индексе потребительских цен сформированы точно так же как и сведения об инфляции (значения не тождественны)  
*Источник данных* - сайт Федеральной службы государственной статистики, раздел индекс потребительских цен  
*Cсылка на датасет* - https://rosstat.gov.ru/storage/mediabank/ipc_mes_02-2024.xlsx  

#### Данные о ВВП и ВВП на душу населения
*Источник данных* - сайт Федеральной службы государственной статистики  
*Cсылка на датасет ВВП* -  https://rosstat.gov.ru/storage/mediabank/VVP_god_s_1995.xlsx  
*Cсылка на датасет ВВП на душу населения* - https://rosstat.gov.ru/storage/mediabank/VVP_na_dushu_s_1995.xlsx  


### Ссылки на удаленные сервера
* Streamlit - https://salarystatrussia-l3983pd7comd795n6zumvd.streamlit.app

### Критерии оценки

Вроде все выполнено, но это мое мнение

* [V] Cоздан публичный репозиторий на GitHub в котором присутствует лицензия, .gitignore и README.md (1 балл)
* [V] В README.md есть описание датасета и ссылка на источник откуда он взят (1 балл)
* [V] В репозитории присутствует Jupyter Notebook с анализом данных (1 балл)
* [V] В ноутбуке построены графики изменения зарплаты по годам для двух и более видов экономической деятельности. Сделаны выводы (5 баллов)
* [V] Пересчитаны средние зарплаты с учетом уровня инфляции и проведено сравнение, как влияет инфляция на изменение зарплаты по сравнению с предыдущим годом (5 баллов)
* [V] Присутствует визуализация и отображена динамика изменения реальных зарплат с учетом инфляции. Сделаны выводы  (5 баллов)
* [V] В репозитории присутствует скрипт(ы), реализующие логику веб-сервиса (2 балла)
* [V] По ссылке на веб-сервис открывается рабочее приложение (2 балла)

* [V] ОПЦИОНАЛЬНО: Данные размещены на удаленном сервере (3 балла)
* [V] В приложении реализована загрузка и отображение данных (3 балла)
* [V] В приложении присутствуют графики изменения зарплаты по годам для двух и более видов экономической деятельности (5 баллов)
* [V] В приложении отображаются средние зарплаты с учетом уровня инфляции и проведено сравнение как влияет инфляция на изменение зарплаты по сравнению с предыдущим годом (5 баллов)
* [V] В приложении присутствует визуализация и отображена динамика изменения реальных зарплат с учетом инфляции (5 баллов)


