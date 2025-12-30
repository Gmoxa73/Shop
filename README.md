# Shop
python .\manage.py import_products .products.yaml

1. Аутентификация и регистрация
POST /api/auth/login/ — вход в систему

Тело запроса (JSON):

json
{
  "email": "user@example.com",
  "password": "secure_password"
}
Ответ (200 OK):

json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 123,
    "first_name": "Иван",
    "last_name": "Петров",
    "email": "user@example.com"
  }
}
Ошибка (400 Bad Request):

json
{"error": "Неверные учётные данные"}
POST /api/auth/register/ — регистрация

Тело запроса:

json
{
  "last_name": "Иванов",
  "first_name": "Алексей",
  "email": "newuser@example.com",
  "password": "strong_password123"
}
Ответ (201 Created):

json
{
  "id": 456,
  "email": "newuser@example.com",
  "first_name": "Алексей",
  "last_name": "Иванов"
}

2. Каталог товаров
GET /api/products/ — список товаров (с фильтрацией и поиском)

Параметры запроса (query params):

search — поиск по названию/описанию;

category — ID категории;

min_price, max_price — диапазон цен;

in_stock — только в наличии (true/false).

Пример запроса:
GET /api/products/?search=ноутбук&min_price=20000&in_stock=true

Ответ:

json
{
  "count": 50,
  "next": "http://api.example.com/api/products/?page=2",
  "previous": null,
  "results": [
    {
      "id": 789,
      "name": "Ноутбук Lenovo IdeaPad",
      "description": "Мощный ноутбук для работы и учёбы",
      "supplier": "ООО 'ТехноТрейд'",
      "characteristics": {
        "Процессор": "Intel Core i5",
        "Оперативная память": "8 GB",
        "Накопитель": "SSD 256 GB"
      },
      "price": 49990.00,
      "stock": 15
    }
  ]
}
3. Корзина
GET /api/cart/ — получить содержимое корзины

Ответ:

json
{
  "items": [
    {
      "product_id": 789,
      "product_name": "Ноутбук Lenovo IdeaPad",
      "store": "Главный склад",
      "price": 49990.00,
      "quantity": 2,
      "total": 99980.00
    }
  ],
  "total_amount": 99980.00
}
POST /api/cart/add/ — добавить товар в корзину

Тело запроса:

json
{
  "product_id": 789,
  "quantity": 1
}
DELETE /api/cart/remove/{item_id}/ — удалить товар из корзины
(где {item_id} — ID позиции в корзине)

4. Контакты
POST /api/contacts/ — создать контакт

Тело запроса:

json
{
  "last_name": "Сидоров",
  "first_name": "Пётр",
  "patronymic": "Сергеевич",
  "email": "contact@example.com",
  "phone": "+79161234567",
  "address": {
    "city": "Москва",
    "street": "Тверская",
    "house": "15",
    "building": "2",
    "structure": "1",
    "apartment": "34"
  }
}
Ответ (201 Created):

json
{
  "id": 101,
  "full_name": "Сидоров Пётр Сергеевич",
  "email": "contact@example.com",
  ...
}
5. Заказы
POST /api/orders/confirm/ — подтвердить заказ

Тело запроса:

json
{
  "cart_id": "c7f3e2a1-b8d4-4e2c-9f1a-2b3c4d5e6f7a",
  "contact_id": 101
}
Ответ (201 Created):

json
{
  "order_number": "ORD-2024-00123",
  "created_at": "2024-01-15T10:30:00Z",
  "total_amount": 99980.00,
  "status": "pending"
}
GET /api/orders/ — история заказов

Ответ:

json
[
  {
    "order_number": "ORD-2024-00123",
    "created_at": "2024-01-15T10:30:00Z",
    "total_amount": 99980.00,
    "status": "confirmed",
    "items": [
      {
        "product_name": "Ноутбук Lenovo IdeaPad",
        "quantity": 2,
        "price": 49990.00
      }
    ]
  }
]
GET /api/orders/{order_number}/ — статус конкретного заказа

Ответ:

json
{
  "order_number": "ORD-2024-00123",
  "created_at": "2024-01-15T10:30:00Z",
  "total_amount": 99980.00,
  "status": "shipped",
  "shipping_date": "2024-01-17T14:00:00Z"
