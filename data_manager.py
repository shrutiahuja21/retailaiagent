import pandas as pd
import ast
import os
from datetime import datetime

class DataManager:
    def __init__(self, inventory_path='product_inventory.csv', orders_path='orders.csv', policy_path='policy.txt'):
        self.inventory_path = inventory_path
        self.orders_path = orders_path
        self.policy_path = policy_path
        
        # In-memory cache for lookups
        self._product_cache = {}
        self._order_cache = {}
        self._search_cache = {}

        self.inventory = self._load_inventory()
        self.orders = self._load_orders()
        self.policy = self._load_policy()

    def _load_inventory(self):
        if not os.path.exists(self.inventory_path):
            return pd.DataFrame()
        df = pd.read_csv(self.inventory_path)
        # Parse stock_per_size string to dictionary
        df['stock_per_size'] = df['stock_per_size'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
        return df

    def _load_orders(self):
        if not os.path.exists(self.orders_path):
            return pd.DataFrame()
        return pd.read_csv(self.orders_path)

    def _load_policy(self):
        if not os.path.exists(self.policy_path):
            return ""
        with open(self.policy_path, 'r') as f:
            return f.read()

    def get_product(self, product_id):
        if product_id in self._product_cache:
            return self._product_cache[product_id]
            
        product = self.inventory[self.inventory['product_id'] == product_id]
        if product.empty:
            return None
        
        result = product.iloc[0].to_dict()
        self._product_cache[product_id] = result
        return result

    def get_order(self, order_id):
        if order_id in self._order_cache:
            return self._order_cache[order_id]
            
        order = self.orders[self.orders['order_id'] == order_id]
        if order.empty:
            return None
            
        result = order.iloc[0].to_dict()
        self._order_cache[order_id] = result
        return result

    def search_products(self, filters):
        # Create a cache key from the filters dictionary
        cache_key = str(sorted(filters.items()))
        if cache_key in self._search_cache:
            return self._search_cache[cache_key]

        df = self.inventory.copy()
        
        # Filter by tags
        if 'tags' in filters:
            for tag in filters['tags']:
                df = df[df['tags'].str.contains(tag, case=False, na=False)]
        
        # Filter by price
        if 'max_price' in filters:
            df = df[df['price'] <= filters['max_price']]
        
        # Filter by size availability
        if 'size' in filters:
            size = str(filters['size'])
            def has_size_and_stock(stock_dict):
                return size in stock_dict and stock_dict[size] > 0
            df = df[df['stock_per_size'].apply(has_size_and_stock)]
            
        # Filter by sale
        if filters.get('is_sale'):
            df = df[df['is_sale'] == True]

        # Sort by bestseller_score (descending)
        df = df.sort_values(by='bestseller_score', ascending=False)
        
        result = df.head(10).to_dict('records')
        self._search_cache[cache_key] = result
        return result

    def get_policy(self):
        return self.policy
