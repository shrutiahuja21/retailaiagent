import os
import sys
from agent import RetailAgent

def main():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set.")
        print("Please set it using: export OPENAI_API_KEY='your-key-here' (Linux/Mac) or set OPENAI_API_KEY='your-key-here' (Windows)")
        # sys.exit(1) # Commented out for now so the user can see the code structure even without key
        api_key = "dummy-key" # Placeholder

    agent = RetailAgent(api_key=api_key)

    print("--- Retail AI Assistant ---")
    print("Type 'exit' or 'quit' to stop.")
    
    while True:
        try:
            user_input = input("\nYou: ")
            if user_input.lower() in ['exit', 'quit']:
                break
            
            if api_key == "dummy-key":
                print("\nAssistant: [Simulation Mode] API Key not found. Please set OPENAI_API_KEY to interact with the real LLM.")
                continue

            response = agent.run(user_input)
            print(f"\nAssistant: {response}")
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"\nError: {e}")

if __name__ == "__main__":
    main()
