"""Advanced multi-step examples for the ReAct Agent."""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agent import create_agent


def example_1_research_and_save():
    """Research a topic using web scraping and save results."""
    print("\n" + "=" * 60)
    print("Example 1: Web Scraping + File Save")
    print("=" * 60)
    
    agent = create_agent(verbose=True)
    
    query = (
        "Scrape https://news.ycombinator.com and extract the first 3 story titles, "
        "then save them to a file named 'hackernews.txt'"
    )
    print(f"Query: {query}\n")
    
    result = agent.run(query)
    print(f"\nFinal Result: {result}")


def example_2_weather_travel():
    """Check weather and provide travel advice."""
    print("\n" + "=" * 60)
    print("Example 2: Weather + Decision Making")
    print("=" * 60)
    
    agent = create_agent(verbose=True)
    
    query = (
        "Get the weather for London and Tokyo. "
        "If London is warmer than Tokyo, say 'Go to London'. "
        "Otherwise, say 'Go to Tokyo'."
    )
    print(f"Query: {query}\n")
    
    result = agent.run(query)
    print(f"\nFinal Result: {result}")


def example_3_calculations():
    """Complex calculations and file saving."""
    print("\n" + "=" * 60)
    print("Example 3: Calculator + File Operations")
    print("=" * 60)
    
    agent = create_agent(verbose=True)
    
    query = (
        "Calculate the following: (1500 * 1.08) + (2300 * 0.95) - 500. "
        "Then divide by 12 to get the monthly amount. "
        "Save the final result to 'monthly_calculation.txt'"
    )
    print(f"Query: {query}\n")
    
    result = agent.run(query)
    print(f"\nFinal Result: {result}")


def example_4_api_request():
    """Make an API request and process the response."""
    print("\n" + "=" * 60)
    print("Example 4: API Request + Calculator")
    print("=" * 60)
    
    agent = create_agent(verbose=True)
    
    # Using a public API for testing
    query = (
        "Make a GET request to https://httpbin.org/get. "
        "Then save the response headers to a file named 'api_response.txt'"
    )
    print(f"Query: {query}\n")
    
    result = agent.run(query)
    print(f"\nFinal Result: {result}")


def example_5_multi_step():
    """Multi-step workflow with multiple tools."""
    print("\n" + "=" * 60)
    print("Example 5: Multi-Step Workflow")
    print("=" * 60)
    
    agent = create_agent(verbose=True)
    
    query = (
        "1. Get the current time\n"
        "2. Check the weather in New York\n"
        "3. Calculate 100 divided by 3\n"
        "4. Write all three results to a file named 'multi_step_report.txt'"
    )
    print(f"Query: {query}\n")
    
    result = agent.run(query)
    print(f"\nFinal Result: {result}")


def main():
    """Run all advanced examples."""
    print("=" * 60)
    print("ReAct Agent with Mistral - Advanced Examples")
    print("=" * 60)
    
    try:
        # Run selected examples (comment out unwanted ones)
        example_1_research_and_save()
        example_2_weather_travel()
        example_3_calculations()
        # example_4_api_request()  # Uncomment to test API requests
        # example_5_multi_step()  # Uncomment to test multi-step
        
    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("Advanced examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
