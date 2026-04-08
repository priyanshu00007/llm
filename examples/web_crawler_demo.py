"""Web Crawler Demo - Advanced scraping without API keys."""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agent import create_agent


def demo_1_search_web():
    """Demo: Search web without API keys."""
    print("\n" + "=" * 60)
    print("Demo 1: Web Search (No API Key Required)")
    print("=" * 60)
    
    agent = create_agent()
    
    queries = [
        "Python programming tutorials",
        "latest AI news 2024",
        "best programming laptops"
    ]
    
    for query in queries[:1]:  # Just first one for demo
        print(f"\n🔍 Searching: '{query}'")
        result = agent.run(f"Search the web for: {query}")
        print(f"\n📊 Results:\n{result[:1000]}")
        break


def demo_2_weather_no_api():
    """Demo: Get weather without API keys."""
    print("\n" + "=" * 60)
    print("Demo 2: Weather via Web Scraping (No API Key)")
    print("=" * 60)
    
    agent = create_agent()
    
    cities = ["London", "New York", "Tokyo"]
    
    for city in cities[:1]:
        print(f"\n🌤️  Getting weather for: {city}")
        result = agent.run(f"Get the weather in {city} using web search")
        print(f"\n📊 Result:\n{result}")


def demo_3_news_extraction():
    """Demo: Get latest news."""
    print("\n" + "=" * 60)
    print("Demo 3: Latest News (No API Key Required)")
    print("=" * 60)
    
    agent = create_agent()
    
    print("\n📰 Getting latest technology news...")
    result = agent.run("Get the latest news about technology")
    print(f"\n📊 Results:\n{result[:1500]}")


def demo_4_stock_prices():
    """Demo: Get stock prices without API."""
    print("\n" + "=" * 60)
    print("Demo 4: Stock Prices via Web Scraping")
    print("=" * 60)
    
    agent = create_agent()
    
    symbols = ["AAPL", "GOOGL", "TSLA"]
    
    for symbol in symbols[:2]:
        print(f"\n📈 Checking stock: {symbol}")
        result = agent.run(f"Get the current stock price for {symbol}")
        print(f"\n📊 Result:\n{result}")


def demo_5_website_crawl():
    """Demo: Deep website crawling."""
    print("\n" + "=" * 60)
    print("Demo 5: Comprehensive Website Crawling")
    print("=" * 60)
    
    agent = create_agent()
    
    # Crawl Python documentation
    url = "https://docs.python.org/3/tutorial/"
    print(f"\n🕷️  Crawling: {url}")
    print("(This may take a moment...)")
    
    result = agent.run(f"Crawl the website {url} and give me a summary of what content is available")
    print(f"\n📊 Results:\n{result[:2000]}")


def demo_6_multi_step_research():
    """Demo: Multi-step research using crawler."""
    print("\n" + "=" * 60)
    print("Demo 6: Multi-Step Research Workflow")
    print("=" * 60)
    
    agent = create_agent()
    
    query = (
        "Search for the latest news about artificial intelligence, "
        "then get the weather in San Francisco, "
        "and save a summary of both to a file called 'daily_brief.txt'"
    )
    
    print(f"\n🎯 Complex Query:\n{query}")
    print("\n⏳ Processing (this may take a minute)...")
    
    result = agent.run(query)
    print(f"\n📊 Final Result:\n{result}")


def main():
    """Run crawler demos."""
    print("=" * 70)
    print("  ReAct Agent - Web Crawler Demo")
    print("  Advanced Web Scraping (No API Keys Required)")
    print("=" * 70)
    
    print("\n🦙 Powered by Mistral AI + Web Crawler Tools")
    print("\nThese demos show how to:")
    print("  • Search the web without API keys")
    print("  • Get weather via web scraping")
    print("  • Extract latest news")
    print("  • Check stock prices")
    print("  • Deep crawl websites")
    print("  • Multi-step research workflows")
    
    try:
        # Run selected demos
        print("\n" + "=" * 70)
        print("Starting Demos...")
        print("=" * 70)
        
        demo_1_search_web()
        demo_2_weather_no_api()
        demo_3_news_extraction()
        demo_4_stock_prices()
        # demo_5_website_crawl()  # Uncomment to test deep crawling
        # demo_6_multi_step_research()  # Uncomment to test complex workflow
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error running demos: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("Demo completed!")
    print("=" * 70)
    print("\n💡 Tip: All these features work WITHOUT API keys!")
    print("   The agent uses web scraping to gather information.")


if __name__ == "__main__":
    main()
