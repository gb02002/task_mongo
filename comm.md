So, that's the way of handling the request:

1. Verify request
2. dates, type = Get type
3. Forward request -> execute(dates, type)
4. procced with checking if no misses in db
5. formating for message, spliting if needed
6. send response

Main questions:

Как сделать заполнение пустых значений? 

1. Попытка поиска аналога not exists из postgres. Отсутствует  
2. Через создание нулёвой дублирующей таблицы и наложении значений при наличии? 
3. Учитывая базу и данные(их не так много), выбор пал на изменения на уровне приложения с готовым ответом


