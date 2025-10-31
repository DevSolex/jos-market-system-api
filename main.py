from fastapi import FastAPI, status, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum

app = FastAPI()

class Vendor(BaseModel):
    name: str
    market_location: str
    phone: str

class VendorInDb(Vendor):
    created_at: datetime
    updated_at: datetime
    

class VendorUpdate(BaseModel):
    name: Optional[str] = None
    market_location: Optional[str] = None
    phone: Optional[str] = None

class Produce(BaseModel):
    name: str
    quantity_kg: float
    price_per_kg: float
    category: str
    is_available: bool

class ProduceInDb(Produce):
    id: int
    created_at: datetime
    updated_at: datetime

class Status(Enum):
    pending = "pending"
    confirmed = "confirmed"
    delivered = "delivered"

class Order(BaseModel):
    produce_id: int
    buyer_name: str
    buyer_phone: str
    produce_name: str
    quantity_kg: float
    total_price: float
    delivery_area: str
    status: Status

class OrderInDb(Order):
    id: int
    order_date: datetime
    updated_at: datetime

class DataBase:
    def __init__(self):
        self._vendors: Dict[int, VendorInDb] = {}
        self.vendor_id = 1
        self._produce: Dict[int, List[ProduceInDb]] = {}
        self.produce_id = 1
        self._orders: Dict[int, OrderInDb] = {}
        self.order_id = 1

    def increment_vendor_id(self):
        self.vendor_id += 1

    def increment_produce_id(self):
        self.produce_id += 1

    def increment_order_id(self):
        self.order_id += 1

    def add_vendor(self, vendor: VendorInDb):
        vendor_id = self.vendor_id
        self._vendors[vendor_id] = vendor
        return vendor_id
    
    def get_vendor_by_id(self, id: int):
        if id not in self._vendors:
            return None
        return self._vendors[id]
    

    def get_vendors(self):
        return self._vendors
    
    # def update_vendor(self, vendor_id: int, vendor: VendorUpdate):
    #     if not vendor.market_location or not vendor.name or not vendor.phone:
    #         return None
    #         raise HTTPException(
    #         status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
    #         detail="Atleast One field is required"
    #     )
    #     if vendor_id not in self._vendors:
    #         return None
    #         raise HTTPException(
    #             status_code= status.HTTP_404_NOT_FOUND,
    #             detail= "Vendor id not found"
    #         )
    #     if not vendor.market_location:
    #         self._vendors[vendor_id].market_location = 

    
    def check_vendor(self, vendor_id: int):
        if not vendor_id in self._vendors:
            return None
        return vendor_id
    
    
    def delete_vendor(self, id: int):
        if id not in self._vendors:
            return None
        del self._vendors[id]
        return True
    
    def add_produce(self, vendor_id: int, produce: ProduceInDb):

        self._produce.setdefault(vendor_id, []).append(produce)
        
    
    def get_produce_by_id(self, produce_id: int):
        for _,produce_details in self._produce.items():
            for produce in produce_details:
                if produce.id == produce_id:
                    return produce_details[produce].id
        return None


    def get_produce(self):
        return self._produce
    
    # def update_product(self, id:int, product:ProduceInDb):
    #     if id not in self._produce:
    #         return self._

    def delete_produce(self, id: int):
        if id not in self._produce:
            return None
        del self._produce[id]
        return True

    
    

    def add_order(self, order: OrderInDb):
        if order.produce_id not in self._produce:
            return None
        if order.quantity_kg > self._produce[order.produce_id].quantity_kg:
            return None
        if order.produce_name != self._produce[order.produce_id].name:
            return None
        self._orders[order.id] = order
        self.increment_order_id()

    def get_orders(self):
        return self._orders

db = DataBase()

@app.post("/vendors", status_code=status.HTTP_201_CREATED)
def create_vendor(vendor: Vendor):
    new_vendor = VendorInDb(
        **vendor.model_dump(),
        id=db.vendor_id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add_vendor(new_vendor)
    db.increment_vendor_id()

    return {
        "success": True,
        "data": new_vendor,
        "message": "Vendor created successfully"
    }

@app.get("/vendors/{id}")
def get_vendor_by_id(id:int):
    vendor = db.get_vendor_by_id(id)
    if vendor == None:
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail="Vendor id not found."
        )
    
    return{
        "success": True,
        "data": vendor,
        "message": "vendor retrived successfully"
    }

    
# @app.patch("/vendors/{id}", status_code=status.HTTP_200_OK)
# def update_vendor(id: int, vendor: Vendor):
#     updated_vendor = db.update_vendor(id, vendor)
#     if updated_vendor is None:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Vendor not found."
#         )
#     return {
#         "success": True,
#         "data": updated_vendor,
#         "message": "Vendor updated successfully"
#     }


@app.get("/vendors", status_code=status.HTTP_200_OK)
def get_vendors():
    vendors = db.get_vendors()
    return{
        "success": True,
        "data": vendors,
        "message": "vendors retrived successfully"
    }

@app.post("/produce", status_code=status.HTTP_201_CREATED)
def create_produce(vendor_id: int, produce: Produce):
    if not produce.name or not produce.category or not produce.price_per_kg or not produce.quantity_kg or not produce.is_available:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="All fields are required."
        )
    vendor_check = db.check_vendor(vendor_id)
    if vendor_check is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Vendor does not exist."
        )

    new_produce = ProduceInDb(
        **produce.model_dump(),
        id=db.produce_id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add_produce(vendor_id, new_produce)
    db.increment_produce_id()

    return {
        "success": True,
        "data": new_produce,
        "message": "Produce created successfully"
    }

@app.get("/produce/{produce_id}")
def get_produce_by_id(produce_id:int):
    produce = get_produce_by_id(produce_id)
    if produce is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="produce id not found"
        )
    return{
        "success": True,
        "data": produce,
        "message": "produce retrived successfully"
    }

@app.get("/produce", status_code=status.HTTP_200_OK)
def get_produce():
    produce = db.get_produce()

    return{
        "success": True,
        "data": produce,
        "message": "Produce retrieved successfully"
    }

@app.post("/orders", status_code=status.HTTP_201_CREATED)
def create_order(order: Order):
    if not order.produce_id or not order.buyer_name or not order.buyer_phone or not order.produce_name or not order.quantity_kg or not order.total_price or not order.delivery_area or not order.status:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="All fields are required."
        )

    new_order = OrderInDb(
        **order.model_dump(),
        id=db.order_id,
        order_date=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add_order(new_order)
    if new_order is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Invalid produce or insufficient quantity."
        )
    db.increment_order_id()

    return {
        "success": True,
        "data": new_order,
        "message": "Order created successfully"
    }

@app.get("/orders", status_code=status.HTTP_200_OK)
def get_orders():
    orders = db.get_orders()

    return{
        "success": True,
        "data": orders,
        "message": "Orders retrieved successfully"
    }