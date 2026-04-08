"""Interactive CLI for the ReAct Agent."""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agent import create_agent


def print_header():
    """Print welcome header."""
    print("\n" + "=" * 70)
    print("  ReAct Agent - Interactive CLI")
    print("  Powered by Mistral AI")
    print("=" * 70)
    print("\n  Available tools:")
    print("  • calculator - Math calculations")
    print("  • get_weather - Weather information (API)")
    print("  • get_weather_no_api - Weather (web scraping)")
    print("  • get_current_time - Current date/time")
    print("  • write_file - Save to file")
    print("  • read_file - Read from file")
    print("  • scrape_webpage - Extract webpage content")
    print("  • crawl_website - Deep website crawling")
    print("  • search_web - Web search (no API key)")
    print("  • get_latest_news - News extraction")
    print("  • get_stock_price_no_api - Stock prices")
    print("  • make_api_request - HTTP API calls")
    print("  • query_database - SQL queries")
    print("  • analyze_csv - CSV data analysis")
    print("  • send_email - Email notifications")
    print("\n  Commands:")
    print("  • quit, exit - Exit the program")
    print("  • tools - List available tools")
    print("  • clear - Clear the screen")
    print("=" * 70)


def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def main():
    """Run interactive CLI."""
    print_header()
    
    # Initialize agent
    try:
        print("\n🤖 Initializing agent...")
        agent = create_agent(verbose=True)
        print("✓ Agent ready!\n")
    except ValueError as e:
        print(f"\n✗ Error: {e}")
        print("\nPlease set your MISTRAL_API_KEY in the .env file")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        sys.exit(1)
    
    # Main loop
    while True:
        try:
            # Get user input
            user_input = input("\n📝 Enter your query (or 'quit' to exit):\n> ").strip()
            
            if not user_input:
                continue
            
            # Handle commands
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            if user_input.lower() == 'tools':
                print("\nAvailable tools:")
                for tool in agent.list_tools():
                    print(f"  • {tool}")
                continue
            
            if user_input.lower() == 'clear':
                clear_screen()
                print_header()
                continue
            
            if user_input.lower() == 'help':
                print_header()
                continue
            
            # Execute query
            print("\n🔄 Processing...\n")
            result = agent.run(user_input)
            
            print("\n📊 Result:")
            print("-" * 70)
            print(result)
            print("-" * 70)
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
