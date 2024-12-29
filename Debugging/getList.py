import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import concurrent.futures
import json
from datetime import datetime
import pytz
import re
timeZone = "US/Central" #sets timezone used in armyTime def

def findTime(url): #uses armyTime to return MM/DD 00:00 format
    headers = { #sets the user-agent header to mimic request from web browser
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 403: #403 = forbidden
        return 403

    html_content = response.content.decode('utf-8') #decodes response content
    soup = BeautifulSoup(html_content, 'html.parser')

    script_tag = soup.find('script', type='application/ld+json')
    if script_tag:
        try:
            json_ld_content = json.loads(script_tag.string) #puts everything into dictionary like thing
            if isinstance(json_ld_content, list): #checks to see if list
                for entry in json_ld_content:
                    if isinstance(entry, dict) and entry.get('@type') == 'NewsArticle':
                        date_published = entry.get('datePublished')
                        if date_published:
                            try:
                                return armyTime(date_published, timeZone)
                            except ValueError:
                                return 'none 1'
                    elif isinstance(entry, dict) and entry.get('@type') == 'WebPage':
                        date_published = entry.get('datePublished')
                        if date_published:
                            try:
                                return armyTime(date_published, timeZone)
                            except ValueError:
                                return 'none 1'
            elif isinstance(json_ld_content, dict): #checks to see if dict
                if json_ld_content.get('@type') == 'NewsArticle':
                    date_published = json_ld_content.get('datePublished')
                    if date_published:
                        try:
                            return armyTime(date_published, timeZone)
                        except ValueError:
                            return 'none 1'
                date_published = json_ld_content.get('datePublished')
                if not date_published:
                    # If datePublished is not found at the top level, check in @graph
                    for entry in json_ld_content.get('@graph', []):
                        if isinstance(entry, dict) and entry.get('@type') == 'NewsArticle':
                            date_published = entry.get('datePublished')
                            if date_published:
                                try:
                                    return armyTime(date_published, timeZone)
                                except ValueError:
                                    return 'none 1'
                        elif isinstance(entry, dict) and entry.get('@type') == 'WebPage':
                            date_published = entry.get('datePublished')
                            if date_published:
                                try:
                                    return armyTime(date_published, timeZone)
                                except ValueError:
                                    return 'none 1'
            else:
                return 'not dict or list'
        except json.JSONDecodeError:
            return 'none'
        
    meta_tag = soup.find('meta', itemprop='datePublished') #if not in <script>
    if meta_tag:
        # Get the content attribute
        date_published = meta_tag.get('content')
        if date_published:
            try:
                return armyTime(date_published, timeZone)
            except ValueError:
                return 'none 1'
    return 'none 1'

def armyTime(baseTime, localTimezone): #none 2
    formats = [ #different possible raw time formats
            "%Y-%m-%dT%H:%M:%S.%fZ",   # ISO 8601 with milliseconds (UTC)
            "%Y-%m-%dT%H:%M:%SZ",      # ISO 8601 without milliseconds (UTC)
            "%Y-%m-%dT%H:%M:%S%z",     # ISO 8601 with timezone
            "%Y-%m-%dT%H:%M:%S",       # ISO 8601 without timezone
            "%Y-%m-%dT%H:%M",          # ISO 8601 without seconds
            "%B %d, %Y",               # "August 1, 2024"
            "%B %d, %Y %I:%M %p",      # "August 1, 2024 6:29 PM"
            "%Y-%m-%dT%H:%M:%S%z"      # "2024-08-01T16:57:00-06:00"
        ]
    correctFormat = None
    try:
        for fmt in formats:
            try:
                date_object = datetime.strptime(baseTime, fmt)
                correctFormat = fmt
                break
            except ValueError:
                continue #checks to see if format is correct
    except ValueError:
        return 'none 2'

    if correctFormat:
        # Set the timezone for the parsed time to UTC if needed
        if 'Z' in correctFormat or '%z' in correctFormat:
            date_object = date_object.replace(tzinfo=pytz.UTC)

        # Convert the time to the specified local timezone
        local_time = date_object.astimezone(pytz.timezone(localTimezone))

        # Format the time as "MM/DD 00:00" in 24-hour time
        formatted_time = local_time.strftime("%m/%d %H:%M")

        return formatted_time
    else:
        return 'none 3'

def getTitle(url): #used for bbc.com to find title in article URL
    response = requests.get(url, timeout=5)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text(strip=True)
            return title

def getListBBC(url, response): #returns list of dictionarys. element 1 is base 
    
    response = requests.get(url)
    linkDictionary = {"Title": 'none', "Link": 'none', "Time": 'none'} #dictionary key
    fullList = [] #main list that gets returned
    linkList = [] 
    seenLinks = set()
    fullList.append(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a', href=True)
        for link in links: #makes list of absolute links
            linkLists = urljoin(url, link['href'])
            if linkLists not in seenLinks:
                if linkLists.startswith("https://www.bbc.com"):
                    if '/article' in linkLists:
                        linkList.append(linkLists)
                        seenLinks.add(linkLists)
                    else:
                        continue
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_url = {executor.submit(getTitle, link): link for link in linkList}
            future_to_time = {executor.submit(findTime, link): link for link in linkList}
            titles = {future_to_url[future]: future.result() for future in concurrent.futures.as_completed(future_to_url)}
            times = {future_to_time[future]: future.result() for future in concurrent.futures.as_completed(future_to_time)}

            for link in linkList:
                title = titles.get(link, 'none')
                time = times.get(link, 'none')
                if title:
                    temp = linkDictionary.copy()
                    temp["Title"] = title
                    temp["Link"] = link
                    temp["Time"] = time
                    fullList.append(temp)

        return fullList

def getList(url): #returns complete list of dictionarys 
    response = requests.get(url)
    if response.status_code == 200: #saves time if URL not valid
        finalList = ()
        if url.startswith("https://www.bbc.com"):
            return getListBBC(url, response)

def printList(list):#prints full list of dictionarys with first element the base URL
    print(list[0])
    print()
    for n in list[1:]:
        print(n["Title"])
        print(n["Link"])
        print(n["Time"])
        print()

url = "https://www.bbc.com"
list = getList(url)

printList(list)