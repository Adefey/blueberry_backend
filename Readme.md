# Blueberry Backend

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
sudo docker compose up -d -build
```