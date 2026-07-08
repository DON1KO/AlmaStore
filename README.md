# 🛒 AlmaStore API

REST API для интернет-магазина **Alma** — полный бэкенд на Django + DRF.

## Возможности

- 🛍️ **Каталог** — категории, товары, акции, локации магазинов
- 🛒 **Корзина** — добавление, обновление количества
- 📦 **Заказы** — оформление, статусы, адреса доставки, способы оплаты
- 👤 **Пользователи** — регистрация по email, OTP-верификация, JWT-авторизация
- 💳 **Бонусная карта** — баланс, QR-код
- 🔔 **Уведомления** — + push через OneSignal
- ❤️ **Избранное** — сохранение любимых товаров
- 🔑 **Сброс пароля** — 3-шаговый процесс через SMS
- 📋 **Swagger/ReDoc** — автодокументация API

## Технологии

- Python 3.10+
- Django 5.2
- Django REST Framework
- SQLite (dev) / PostgreSQL (prod)
- Simple JWT
- django-filter
- django-cors-headers
- drf-yasg (Swagger)
- Jazzmin (админ-панель)
- python-decouple (.env)

## Установка

```bash
# Клонировать
git clone https://github.com/DON1KO/AlmaStore.git
cd AlmaStore

# Виртуальное окружение
python -m venv env
source env/bin/activate   # Linux/Mac

# Зависимости
pip install -r requirements.txt

# Настройка
cp .env.example .env
# Отредактируй .env — укажи SECRET_KEY, EMAIL данные

# Миграции + суперпользователь
python manage.py migrate
python manage.py createsuperuser

# Запуск
python manage.py runserver
```

## API Endpoints

### Авторизация
| Метод | URL | Описание |
|-------|-----|----------|
| POST | `/api/auth/register/` | Регистрация (email + OTP) |
| POST | `/api/auth/verify/` | Подтверждение кода |
| POST | `/api/auth/login/` | Вход (JWT токены) |
| POST | `/api/auth/forgot-password/` | Сброс пароля |

### Магазин
| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/api/home/` | Главная страница (меню, акции, QR) |
| GET | `/api/categories/` | Категории |
| GET | `/api/products/` | Товары |
| GET | `/api/promotions/` | Акции |
| GET | `/api/locations/` | Магазины |

### Корзина и заказы
| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/api/cart/` | Корзина |
| POST | `/api/cart/add_item/` | Добавить товар |
| GET | `/api/orders/` | История заказов |
| POST | `/api/orders/create_order/` | Оформить заказ |

### Профиль
| Метод | URL | Описание |
|-------|-----|----------|
| GET/PUT | `/api/auth/profile/` | Профиль |
| GET | `/api/bonus-cards/` | Бонусная карта + QR |
| GET | `/api/notifications/` | Уведомления |
| GET | `/api/favorites/` | Избранное |

## Документация

- **Swagger UI:** `/swagger/`
- **ReDoc:** `/redoc/`
- **Админ-панель:** `/admin/`

## Автор

**DON1KO** — [GitHub](https://github.com/DON1KO)
