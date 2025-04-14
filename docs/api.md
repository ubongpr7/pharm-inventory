# API Documentation

## Authentication
```http
POST /api/auth/login/
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}
```

## Inventory Endpoints
### Get Inventory Items
```http
GET /api/inventory/items/
Authorization: Bearer {token}
```

### Create Inventory Item
```http
POST /api/inventory/items/
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Paracetamol 500mg",
  "batch_number": "BATCH123",
  "quantity": 100,
  "expiry_date": "2025-12-31"
}
```

## Order Endpoints
### Create Purchase Order
```http
POST /api/orders/purchase/
Authorization: Bearer {token}
Content-Type: application/json

{
  "supplier": 1,
  "items": [
    {
      "product": 1,
      "quantity": 50,
      "unit_price": 2.50
    }
  ]
}
```

## Error Responses
| Status Code | Description |
|-------------|-------------|
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 500 | Server Error |
