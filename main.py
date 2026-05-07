import sys
from agent import RetailAgent

def main():
    agent = RetailAgent()

    print("--- Retail AI Assistant (Local Engine) ---")
    print("Type 'exit' or 'quit' to stop.")
    
    while True:
        try:
            user_input = input("\nYou: ")
            if user_input.lower() in ['exit', 'quit']:
                break
            
            response = agent.run(user_input)
            print(f"\nAssistant: {response}")
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"\nError: {e}")

if __name__ == "__main__":
    main()
