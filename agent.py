import json
import os
import re
from tools import RetailTools
from data_manager import DataManager

class RetailAgent:
    def __init__(self):
        self.dm = DataManager()
        self.tools = RetailTools(self.dm)

    def run(self, user_input):
        """
        A heuristic-based reasoning engine that processes user input locally.
        Uses regex and keyword matching to call tools based on CSV data.
        """
        user_input_lower = user_input.lower()
        
        # 1. Check for Support/Return Intent (Order ID pattern like O0001)
        order_match = re.search(r'o\d{4}', user_input_lower)
        if order_match:
            order_id = order_match.group(0).upper()
            return_eval = self.tools.evaluate_return(order_id)
            
            if "error" in return_eval:
                return f"I couldn't find any information for Order {order_id}. Please double-check your order number."
            
            order = self.tools.get_order(order_id)
            product = self.tools.get_product(order['product_id'])
            
            status = "eligible" if return_eval['eligible'] else "not eligible"
            type_info = f" ({return_eval['type']})" if "type" in return_eval else ""
            
            return (f"I've looked up Order {order_id} for the '{product['title']}'. "
                    f"Based on our policy, this item is **{status}{type_info}** for a return. "
                    f"Reason: {return_eval['reason']}")

        # 2. Check for Shopping Intent
        # Extract constraints using keywords
        tags = []
        possible_tags = ['modest', 'evening', 'lace', 'cocktail', 'sleeve', 'fitted', 'flowy', 'minimal', 'sparkle', 'prom', 'bridal']
        for tag in possible_tags:
            if tag in user_input_lower:
                tags.append(tag)
        
        max_price = None
        price_match = re.search(r'under \$?(\d+)', user_input_lower)
        if price_match:
            max_price = float(price_match.group(1))
            
        size = None
        size_match = re.search(r'size (\d+)', user_input_lower)
        if size_match:
            size = size_match.group(1)
            
        is_sale = True if "sale" in user_input_lower else None
        
        # Call tool to get data from CSV
        products = self.tools.search_products(tags=tags, max_price=max_price, size=size, is_sale=is_sale)
        
        if not products:
            return "I couldn't find any products matching your specific criteria in our inventory. Could you try broadening your search?"
        
        # Build reasoning-based response from CSV data
        response = "Based on our current inventory, here are the best matches for your request:\n\n"
        for p in products[:3]:
            reason_parts = []
            if tags: reason_parts.append(f"matches your style preference")
            if max_price: reason_parts.append(f"is within your budget at ${p['price']}")
            if size: reason_parts.append(f"is available in size {size}")
            if p['is_sale']: reason_parts.append("is currently on sale")
            
            reason_str = " and ".join(reason_parts) if reason_parts else "is a great choice"
            response += f"- **{p['title']}**: I recommend this because it {reason_str}. It has a bestseller score of {p['bestseller_score']}.\n"
            
        return response
