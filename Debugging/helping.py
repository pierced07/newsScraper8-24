import requests #used for contacting website
from bs4 import BeautifulSoup #used for parsint
from urllib.parse import urljoin #makes absolute URL
import os
import asyncio
import aiohttp

#TO-DO LIST - Use concurrent features for summarization. make sure i dont use too many threads
#1. Create getTitles&Links() function. Make sure to go through a bunch of different websites to see what kind of entry variables I need
#2. getTime() function.
#3. Make function to automatically add website to mainList

def getAllHeaders(link, response):
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "DNT": "1",  # Do Not Track request header
}
    header_tags = ["h1", "h2", "h3", "h4", "h5", "h6"]
    full_list = [] #full list of headers
    seen_headers = set()
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        for tag in header_tags:
            headers = soup.find_all(tag)
            if headers:
                for h in headers:
                    header = h.get_text(strip=True)
                    if header not in seen_headers:
                        full_list.append(header)
                        seen_headers.add(header)
    elif response.status_code != 200:
        response = requests.get(link, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            for tag in header_tags:
                headers = soup.find_all(tag)
                if headers:
                    for h in headers:
                        header = h.get_text(strip=True)
                        if header not in seen_headers:
                            full_list.append(header)
                            seen_headers.add(header)
    else:
        return 'header response error'

    return full_list

def getAllLinks(url, response): #uses brute force and only works for "https://www.bbc.com/", "https://www.washingtonpost.com/", "https://www.nytimes.com/", "https://www.wsj.com/", "https://www.ft.com/", "https://www.economist.com/"
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "DNT": "1",  # Do Not Track request header
}
   
    linkList = [] 
    seenLinks = set()

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a', href=True)
        for link in links: #makes list of absolute links
            linkLists = urljoin(url, link['href'])
            if linkLists not in seenLinks:
                if linkLists.startswith(url):
                    linkList.append(linkLists)
                    seenLinks.add(linkLists)
    else:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            links = soup.find_all('a', href=True)
            for link in links: #makes list of absolute links
                linkLists = urljoin(url, link['href'])
                if linkLists not in seenLinks:
                    if linkLists.startswith(url):
                        linkList.append(linkLists)
                        seenLinks.add(linkLists)

    return linkList

def getArticleList(list): #need to find article title and link first, then time. use concurrent features to find time
    fullArticleDict = {} #at end of category loop, creates a dictionary with 'World' type 1st layer and adds all sources with their respective articles

    for category, entries in list.items(): #first level {'World' : []}
        tempFullSourceList = [] #full list of source dictionarys in category
        
        for entry in entries: #second level [{'Source': 'BBC'}, {'Source': 'Reuters'}]
            response = requests.get(entry['URL'])
            tempSourceDict = {} #temporary dict for all 'Sources' in category. Appended at end of outer for loop to add list to 'World', or Category
            
            #!! Need to check to see if status_code == 200 down the line
            articles = getTitles_Links(entry['URL'], response) #returns [{'Title', 'Link', 'Time': 'time'}]                
            tempSourceDict[entry['Source']] = articles #{'Source': []} append this to list of sources under category
            #!! Implement else function to see if requests == 200 if not return request error

            tempFullSourceList.append(tempSourceDict) #adds all sources to source list


        fullArticleDict[category] = tempFullSourceList #adds all sources to category
                

    return fullArticleDict

def getTitles_Links(link, response): #returns a list of dictionaries [{'Title': 'title', 'Link': 'link', 'Time': 'none'}]. For now, use brute force
    links = getAllLinks(link, response) #uses brute force and only works for "https://www.bbc.com/", "https://www.washingtonpost.com/", "https://www.nytimes.com/", "https://www.wsj.com/", "https://www.ft.com/", "https://www.economist.com/"
    headers = getAllHeaders(link, response) #returns list of headers
    full_list = get_title_link_pair(links, headers, response)
    #use Asyncio + Aiohttp to get all titles and compare to headers. once we have pair, get time

    return [{'Title': 'link', 'Link': 'link', 'Time': 'time'}, {'Title': 'link', 'Link': 'link', 'Time': 'time'}]

def get_time(response):
    print()

def link_title(session, links, baseResponse): #returns [{"Title": 'none', "Link": 'none', "Time": 'none'}]
    dict_key = {"Title": 'none', "Link": 'none', "Time": 'none'}
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "DNT": "1",  # Do Not Track request header
    }

    tasks = []
    for link in links:
        if baseResponse == 200:
            response = requests.get(link)
            soup = BeautifulSoup(response.text, 'html.parser')
            title_tag = soup.find('title')
            if title_tag:
                title = title_tag.get_text(strip=True)
                temp = dict_key
                temp['Title'] = title
                temp['Link'] = link
                tasks.append(temp)
            return tasks

            #add to title, link list
            print()
        elif baseResponse != 200:
            print()
        print()

    return tasks

async def get_title_link_pair(links, headers, baseResponse): #returns 'Title': 'title', 'Time': 'time', 'Link': 'link'

    async with aiohttp.ClientSession() as session:
        full_list = link_title(session, links, baseResponse)
        responses = await asyncio.gather(*full_list)
        for response in responses:
            print()


"""Eventually, have a function that can determine which classes the article titles, links, and
maybe times are located. first, find all title link pairs through brute force i.e. getting the
title of every link on the main page and comparing it to every header on the main page to 
see if they match. Once i have this, get every single HTML class. If the class contains multiple
headers or links that match, move down a class level. Otherwise, if no headers or links are found,
move up a class level. Find the highest nested class that contains the header and maybe the link
and time and save that. By highest class, i mean that if you went up another class level, 
the class would contain multiple headers and maybe links. This may take a couple days to see if
the classes the headers and links are in change. If they do, then I just have to use brute force
to get all title link pairs."""
mainList = {'World': [{'Source': 'BBC', 'URL': 'https://www.bbc.com/'},
                      {'Source': 'Washington Post', 'URL': 'https://www.washingtonpost.com/'},
                      {'Source': 'FT', 'URL': 'https://www.ft.com/'}]} #header, time, class, link used to help functions
articleList = {'World': [{'Source': [{'Title': 'title', 'Time': 'time', 'Link': 'link'}]}]}

list = getArticleList(mainList)

print(list)

