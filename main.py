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


class DataBase:
    def __init__(self):
        self._vendors: Dict[int, VendorInDb] = {}
        self.vendor_id = 1
        self._produce: Dict[int, List[ProduceInDb]] = {}
        self.produce_id = 1
        # self._orders: Dict[int, OrderInDb] = {}
        # self.order_id = 1

    def increment_vendor_id(self):
        self.vendor_id += 1

    def increment_produce_id(self):
        self.produce_id += 1

    def increment_order_id(self):
        self.order_id += 1

    def add_vendor(self, vendor: VendorInDb):
        vendor_id = self.vendor_id
        for _, vendor_details in self._vendors.items():
            if vendor_details.phone == vendor.phone:
                return None
            
        self._vendors[vendor_id] = vendor
        return vendor_id
    

    def get_vendor_by_id(self, vendor_id: int):
        if vendor_id not in self._vendors:
            return None
        return self._vendors[vendor_id]


    def get_vendors(self):
        return self._vendors
    

    def update_vendor(self, vendor_id: int, vendor: VendorUpdate):
        if vendor_id not in self._vendors:
            return None
        stored_vendor = self._vendors[vendor_id]
        if vendor.name is not None:
            stored_vendor.name = vendor.name
        if vendor.market_location is not None:
            stored_vendor.market_location = vendor.market_location
        if vendor.phone is not None:
            stored_vendor.phone = vendor.phone
        stored_vendor.updated_at = datetime.utcnow()
        self._vendors[vendor_id] = stored_vendor
        return stored_vendor
    

    def delete_vendor(self, vendor_id: int):
        if vendor_id not in self._vendors:
            return None
        del self._vendors[vendor_id]
        return True

    def add_produce(self, vendor_id: int, produce: ProduceInDb):
        self._produce.setdefault(vendor_id, []).append(produce)
        return produce
    
    def get_produce_by_id(self, produce_id: int):
        for _, produce_details in self._produce.items():
            for produce in produce_details:
                if produce.id == produce_id:
                    return produce
        return None

    def get_produce(self):
        return self._produce
    
    def update_produce(self, produce_id: int, produce: ProduceInDb):
        for _, produce_details in self._produce.items():
            for produce in produce_details:
                if produce.id == produce_id:
                    if produce.name is not None:
                        produce.name = produce.name
                    if produce.category is not None:
                        produce.category = produce.category
                    if produce.price_per_kg is not None:
                        produce.price_per_kg = produce.price_per_kg
                    if produce.quantity_kg is not None:
                        produce.quantity_kg = produce.quantity_kg
                    if produce.is_available is not None:
                        produce.is_available = produce.is_available
                    produce.updated_at = datetime.utcnow()
                    return produce
        return None
    

    def delete_produce(self, produce_id: int):
        for _, produce_details in self._produce:
            for produce in produce_details:
                if produce.id == produce_id:
                    produce_details.remove(produce)
                    return True
        return None


db = DataBase()

@app.post("/vendors", status_code=status.HTTP_201_CREATED)
def create_vendor(vendor: Vendor):
    if not vendor.name or not vendor.market_location or not vendor.phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="All fields are required."
        )
    new_vendor = VendorInDb(
        **vendor.model_dump(),
        id=db.vendor_id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    vendor = db.add_vendor(new_vendor)
    if vendor is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Vendor with this phone number already exists."
        )
    db.increment_vendor_id()

    return {
        "success": True,
        "data": new_vendor,
        "message": "Vendor created successfully"
    }


@app.get("/vendors/{vendor_id}")
def read_vendor(vendor_id: int):
    vendor = db.get_vendor_by_id(vendor_id)
    if vendor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor not found"
        )
    return {
        "success": True,
        "data": vendor,
        "message": "Vendor retrieved successfully"
    }



@app.get("/vendors")
def read_vendors():
    vendors = db.get_vendors()
    return {
        "success": True,
        "data": vendors,
        "message": "Vendors retrieved successfully"
    }


@app.patch("/vendors/{vendor_id}")
def update_vendor(vendor_id: int, vendor: VendorUpdate):
    updated_vendor = db.update_vendor(vendor_id, vendor)
    if updated_vendor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor not found"
        )
    return {
        "success": True,
        "data": updated_vendor,
        "message": "Vendor updated successfully"
    }


@app.delete("/vendors/{vendor_id}") 
def delete_vendor(vendor_id: int):
    result = db.delete_vendor(vendor_id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor not found"
        )
    return {
        "success": True,
        "message": "Vendor deleted successfully"
    }

@app.post("/produce", status_code=status.HTTP_201_CREATED)
def create_produce(vendor_id: int, produce: Produce):
    if not produce.name or not produce.category or not produce.price_per_kg or not produce.quantity_kg or not produce.is_available:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="All fields are required."
        )
    vendor_check = db.get_vendor_by_id(vendor_id)
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
    produce = db.get_produce_by_id(produce_id)
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


@app.patch("/produce/{produce_id}")
def update_produce(produce_id: int, produce: Produce):
    updated_produce = db.update_produce(produce_id, produce)
    if updated_produce is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produce not found"
        )
    return {
        "success": True,
        "data": updated_produce,
        "message": "Produce updated successfully"
    }


@app.delete("/product/{product_id}")
def delete_produce(produce_id:int):
    deleted = db.delete_produce(produce_id)
    if deleted is None:
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail="produce not found"
        )
    return {
        "success": True,
        "message": "produce delete successfully"
    }


















# class Status(Enum):
#     pending = "pending"
#     confirmed = "confirmed"
#     delivered = "delivered"

# class Order(BaseModel):
#     produce_id: int
#     buyer_name: str
#     buyer_phone: str
#     produce_name: str
#     quantity_kg: float
#     total_price: float
#     delivery_area: str
#     status: Status

# class OrderInDb(Order):
#     id: int
#     order_date: datetime
#     updated_at: datetime













    
    

    





    
    

#     def add_order(self, order: OrderInDb):
#         if order.produce_id not in self._produce:
#             return None
#         if order.quantity_kg > self._produce[order.produce_id].quantity_kg:
#             return None
#         if order.produce_name != self._produce[order.produce_id].name:
#             return None
#         self._orders[order.id] = order
#         self.increment_order_id()

#     def get_orders(self):
#         return self._orders



# @app.get("/vendors/{id}")
# def get_vendor_by_id(id:int):
#     vendor = db.get_vendor_by_id(id)
#     if vendor == None:
#         raise HTTPException(
#             status_code= status.HTTP_404_NOT_FOUND,
#             detail="Vendor id not found."
#         )
    
#     return{
#         "success": True,
#         "data": vendor,
#         "message": "vendor retrived successfully"
#     }

    
# # @app.patch("/vendors/{id}", status_code=status.HTTP_200_OK)
# # def update_vendor(id: int, vendor: Vendor):
# #     updated_vendor = db.update_vendor(id, vendor)
# #     if updated_vendor is None:
# #         raise HTTPException(
# #             status_code=status.HTTP_404_NOT_FOUND,
# #             detail="Vendor not found."
# #         )
# #     return {
# #         "success": True,
# #         "data": updated_vendor,
# #         "message": "Vendor updated successfully"
# #     }


# @app.get("/vendors", status_code=status.HTTP_200_OK)
# def get_vendors():
#     vendors = db.get_vendors()
#     return{
#         "success": True,
#         "data": vendors,
#         "message": "vendors retrived successfully"
#     }

# @app.post("/produce", status_code=status.HTTP_201_CREATED)
# def create_produce(vendor_id: int, produce: Produce):
#     if not produce.name or not produce.category or not produce.price_per_kg or not produce.quantity_kg or not produce.is_available:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST, 
#             detail="All fields are required."
#         )
#     vendor_check = db.check_vendor(vendor_id)
#     if vendor_check is None:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST, 
#             detail="Vendor does not exist."
#         )

#     new_produce = ProduceInDb(
#         **produce.model_dump(),
#         id=db.produce_id,
#         created_at=datetime.utcnow(),
#         updated_at=datetime.utcnow()
#     )
#     db.add_produce(vendor_id, new_produce)
#     db.increment_produce_id()

#     return {
#         "success": True,
#         "data": new_produce,
#         "message": "Produce created successfully"
#     }

# @app.get("/produce/{produce_id}")
# def get_produce_by_id(produce_id:int):
#     produce = db.get_produce_by_id(produce_id)
#     if produce is None:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="produce id not found"
#         )
#     return{
#         "success": True,
#         "data": produce,
#         "message": "produce retrived successfully"
#     }

# @app.get("/produce", status_code=status.HTTP_200_OK)
# def get_produce():
#     produce = db.get_produce()

#     return{
#         "success": True,
#         "data": produce,
#         "message": "Produce retrieved successfully"
#     }

# @app.post("/orders", status_code=status.HTTP_201_CREATED)
# def create_order(order: Order):
#     if not order.produce_id or not order.buyer_name or not order.buyer_phone or not order.produce_name or not order.quantity_kg or not order.total_price or not order.delivery_area or not order.status:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST, 
#             detail="All fields are required."
#         )

#     new_order = OrderInDb(
#         **order.model_dump(),
#         id=db.order_id,
#         order_date=datetime.utcnow(),
#         updated_at=datetime.utcnow()
#     )
#     db.add_order(new_order)
#     if new_order is None:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST, 
#             detail="Invalid produce or insufficient quantity."
#         )
#     db.increment_order_id()

#     return {
#         "success": True,
#         "data": new_order,
#         "message": "Order created successfully"
#     }

# @app.get("/orders", status_code=status.HTTP_200_OK)
# def get_orders():
#     orders = db.get_orders()

#     return{
#         "success": True,
#         "data": orders,
#         "message": "Orders retrieved successfully"
#     }
