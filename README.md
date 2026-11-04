## Цель сервиса
Интеграционный сервисы который получает результаты звонков из очереди RabbitMQ, 
сохраняет их в MongoDB и отдает данные через REST API.

## Запуск

Для локального запуска нужны Docker Compose и Python 3.11+. В контейнере используется Python 3.12.

Для локальной сборки и запуска сервиса:
```bash
cp .env.example .env
docker compose up --build
```

Для запуска в демон режиме:
```bash
docker compose up --build -d
```

.env файл содержит пути, логин и пароли до внешних сервисов (mongo and rabbitmq).
При необходимости можно заменить.

Для запуска producer создадим отдельную виртуальную среду и будем запускать его там:
```bash
python3.12 -m venv .dev-3.12
source .dev-3.12/bin/activate
pip install -r requirements_producer.txt
python src/producer.py
```

producer.py создаст две компании camp_001 и camp_002.
Чтобы проверить что он создал можно воспользовальзоваться такой командой

```bash
curl http://localhost:8000/campaigns/camp_001/calls | jq .
```
