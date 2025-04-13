from bs4 import BeautifulSoup
import requests

class WebScraperTool:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }

    def scrape(self, url, selector=None):
        try:
            response = self.session.get(url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            if selector:
                elements = soup.select(selector)
                return [element.text.strip() for element in elements]
            return soup.get_text()
            
        except requests.RequestException as e:
            print(f"Error scraping {url}: {str(e)}")
            return None

    def scrape_multiple(self, urls, selector=None):
        results = {}
        for url in urls:
            results[url] = self.scrape(url, selector)
        return results
