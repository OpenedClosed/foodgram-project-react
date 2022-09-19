## Проект FOODGRAM
* * *
## Установка
- Настройте приложение для работы с базой данных (файл .env):
`DB_ENGINE=указываем, что работаем с конкретной базой данных`
`DB_NAME=имя базы данных`
`POSTGRES_USER=логин для подключения к базе данных`
`POSTGRES_PASSWORD=пароль для подключения к БД (установите свой)`
`DB_HOST=название сервиса (контейнера)`
`DB_PORT=порт для подключения к БД`
`DOCKER_PASSWORD=пароль DockerHub`
`DOCKER_USERNAME=имя пользователя DockerHub`
`USER=username для подключения к серверу`
`HOST=IP сервера`
`PASSPHRASE=пароль для сервера, если он установлен`
`SSH_KEY=ваш SSH ключ (для получения команда: cat ~/.ssh/id_rsa)`
`TELEGRAM_TO=ID своего телеграм-аккаунта`
`TELEGRAM_TOKEN=токен вашего бота`
* * *
## Вход в админ-зону
- Логин: admin
- Пароль: admin
* * *
## Запросы к API
Чтобы познакомиться с функционалом API составляющей сайта просмотрите документацию:
- http://130.193.55.211/api/docs/
* * *
## Описание Workflow (при push проекта на GitHub)
Workflow состоит из четырёх шагов:
- Проверка кода на соответствие PEP8.
- Сборка и публикация образа на DockerHub.
- Автоматический деплой на боевой сервер при пуше в главную ветку.
- Отправка уведомления в телеграм-чат.
* * *
## Технологии
- Django
- Python
- Docker
- React
* * *
## Информация об авторе проекта 
- Ник: openclose
- Электронная почта: opendoor200179@gmail.com
- Ссылка на проект: http://130.193.55.211/

[![foodgram_workflow](https://github.com/OpenedClosed/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)]