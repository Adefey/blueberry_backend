# Blueberry Backend

## О приложении

Blueberry - приложение для готовки, это автоматическая книга рецептов, которая сама говорит тебе как готовить. На бекенде хранятся рецепты в MongoDB, FastAPI приложение предоставляет API ручки для взаимодействия с базой данных. Управление деплоем и окружением - Docker-Compose


## Сборка и запуск

Создайте текстовый файл конфига `env_config.txt`, шаблон файла:

```
SERVER_PORT=

MYSQL_PASSWORD=
MYSQL_ROOT_PASSWORD=
MYSQL_DATABASE=
MYSQL_USER=
```

Чтобы собрать и запустить бекенд с базой данных, напишите:

```
sudo docker compose up -d --build
```