import json
import os
import re
from openai import OpenAI
from tools import RetailTools
from data_manager import DataManager
from dotenv import load_dotenv

# Try importing Gemini, but don't fail if not installed
try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

# Load environment variables from .env file
load_dotenv()

class RetailAgent:
    def __init__(self, api_key=None, provider="local"):
        self.dm = DataManager()
        self.tools = RetailTools(self.dm)
        self.provider = provider
        
        if provider == "openai":
            self.client = OpenAI(api_key=api_key or os.environ.get("OPENAI_API_KEY"))
            self.model_name = "gpt-4o"
        elif provider == "gemini":
            if not HAS_GEMINI:
                print("Warning: google-generativeai not installed. Falling back to local.")
                self.provider = "local"
            else:
                gemini_key = api_key or os.environ.get("GEMINI_API_KEY")
                genai.configure(api_key=gemini_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                self.model_name = "gemini-1.5-flash"
        
        # System prompt for LLM providers
        self.system_prompt = """
        You are an intelligent Retail AI Assistant with two roles:
        1. Personal Shopper: Help users find products based on their preferences.
        2. Customer Support: Help users with order inquiries and returns.

        GUIDELINES:
        - ALWAYS use tools to fetch data. Never hallucinate product details, order statuses, or policy rules.
        - If a user asks for a recommendation, use search_products.
        - If a user asks about a return, use get_order and evaluate_return.
        - For recommendations:
            - Filter by size and stock availability.
            - Prioritize sale items if requested or appropriate.
            - Consider bestseller_score for quality.
            - Explain WHY you are recommending specific items based on the user's constraints.
        - For support:
            - Fetch the order details first.
            - Apply policy rules strictly using evaluate_return.
            - If an order ID or product ID is not found, inform the user clearly and do not proceed with reasoning.
            - Explain the decision clearly based on the policy (e.g., return window, item status).
        - Be professional, helpful, and concise.
        - Today's date is 2026-05-07.
        """

    def run(self, user_input):
        if self.provider == "openai":
            return self._run_openai(user_input)
        elif self.provider == "gemini":
            return self._run_gemini(user_input)
        else:
            return self._run_local(user_input)

    def _run_local(self, user_input):
        """
        A heuristic-based reasoning engine that doesn't require an LLM API key.
        Uses regex and keyword matching to call tools.
        """
        user_input_lower = user_input.lower()
        
        # 1. Check for Support/Return Intent (Order ID pattern)
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
        # Extract constraints using regex/keywords
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
        
        # Call tool
        products = self.tools.search_products(tags=tags, max_price=max_price, size=size, is_sale=is_sale)
        
        if not products:
            return "I couldn't find any products matching all your specific constraints. Would you like to try with fewer filters?"
        
        # Build reasoning-based response
        response = "Based on your request, I've found some great options from our inventory:\n\n"
        for p in products[:3]:
            reason = f"I'm recommending the **{p['title']}** because it "
            reasons = []
            if tags: reasons.append(f"matches your style ({', '.join(tags)})")
            if max_price: reasons.append(f"is within your budget at ${p['price']}")
            if size: reasons.append(f"is currently in stock for size {size}")
            if p['is_sale']: reasons.append("is currently on sale")
            
            response += f"- {reason}{', '.join(reasons)}. It has a high bestseller score of {p['bestseller_score']}.\n"
            
        return response

    def _run_openai(self, user_input):
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_input}
        ]

        while True:
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    tools=self.get_tool_schemas(),
                    tool_choice="auto"
                )
            except Exception as e:
                return f"OpenAI Error: {e}. Switching to local mode might help."

            response_message = response.choices[0].message
            messages.append(response_message)

            if not response_message.tool_calls:
                return response_message.content

            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                result = self._execute_tool(function_name, function_args)

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": json.dumps(result)
                })

    def _run_gemini(self, user_input):
        try:
            chat = self.model.start_chat(enable_automatic_function_calling=True)
            full_prompt = f"{self.system_prompt}\n\nUser: {user_input}"
            response = chat.send_message(full_prompt, tools=self.get_tool_definitions())
            return response.text
        except Exception as e:
            return f"Gemini Error: {e}. Switching to local mode might help."

    def get_tool_definitions(self):
        return [self.tools.search_products, self.tools.get_product, self.tools.get_order, self.tools.evaluate_return]

    def get_tool_schemas(self):
        return [
            {
                "type": "function",
                "function": {
                    "name": "search_products",
                    "description": "Search for products based on filters like tags, price, size, and sale status.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "tags": {"type": "array", "items": {"type": "string"}},
                            "max_price": {"type": "number"},
                            "size": {"type": "string"},
                            "is_sale": {"type": "boolean"}
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_product",
                    "description": "Get detailed information about a product by its ID.",
                    "parameters": {"type": "object", "properties": {"product_id": {"type": "string"}}, "required": ["product_id"]}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_order",
                    "description": "Get order details by order ID.",
                    "parameters": {"type": "object", "properties": {"order_id": {"type": "string"}}, "required": ["order_id"]}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "evaluate_return",
                    "description": "Evaluate if an order is eligible for return based on policy.",
                    "parameters": {"type": "object", "properties": {"order_id": {"type": "string"}}, "required": ["order_id"]}
                }
            }
        ]

    def _execute_tool(self, name, args):
        if name == "search_products":
            return self.tools.search_products(**args)
        elif name == "get_product":
            return self.tools.get_product(**args)
        elif name == "get_order":
            return self.tools.get_order(**args)
        elif name == "evaluate_return":
            return self.tools.evaluate_return(**args)
        else:
            return {"error": f"Unknown tool: {name}"}
