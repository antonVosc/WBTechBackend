# WBTechBackend
Задание на стажировку - Shop API

REST API интернет-магазина на Django REST Framework: регистрация/авторизация,
профиль с балансом, каталог товаров, корзина и оформление заказов со списанием
баланса и остатков склада.

## Запуск

1. ```bash
git clone https://github.com/antonVosc/WBTechBackend.git
```

2. ```bash
cd WBTechBackend/
```

3. ```bash
docker-compose up --build
```

Создать суперпользователя (в отдельном терминале, пока контейнеры работают):

```bash
docker-compose exec web python manage.py createsuperuser
```

Тесты
```bash
docker-compose exec web python manage.py test
```

## Запуск без Docker (локально)

1. ```bash
python -m venv .venv && source .venv/bin/activate
```

2. ```bash
pip install -r requirements.txt
```

#  POSTGRES_HOST=localhost в .env

3. ```bash
python manage.py migrate
```

4. ```bash
python manage.py createsuperuser
```

5. ```bash
python manage.py runserver
```

## Тесты

```bash
python manage.py test
```

## Основные эндпоинты

| Метод | URL | Описание | Доступ |
|---|---|---|---|
| POST | `/api/users/register/` | Регистрация | все |
| POST | `/api/token/` | Получить JWT (access/refresh) | все |
| POST | `/api/token/refresh/` | Обновить access-токен | все |
| GET | `/api/users/me/` | Профиль текущего пользователя | авторизован |
| POST | `/api/users/me/top-up/` | Пополнить баланс `{"amount": "100.00"}` | авторизован |
| GET | `/api/products/` | Список товаров | все |
| POST/PUT/PATCH/DELETE | `/api/products/{id}/` | Управление товарами | только админ |
| GET | `/api/cart/` | Текущая корзина | авторизован |
| POST | `/api/cart/items/` | Добавить товар `{"product_id": 1, "quantity": 2}` | авторизован |
| PATCH | `/api/cart/items/{id}/` | Изменить количество | авторизован |
| DELETE | `/api/cart/items/{id}/` | Удалить товар из корзины | авторизован |
| POST | `/api/orders/checkout/` | Оформить заказ из корзины | авторизован |
| GET | `/api/orders/` | История заказов пользователя | авторизован |
| GET | `/api/orders/{id}/` | Детали заказа | авторизован |

Полная документация - на `/api/docs/` (Swagger) и `/api/redoc/`.

## Оформление заказа: что проверяется

1. Корзина не пуста.
2. На складе достаточно каждого товара (`stock >= quantity`).
3. У пользователя достаточно средств на балансе.
4. При успехе: списывается баланс, уменьшается остаток на складе, товары
   заказа фиксируются в `OrderItem` (с ценой на момент покупки), корзина
   очищается, в лог (`logs/orders.log` + консоль) и по email (консольный
   backend) пишется уведомление о заказе.
5. При ошибке — весь процесс откатывается (атомарная транзакция), возвращается
   `400` с описанием причины.

## Возможные доработки

- Пагинация/фильтрация каталога уже подключены (`django-filter`, поиск по
  названию/описанию, сортировка по цене/остатку).
- Роль "админ" — стандартный `is_staff` из Django; при желании легко
  расширяется до отдельной группы/роли.
