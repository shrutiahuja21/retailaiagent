from data_manager import DataManager
from datetime import datetime

class RetailTools:
    def __init__(self, data_manager: DataManager):
        self.dm = data_manager

    def search_products(self, tags=None, max_price=None, size=None, is_sale=None):
        """
        Search for products based on various filters.
        :param tags: List of strings (e.g., ['modest', 'evening'])
        :param max_price: Maximum price as a number
        :param size: Requested size as a string or number
        :param is_sale: Boolean to filter only sale items
        """
        filters = {}
        if tags: filters['tags'] = tags
        if max_price: filters['max_price'] = max_price
        if size: filters['size'] = size
        if is_sale is not None: filters['is_sale'] = is_sale
        
        return self.dm.search_products(filters)

    def get_product(self, product_id):
        """
        Retrieve detailed information about a specific product.
        """
        product = self.dm.get_product(product_id)
        if not product:
            return {"error": f"Product {product_id} not found."}
        return product

    def get_order(self, order_id):
        """
        Retrieve details of a specific order.
        """
        order = self.dm.get_order(order_id)
        if not order:
            return {"error": f"Order {order_id} not found."}
        return order

    def evaluate_return(self, order_id):
        """
        Evaluates if an order is eligible for return based on policy rules.
        """
        order = self.dm.get_order(order_id)
        if not order:
            return {"error": f"Order {order_id} not found."}
        
        product = self.dm.get_product(order['product_id'])
        if not product:
            return {"error": f"Product {order['product_id']} for order {order_id} not found."}

        # Calculate days since order (assuming current date is 2026-05-07 as per system prompt)
        current_date = datetime(2026, 5, 7)
        order_date = datetime.strptime(order['order_date'], '%Y-%m-%d')
        days_elapsed = (current_date - order_date).days

        reasons = []
        is_eligible = True
        return_type = "Full Refund"

        # 1. Clearance Rule
        if product.get('is_clearance'):
            return {"eligible": False, "reason": "Clearance items are final sale and not eligible for return."}

        # 2. Vendor Exceptions & Return Type
        vendor = product.get('vendor')
        is_sale = product.get('is_sale')
        
        if vendor == 'Aurelia Couture':
            return_type = "Exchange Only"
        elif is_sale:
            return_type = "Store Credit"
        else:
            return_type = "Full Refund"
        
        # 3. Window Rules
        max_days = 14 # Normal
        if is_sale:
            max_days = 7
        
        if vendor == 'Nocturne':
            max_days = 21

        if days_elapsed > max_days:
            return {
                "eligible": False, 
                "reason": f"Return window expired. Order was placed {days_elapsed} days ago, but the limit for this item is {max_days} days."
            }

        # 4. Special Vendor Rules (Aurelia Couture - no refunds)
        if vendor == 'Aurelia Couture':
            return {
                "eligible": True,
                "type": "Exchange Only",
                "reason": f"Eligible for exchange only per {vendor} policy. Order was placed {days_elapsed} days ago (limit {max_days} days)."
            }

        return {
            "eligible": True,
            "type": return_type,
            "reason": f"Within the {max_days}-day return window for this item ({days_elapsed} days elapsed)."
        }
