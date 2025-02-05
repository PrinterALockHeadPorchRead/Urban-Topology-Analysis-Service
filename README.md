# Сервис по анализу городской топологии

## Обзор

Сервис позволяет работать с картами формата open street map. Можно использовать как свои карты, так и подгружать нужные с помощью python скрипта.

Далее сервис позволяет в выбранном городе исследовать существующие районы или произвольную область, которую можно выделить с помощью полигонов.

По выбранному городу, району или полигональной области можно построить граф дорожно-транспортной сети и его топологическое разложение, посчитать некоторые метрики. Затем можно загрузить граф в виде таблицы или изображения.  

[Документация на гугл диске](https://docs.google.com/document/d/1tfpvU7qveO0ENqOvozmdVhncU48zHyhg/edit?usp=share_link&ouid=109435802449316353222&rtpof=true&sd=true)

## Предварительные действия

- Поместить PBF файлы исследуемых городов в директорию `/api/cities_osm/`. 
- Название файлов должны иметь вид: `{Название города с большой буквы}.osm.pbf`. Пример: `Москва.osm.pbf`.
- Для скачивания готовых фалов можно воспользоваться https://extract.bbbike.org/.

## Запуск
 
Для запуска серверной части приложения необходимо выполнить из основной директории проекта команду:

    docker compose up --build
    
## Примечания
 
После выполнения команды, по окончании сборки контейнера, доступ к сайту и серверу базы данных можно получить по следующим ссылкам:
- Сайт: http://localhost:4200/
- Сервер базы данных: http://localhost:8002/docs/

## Выключение сервера

Для того, чтобы корректно завершить работу сервера в консоле выполните команду:
    
     docker compose down

## Тут представлены ссылки на файлы с документацией по конкретным частям проекта:

1) [Бекенд и серверная часть](api/backend.md)
2) [Фронтенд](ui/front_docs.md)
3) [Аналитика](https://docs.google.com/document/d/13tFoxjkt9tnyzSbRs8adxpwf3rUp_CEGhsHXNY_ei8A/edit?usp=share_link)
