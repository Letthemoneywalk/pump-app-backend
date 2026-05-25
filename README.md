# Pump App — Backend

Бэкенд для мобильного приложения поиска фитнес-тренеров. Механика похожа на приложения для знакомств — клиент свайпает тренеров, отправляет заявку, тренер принимает или отклоняет.

## Стек

- **Python 3.10**
- **FastAPI** — REST API + WebSocket
- **PostgreSQL** — база данных
- **SQLAlchemy** — ORM
- **Alembic** — миграции
- **JWT** — авторизация
- **Docker** — запуск PostgreSQL

## Структура проекта

```
pump_app/
├── app/                  # ядро приложения
│   ├── main.py           # точка входа
│   ├── config.py         # настройки (.env)
│   ├── database.py       # подключение к БД
│   ├── auth.py           # JWT, хэширование паролей
│   └── routers/          # эндпоинты
│       ├── auth.py       # регистрация, логин
│       ├── trainers.py   # профили тренеров, лента
│       ├── clients.py    # профили клиентов
│       ├── swipes.py     # заявки
│       ├── scheduling.py # календарь тренировок
│       └── chat.py       # чат + WebSocket
├── users/                # модель и схемы пользователей
├── trainers/             # модель и схемы тренеров
├── clients/              # модель и схемы клиентов
├── swipes/               # модель и схемы заявок
├── scheduling/           # модель и схемы тренировок
├── chat/                 # модель и схемы чата
├── alembic/              # миграции БД
├── .env                  # переменные окружения (не коммитить)
├── docker-compose.yml    # PostgreSQL
└── requirements.txt
```

## Установка и запуск

### 1. Клонировать репозиторий

```bash
git clone https://github.com/YOUR_USERNAME/pump_app.git
cd pump_app
```

### 2. Создать виртуальное окружение

```bash
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows
```

### 3. Установить зависимости

```bash
pip install -r requirements.txt
```

### 4. Создать `.env` файл

```env
DATABASE_URL=postgresql+asyncpg://fitcoach:fitcoach@localhost:5432/fitcoach
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200
```

### 5. Запустить PostgreSQL через Docker

```bash
docker compose up -d
```

### 6. Применить миграции

```bash
alembic upgrade head
```

### 7. Запустить сервер

```bash
uvicorn app.main:app --reload
```

Сервер запустится на `http://localhost:8000`

Документация API: `http://localhost:8000/docs`

## API эндпоинты

### Auth
| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/auth/register` | Регистрация |
| POST | `/auth/login` | Логин, возвращает JWT токен |

### Тренеры
| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/trainers/feed` | Лента тренеров для свайпов |
| GET | `/trainers/{id}` | Профиль тренера |
| POST | `/trainers/profile` | Создать профиль тренера |

### Клиенты
| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/clients/profile` | Создать профиль клиента |
| GET | `/clients/profile` | Получить свой профиль |
| PATCH | `/clients/profile` | Обновить профиль |

### Заявки (свайпы)
| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/swipes` | Клиент свайпает тренера вправо |
| GET | `/swipes/incoming` | Тренер смотрит входящие заявки |
| PATCH | `/swipes/{id}` | Тренер принимает или отклоняет |

### Календарь
| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/scheduling` | Создать тренировку |
| GET | `/scheduling` | Список своих тренировок |
| PATCH | `/scheduling/{id}` | Обновить тренировку |
| DELETE | `/scheduling/{id}` | Удалить тренировку |

### Чат
| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/chat` | Создать чат |
| GET | `/chat` | Список своих чатов |
| GET | `/chat/{id}/messages` | История сообщений |
| WS | `/chat/ws/{chat_id}?token=JWT` | WebSocket соединение |

## Авторизация

Все эндпоинты кроме `/auth/register` и `/auth/login` требуют JWT токен в заголовке:

```
Authorization: Bearer YOUR_TOKEN
```

Токен получается при логине через `POST /auth/login`.

## Роли пользователей

- `client` — может свайпать тренеров, создавать заявки, заполнять анкету
- `trainer` — может создавать профиль, принимать/отклонять заявки

## Тестовые данные

Для быстрого старта можно создать тестовых пользователей через `POST /auth/register`:

```json
// Клиент
{"name": "Тест Клиент", "email": "client@test.com", "password": "123456", "role": "client"}

// Тренер
{"name": "Тест Тренер", "email": "trainer@test.com", "password": "123456", "role": "trainer"}
```

## База данных

Таблицы:
- `users` — все пользователи
- `client_profiles` — анкеты клиентов
- `trainer_profiles` — профили тренеров
- `trainer_requests` — заявки (свайпы)
- `trainings` — тренировки в календаре
- `chats` — чаты
- `messages` — сообщения