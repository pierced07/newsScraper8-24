import json
from datetime import datetime
import requests
from bs4 import BeautifulSoup

def get_time(soup):
    script_tag = soup.find('script', type='application/ld+json')

    if script_tag:
        try:
            json_ld_content = json.loads(script_tag.string) #puts everything into dictionary like thing
            if isinstance(json_ld_content, list): #checks to see if list
                for entry in json_ld_content:
                    if isinstance(entry, dict) and entry.get('@type') == 'NewsArticle':
                        date_published = entry.get('datePublished')
                        if date_published:
                            return date_published
                        else:
                            return 'none 1'
                    elif isinstance(entry, dict) and entry.get('@type') == 'WebPage':
                        date_published = entry.get('datePublished')
                        if date_published:
                            return date_published
                        else:
                            return 'none 1'
            elif isinstance(json_ld_content, dict): #checks to see if dict
                if json_ld_content.get('@type') == 'NewsArticle':
                    date_published = json_ld_content.get('datePublished')
                    if date_published:
                        return date_published
                    else:
                        return 'none 1'
                date_published = json_ld_content.get('datePublished')
                if not date_published:
                    # If datePublished is not found at the top level, check in @graph
                    for entry in json_ld_content.get('@graph', []):
                        if isinstance(entry, dict) and entry.get('@type') == 'NewsArticle':
                            date_published = entry.get('datePublished')
                            if date_published:
                                return date_published
                            else:
                                return 'none 1'
                        elif isinstance(entry, dict) and entry.get('@type') == 'WebPage':
                            date_published = entry.get('datePublished')
                            if date_published:
                                return date_published
                            else:
                                return 'none 1'
            else:
                return 'not dict or list'
        except json.JSONDecodeError:
            return 'none 1'

url = 'https://www.bbc.com/news/articles/c8xlq0rg4yzo'

response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

time = get_time(soup)
h = 'None'
print(time)
