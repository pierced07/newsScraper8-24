import requests #used for contacting website
from bs4 import BeautifulSoup #used for parsint
from urllib.parse import urljoin #makes absolute URL
import os
import asyncio
import aiohttp

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "DNT": "1",  # Do Not Track request header
    }

#BBC 'title' headers, WP 'title', NYT 'h1, 

url = 'https://www.wsj.com/world/as-ukraine-invades-russia-kyivs-troops-are-in-trouble-on-the-eastern-front-8a7b1686?mod=hp_lead_pos1'
response = requests.get(url)

soup = BeautifulSoup(response.text, 'html.parser')

if response.status_code == 200:
    h1_tag = soup.find('title')
    if h1_tag:
        title = h1_tag.get_text(strip=True)
        print('title')
    else:
        h1_tag = soup.find('h1')
        title = h1_tag.get_text(strip=True)
        print('h1')
else:
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    h1_tag = soup.find('h1')
    print('h1')
    #title = h1_tag.get_text(strip=True)

#title = title_tag.get_text(strip=True)

print(response.status_code)
