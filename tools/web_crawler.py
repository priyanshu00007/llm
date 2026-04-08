"""Advanced Web Crawler for extracting data from websites without APIs."""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, quote_plus
from typing import List, Dict, Optional
import re
import json


class WebCrawler:
    """Advanced web crawler for data extraction."""
    
    def __init__(self, timeout: int = 15):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })
    
    def crawl_page(self, url: str, extract_links: bool = False, extract_images: bool = False, 
                   extract_tables: bool = False) -> Dict:
        """
        Comprehensive page crawling with multiple extraction options.
        
        Args:
            url: URL to crawl
            extract_links: Extract all links
            extract_images: Extract image URLs
            extract_tables: Extract data tables
        
        Returns:
            Dictionary with extracted data
        """
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            result = {
                'url': url,
                'title': self._get_title(soup),
                'text': self._get_clean_text(soup),
                'meta': self._get_meta_data(soup),
            }
            
            if extract_links:
                result['links'] = self._get_links(soup, url)
            
            if extract_images:
                result['images'] = self._get_images(soup, url)
            
            if extract_tables:
                result['tables'] = self._get_tables(soup)
            
            return result
            
        except Exception as e:
            return {'error': str(e), 'url': url}
    
    def search_google(self, query: str, num_results: int = 5) -> List[Dict]:
        """
        Search Google and extract results (web scraping approach).
        
        Args:
            query: Search query
            num_results: Number of results to return
        
        Returns:
            List of search results with title, link, snippet
        """
        try:
            # Use DuckDuckGo HTML version (no API key needed)
            search_url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
            
            response = self.session.get(search_url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            results = []
            result_elements = soup.find_all('div', class_='result') or soup.find_all('a', class_='result__a')
            
            # Try multiple selectors for DuckDuckGo
            if not result_elements:
                result_elements = soup.find_all('a', href=True)
                result_elements = [a for a in result_elements if a.get('href', '').startswith('http')]
            
            for element in result_elements[:num_results]:
                try:
                    # Extract based on element type
                    if element.name == 'a' and 'result__a' in element.get('class', []):
                        title = element.get_text(strip=True)
                        link = element.get('href', '')
                        snippet_elem = element.find_parent().find_next_sibling() if element.find_parent() else None
                        snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                    else:
                        # Generic extraction
                        title_elem = element.find(['h2', 'h3', 'a']) or element
                        title = title_elem.get_text(strip=True)[:200]
                        
                        link_elem = element.find('a', href=True)
                        link = link_elem['href'] if link_elem else element.get('href', '')
                        
                        snippet_elem = element.find(['p', 'span', 'div'], class_=lambda x: x and ('snippet' in x.lower() if x else False))
                        if not snippet_elem:
                            snippet_elem = element.find('a').find_next_sibling() if element.find('a') else None
                        snippet = snippet_elem.get_text(strip=True)[:300] if snippet_elem else ""
                    
                    # Clean link
                    if link.startswith('//'):
                        link = 'https:' + link
                    elif link.startswith('/'):
                        link = 'https://duckduckgo.com' + link
                    elif not link.startswith('http'):
                        continue
                    
                    if title and link:
                        results.append({
                            'title': title,
                            'link': link,
                            'snippet': snippet
                        })
                except Exception:
                    continue
            
            return results[:num_results]
            
        except Exception as e:
            return [{'error': f'Search failed: {str(e)}', 'title': 'Error', 'link': '', 'snippet': ''}]
    
    def get_weather_from_web(self, city: str) -> Dict:
        """
        Get weather by scraping weather websites (no API key needed).
        
        Args:
            city: City name
        
        Returns:
            Weather data dictionary
        """
        try:
            # Search for weather and scrape the result
            search_query = f"weather {city} today"
            search_results = self.search_google(search_query, num_results=3)
            
            weather_data = {
                'city': city,
                'temperature': None,
                'condition': None,
                'source': 'Web Scraping',
                'note': 'Data extracted from web search'
            }
            
            # Try to extract from search snippets
            for result in search_results:
                if 'error' in result:
                    continue
                    
                snippet = result.get('snippet', '')
                title = result.get('title', '')
                
                # Look for temperature patterns (e.g., "25°C", "77°F", "25 degrees")
                temp_match = re.search(r'(\d+)\s*[°º]\s*[CFcf]', snippet + title)
                if temp_match:
                    weather_data['temperature'] = temp_match.group(0)
                
                # Look for common weather conditions
                conditions = ['sunny', 'clear', 'cloudy', 'partly cloudy', 'rain', 'rainy', 
                             'snow', 'snowy', 'storm', 'thunderstorm', 'fog', 'foggy',
                             'overcast', 'windy', 'humid']
                for condition in conditions:
                    if condition.lower() in (snippet + title).lower():
                        weather_data['condition'] = condition.capitalize()
                        break
                
                if weather_data['temperature'] and weather_data['condition']:
                    break
            
            # If no data found, try to crawl a weather website directly
            if not weather_data['temperature']:
                # Try wttr.in (text-based weather service)
                try:
                    wttr_url = f"https://wttr.in/{quote_plus(city)}?format=j1"
                    response = self.session.get(wttr_url, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        current = data.get('current_condition', [{}])[0]
                        weather_data['temperature'] = f"{current.get('temp_C', '?')}°C / {current.get('temp_F', '?')}°F"
                        weather_data['condition'] = current.get('weatherDesc', [{}])[0].get('value', 'Unknown')
                        weather_data['humidity'] = f"{current.get('humidity', '?')}%"
                        weather_data['wind'] = f"{current.get('windspeedKmph', '?')} km/h"
                        weather_data['source'] = 'wttr.in'
                except Exception:
                    pass
            
            return weather_data
            
        except Exception as e:
            return {
                'city': city,
                'error': f'Could not get weather: {str(e)}',
                'source': 'Web Scraping'
            }
    
    def extract_news(self, topic: str = None, url: str = None, num_articles: int = 5) -> List[Dict]:
        """
        Extract news articles from a news website or via search.
        
        Args:
            topic: Topic to search for
            url: Direct URL to news site (optional)
            num_articles: Number of articles to extract
        
        Returns:
            List of news articles
        """
        try:
            if url:
                # Crawl specific news site
                data = self.crawl_page(url, extract_links=True)
                text = data.get('text', '')
                
                # Simple extraction of headlines and snippets
                articles = []
                lines = [l.strip() for l in text.split('\n') if l.strip() and len(l.strip()) > 20]
                
                for i, line in enumerate(lines[:num_articles]):
                    articles.append({
                        'title': line[:100],
                        'summary': line[:200],
                        'source': url
                    })
                
                return articles
            else:
                # Search for news
                query = f"latest news {topic}" if topic else "latest news today"
                search_results = self.search_google(query, num_results=num_articles)
                
                articles = []
                for result in search_results:
                    if 'error' not in result:
                        articles.append({
                            'title': result['title'],
                            'summary': result['snippet'],
                            'source': result['link']
                        })
                
                return articles
                
        except Exception as e:
            return [{'error': str(e), 'title': 'Error fetching news'}]
    
    def get_stock_price(self, symbol: str) -> Dict:
        """
        Get stock price by scraping financial websites.
        
        Args:
            symbol: Stock symbol (e.g., AAPL, GOOGL)
        
        Returns:
            Stock data
        """
        try:
            # Search for stock price
            search_results = self.search_google(f"{symbol} stock price", num_results=3)
            
            stock_data = {
                'symbol': symbol.upper(),
                'price': None,
                'change': None,
                'source': 'Web Scraping'
            }
            
            # Extract from search results
            for result in search_results:
                snippet = result.get('snippet', '')
                title = result.get('title', '')
                combined = snippet + ' ' + title
                
                # Look for price patterns
                price_match = re.search(r'\$?([\d,]+\.?\d*)', combined)
                if price_match:
                    stock_data['price'] = f"${price_match.group(1)}"
                
                # Look for change percentage
                change_match = re.search(r'([+-]?[\d.]+%)', combined)
                if change_match:
                    stock_data['change'] = change_match.group(1)
                
                if stock_data['price']:
                    break
            
            return stock_data
            
        except Exception as e:
            return {'symbol': symbol, 'error': str(e)}
    
    def extract_faq(self, url: str) -> List[Dict]:
        """
        Extract FAQ/Q&A from a webpage.
        
        Args:
            url: URL to extract FAQ from
        
        Returns:
            List of Q&A pairs
        """
        try:
            data = self.crawl_page(url)
            text = data.get('text', '')
            
            # Look for common FAQ patterns
            faqs = []
            
            # Pattern 1: Q: / A: format
            qa_pattern = re.findall(r'[Qq]:(.+?)[Aa]:(.+?)(?=[Qq]:|$)', text, re.DOTALL)
            for q, a in qa_pattern[:10]:
                faqs.append({
                    'question': q.strip()[:200],
                    'answer': a.strip()[:500]
                })
            
            # Pattern 2: Numbered questions
            if not faqs:
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    if re.match(r'^\d+[.\)]\s+', line) and '?' in line:
                        question = line.strip()
                        answer = lines[i+1].strip() if i+1 < len(lines) else ""
                        if answer and len(answer) > 20:
                            faqs.append({'question': question, 'answer': answer})
            
            return faqs if faqs else [{'question': 'No FAQ found', 'answer': 'Could not extract FAQ from this page'}]
            
        except Exception as e:
            return [{'question': 'Error', 'answer': str(e)}]
    
    def extract_product_info(self, url: str) -> Dict:
        """
        Extract product information from e-commerce pages.
        
        Args:
            url: Product page URL
        
        Returns:
            Product data dictionary
        """
        try:
            data = self.crawl_page(url)
            soup = BeautifulSoup(requests.get(url, headers=self.session.headers, timeout=self.timeout).content, 'html.parser')
            
            product = {
                'title': data.get('title', ''),
                'description': data.get('text', '')[:500],
                'price': None,
                'availability': None,
                'rating': None,
            }
            
            # Try to find price
            price_selectors = ['.price', '.product-price', '[class*="price"]', '[class*="Price"]',
                             '.a-price', '.sr-only', '[data-price]']
            for selector in price_selectors:
                price_elem = soup.select_one(selector)
                if price_elem:
                    price_text = price_elem.get_text(strip=True)
                    if '$' in price_text or '€' in price_text or '£' in price_text:
                        product['price'] = price_text[:50]
                        break
            
            # Try to find rating
            rating_elem = soup.find(attrs={'class': lambda x: x and 'rating' in x.lower() if x else False})
            if rating_elem:
                product['rating'] = rating_elem.get_text(strip=True)[:50]
            
            return product
            
        except Exception as e:
            return {'error': str(e), 'url': url}
    
    # Helper methods
    def _get_title(self, soup: BeautifulSoup) -> str:
        """Extract page title."""
        title = soup.find('title')
        return title.get_text(strip=True) if title else "No title"
    
    def _get_clean_text(self, soup: BeautifulSoup) -> str:
        """Extract clean text content."""
        # Remove script and style elements
        for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
            element.decompose()
        
        text = soup.get_text(separator='\n', strip=True)
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        return '\n'.join(lines)
    
    def _get_meta_data(self, soup: BeautifulSoup) -> Dict:
        """Extract meta tags."""
        meta = {}
        for tag in soup.find_all('meta'):
            name = tag.get('name', tag.get('property', ''))
            content = tag.get('content', '')
            if name and content:
                meta[name] = content
        return meta
    
    def _get_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Extract all links."""
        links = []
        for a in soup.find_all('a', href=True):
            href = urljoin(base_url, a['href'])
            text = a.get_text(strip=True)[:100]
            links.append({'text': text, 'url': href})
        return links[:50]  # Limit to 50 links
    
    def _get_images(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Extract all images."""
        images = []
        for img in soup.find_all('img', src=True):
            src = urljoin(base_url, img['src'])
            alt = img.get('alt', '')
            images.append({'src': src, 'alt': alt})
        return images[:30]  # Limit to 30 images
    
    def _get_tables(self, soup: BeautifulSoup) -> List[List[List[str]]]:
        """Extract data tables."""
        tables = []
        for table in soup.find_all('table'):
            rows = []
            for tr in table.find_all('tr'):
                row = [td.get_text(strip=True) for td in tr.find_all(['td', 'th'])]
                if row:
                    rows.append(row)
            if rows:
                tables.append(rows)
        return tables[:5]  # Limit to 5 tables


# Tool functions for the agent
crawler = WebCrawler()


def crawl_website(url: str, max_depth: int = 1) -> str:
    """
    Crawl a website and extract content.
    
    Args:
        url: Website URL to crawl
        max_depth: How deep to crawl (1 = just this page, 2 = this page + linked pages)
    
    Returns:
        Extracted content summary
    """
    try:
        result = crawler.crawl_page(url, extract_links=True, extract_tables=True)
        
        if 'error' in result:
            return f"Error crawling {url}: {result['error']}"
        
        output = f"Crawled: {result['url']}\n"
        output += f"Title: {result['title']}\n\n"
        
        # Add main text (truncated)
        text = result.get('text', '')
        if text:
            output += f"Content Preview:\n{text[:2000]}\n\n"
        
        # Add tables if found
        tables = result.get('tables', [])
        if tables:
            output += f"Found {len(tables)} data table(s)\n"
        
        # Add links summary
        links = result.get('links', [])
        if links:
            output += f"\nFound {len(links)} link(s)\n"
            output += "Top 5 links:\n"
            for link in links[:5]:
                output += f"  - {link['text'][:50]}: {link['url'][:80]}\n"
        
        return output
        
    except Exception as e:
        return f"Error: {str(e)}"


def search_web(query: str, num_results: int = 5) -> str:
    """
    Search the web and get results without using API keys.
    
    Args:
        query: Search query
        num_results: Number of results (default 5)
    
    Returns:
        Search results
    """
    results = crawler.search_google(query, num_results)
    
    if not results or all('error' in r for r in results):
        return "Search failed. Please try a different query."
    
    output = f"Search Results for: '{query}'\n"
    output += "=" * 50 + "\n\n"
    
    for i, result in enumerate(results, 1):
        if 'error' not in result:
            output += f"{i}. {result['title']}\n"
            output += f"   URL: {result['link']}\n"
            output += f"   {result['snippet'][:200]}\n\n"
    
    return output


def get_weather_no_api(city: str) -> str:
    """
    Get weather for a city without using API keys (web scraping).
    
    Args:
        city: City name
    
    Returns:
        Weather information
    """
    data = crawler.get_weather_from_web(city)
    
    if 'error' in data:
        return f"Could not get weather: {data['error']}"
    
    output = f"Weather for {data['city']}\n"
    output += f"Source: {data['source']}\n\n"
    
    if data.get('temperature'):
        output += f"Temperature: {data['temperature']}\n"
    
    if data.get('condition'):
        output += f"Condition: {data['condition']}\n"
    
    if data.get('humidity'):
        output += f"Humidity: {data['humidity']}\n"
    
    if data.get('wind'):
        output += f"Wind: {data['wind']}\n"
    
    if not data.get('temperature') and not data.get('condition'):
        output += "Could not extract detailed weather. Try searching for more specific info.\n"
    
    return output


def get_latest_news(topic: str = None, num_articles: int = 5) -> str:
    """
    Get latest news without using API keys.
    
    Args:
        topic: News topic (optional)
        num_articles: Number of articles
    
    Returns:
        News summary
    """
    query = f"latest news {topic}" if topic else "latest news today"
    articles = crawler.extract_news(topic=topic, num_articles=num_articles)
    
    if not articles or all('error' in a for a in articles):
        return "Could not fetch news. Try again later."
    
    output = f"Latest News{f' about {topic}' if topic else ''}\n"
    output += "=" * 50 + "\n\n"
    
    for i, article in enumerate(articles, 1):
        if 'error' not in article:
            output += f"{i}. {article['title']}\n"
            output += f"   {article['summary'][:150]}...\n"
            output += f"   Source: {article['source'][:60]}\n\n"
    
    return output


def get_stock_price_no_api(symbol: str) -> str:
    """
    Get stock price without using API keys.
    
    Args:
        symbol: Stock symbol (e.g., AAPL, GOOGL, TSLA)
    
    Returns:
        Stock price information
    """
    data = crawler.get_stock_price(symbol)
    
    if 'error' in data:
        return f"Could not get stock price: {data['error']}"
    
    output = f"Stock: {data['symbol']}\n"
    output += f"Source: {data['source']}\n\n"
    
    if data.get('price'):
        output += f"Price: {data['price']}\n"
    else:
        output += "Price: Could not extract\n"
    
    if data.get('change'):
        output += f"Change: {data['change']}\n"
    
    return output


def extract_product_details(url: str) -> str:
    """
    Extract product information from an e-commerce page.
    
    Args:
        url: Product page URL
    
    Returns:
        Product details
    """
    data = crawler.extract_product_info(url)
    
    if 'error' in data:
        return f"Could not extract product: {data['error']}"
    
    output = f"Product Information\n"
    output += "=" * 40 + "\n\n"
    output += f"Title: {data.get('title', 'N/A')}\n\n"
    
    if data.get('price'):
        output += f"Price: {data['price']}\n"
    
    if data.get('rating'):
        output += f"Rating: {data['rating']}\n"
    
    if data.get('availability'):
        output += f"Availability: {data['availability']}\n"
    
    output += f"\nDescription:\n{data.get('description', 'N/A')[:500]}"
    
    return output


def extract_faq_from_page(url: str) -> str:
    """
    Extract FAQ from a webpage.
    
    Args:
        url: Page URL containing FAQ
    
    Returns:
        FAQ content
    """
    faqs = crawler.extract_faq(url)
    
    output = f"FAQ from {url}\n"
    output += "=" * 40 + "\n\n"
    
    for i, faq in enumerate(faqs, 1):
        output += f"Q{i}: {faq['question']}\n"
        output += f"A{i}: {faq['answer']}\n\n"
    
    return output
