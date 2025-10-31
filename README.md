'''Task: Build a Jos Market Produce API
Project Overview
Create a simple API for managing a produce market in Jos, Nigeria. Vendors can list their farm produce, and buyers can browse and place orders.
Data Models (Pydantic)
1. Vendor

id: int
name: str (e.g., "Malam Audu", "Mama Grace")
market_location: str (Terminus, Katako, Bukuru, Farin Gada, Building Materials)
phone: str
created_at: datetime

2. Produce

id: int
vendor_id: int
name: str (e.g., "Irish Potato", "Tomatoes", "Carrots", "Cabbage")
quantity_kg: float (in kilograms)
price_per_kg: float (in Naira)
category: str (Vegetables, Fruits, Grains, Tubers)
is_available: bool

3. Order

id: int
produce_id: int
buyer_name: str
buyer_phone: str
produce_name: str
quantity_kg: float
total_price: float
delivery_area: str (Rayfield, Bukuru, Terminus, Jos South, etc.)
status: str (pending, confirmed, delivered)
order_date: datetime


Required Endpoints
Vendors

POST /vendors - Register new vendor
GET /vendors - Get all vendors
GET /vendors/{id} - Get vendor with their produce
PUT /vendors/{id} - Update vendor info
DELETE /vendors/{id} - Remove vendor

Produce

POST /produce - Add new produce item
GET /produce - Get all produce with filtering and sorting
GET /produce/{id} - Get specific produce details
PUT /produce/{id} - Update produce item
PATCH /produce/{id}/stock - Update quantity available
DELETE /produce/{id} - Remove produce

Orders

POST /orders - Place new order
GET /orders - Get all orders with filtering
GET /orders/{id} - Get order details
PATCH /orders/{id}/status - Update order status
DELETE /orders/{id} - Cancel order


Filtering & Sorting Requirements
GET /produce should support:
Filtering:

category: Filter by category (Vegetables, Fruits, Grains, Tubers)
vendor_id: Filter by vendor
market_location: Filter by market location
max_price: Show produce with price_per_kg <= value
available_only: Show only available items (true/false)
search: Search in produce name

Sorting:

sort_by: name, price_per_kg, quantity_kg
order: asc or desc (default: asc)
'''
