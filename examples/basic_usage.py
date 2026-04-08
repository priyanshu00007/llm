"""Basic usage examples for the ReAct Agent."""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agent import create_agent


def main():
    """Run basic agent examples."""
    
    print("=" * 60)
    print("ReAct Agent with Mistral - Basic Examples")
    print("=" * 60)
    
    # Initialize agent
    print("\n[1] Initializing agent...")
    try:
        agent = create_agent(verbose=True)
        print("✓ Agent initialized successfully")
        print(f"  Available tools: {', '.join(agent.list_tools())}")
    except ValueError as e:
        print(f"✗ Error: {e}")
        print("\nPlease set your MISTRAL_API_KEY in the .env file")
        return
    
    # Example 1: Calculator
    print("\n" + "=" * 60)
    print("Example 1: Calculator Tool")
    print("=" * 60)
    query = "Calculate 1500 divided by 42"
    print(f"Query: {query}")
    result = agent.run(query)
    print(f"Result: {result}\n")
    
    # Example 2: Time
    print("\n" + "=" * 60)
    print("Example 2: Current Time")
    print("=" * 60)
    query = "What is the current date and time?"
    print(f"Query: {query}")
    result = agent.run(query)
    print(f"Result: {result}\n")
    
    # Example 3: Weather
    print("\n" + "=" * 60)
    print("Example 3: Weather Tool")
    print("=" * 60)
    query = "What is the weather like in Paris?"
    print(f"Query: {query}")
    result = agent.run(query)
    print(f"Result: {result}\n")
    
    # Example 4: File Operations
    print("\n" + "=" * 60)
    print("Example 4: File Write & Read")
    print("=" * 60)
    
    # Write file
    query = 'Write "Hello from ReAct Agent!" to a file named hello.txt'
    print(f"Query: {query}")
    result = agent.run(query)
    print(f"Result: {result}")
    
    # Read file
    query = "Read the file hello.txt"
    print(f"\nQuery: {query}")
    result = agent.run(query)
    print(f"Result: {result}\n")
    
    print("=" * 60)
    print("All examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
