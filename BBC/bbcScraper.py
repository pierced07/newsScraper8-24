import requests
from bs4 import BeautifulSoup #used for parsint
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed
from tkinter import *
import tkinter as tk
from tkinter import messagebox
from transformers import pipeline, BartTokenizer

tokenizer = BartTokenizer.from_pretrained("facebook/bart-large-cnn")
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def getAllLinks(url, response): #uses brute force and only works for "https://www.bbc.com/", "https://www.washingtonpost.com/", "https://www.nytimes.com/", "https://www.wsj.com/", "https://www.ft.com/", "https://www.economist.com/"
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "DNT": "1",  # Do Not Track request header
}
   #just a test
    linkList = [] 
    seenLinks = set()

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a', href=True)
        for link in links: #makes list of absolute links
            linkLists = urljoin(url, link['href'])
            if linkLists not in seenLinks:
                if linkLists.startswith(url):
                    if '/article' in linkLists:
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
                        if '/article' in linkLists:
                            linkList.append(linkLists)
                            seenLinks.add(linkLists)

    return linkList

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

def fetchTitle(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check if the request was successful
        soup = BeautifulSoup(response.text, 'html.parser')

        # Assuming the title is within the <title> tag
        title_tag = soup.find('h1')
        title = title_tag.get_text(strip=True) if title_tag else None
        
        return url, title
    except Exception as e:
        return url, None

def match_titles(links, headers):
    matched_titles = {}

    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(fetchTitle, url): url for url in links}

        for future in as_completed(future_to_url):
            url, title = future.result()
            if title:
                for header in headers:
                    if title == header:
                        matched_titles[title] = url
                        break

    return matched_titles

def count_tokens(text):
    """Counts the number of tokens in the text using the BART tokenizer."""
    tokens = tokenizer.encode(text, return_tensors="pt")
    return tokens.shape[1]

def chunk_text(text, max_tokens=1024, min_chunk_tokens=500):
    """Splits text into chunks that are within the max token limit and handles short chunks."""
    sentences = text.split('. ')
    chunks = []
    current_chunk = []
    current_length = 0

    for sentence in sentences:
        sentence_length = count_tokens(sentence)
        if current_length + sentence_length <= max_tokens:
            current_chunk.append(sentence.strip())
            current_length += sentence_length
        else:
            if current_length >= min_chunk_tokens:
                chunks.append('. '.join(current_chunk).strip() + '.')
            current_chunk = [sentence.strip()]
            current_length = sentence_length

    if current_chunk:
        last_chunk = '. '.join(current_chunk).strip() + '.'
        if count_tokens(last_chunk) < min_chunk_tokens:
            if chunks:
                previous_chunk = chunks.pop()
                combined_chunk = previous_chunk + ' ' + last_chunk
                while count_tokens(combined_chunk) > max_tokens:
                    split_point = len(combined_chunk.split()) // 2
                    chunks.append(' '.join(combined_chunk.split()[:split_point]))
                    combined_chunk = ' '.join(combined_chunk.split()[split_point:])
                chunks.append(combined_chunk)
            else:
                chunks.append(last_chunk)
        else:
            chunks.append(last_chunk)

    return chunks

class article_selector:
    def __init__(self, root, articles):
        self.root = root
        self.selected_articles = []
        self.articles = articles
        
        # Create a Listbox to display the titles
        self.listbox = tk.Listbox(root, selectmode=tk.MULTIPLE, width=80, height=20)
        self.listbox.pack(pady=20)
        
        # Insert the article titles into the Listbox
        for title in self.articles.keys():
            self.listbox.insert(tk.END, title)
        
        # Buttons to add selection and finish selection
        self.add_button = tk.Button(root, text="Add to Selection", command=self.add_selection)
        self.add_button.pack(pady=10)
        
        self.done_button = tk.Button(root, text="Done", command=self.show_selected_articles)
        self.done_button.pack(pady=10)

        # Text widget to display the selected article content
        self.text_widget = tk.Text(root, wrap=tk.WORD, width=80, height=20)
        self.text_widget.pack(pady=20)

    def add_selection(self):
        selected_indices = self.listbox.curselection()
        for i in selected_indices:
            article_title = self.listbox.get(i)
            if article_title not in self.selected_articles:
                self.selected_articles.append(article_title)
        
        messagebox.showinfo("Selection", "Articles added to your selection.")

    def show_selected_articles(self):
        if not self.selected_articles:
            messagebox.showwarning("No Selection", "No articles selected.")
            return
        
        self.text_widget.delete(1.0, tk.END)  # Clear the Text widget before displaying new content

        for title in self.selected_articles:
            url = self.articles[title]
            article_text = self.fetch_article_summary(url)
            self.text_widget.insert(tk.END, f"Title: {title}\n{article_text}\n{'-'*50}\n")

    def fetch_article_summary(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            paragraphs = soup.find_all('p')
            article_text = "\n".join(p.get_text() for p in paragraphs)

            chunks = chunk_text(article_text)
            
            summary = []
            for chunk in chunks:
                chunk_summary = summarizer(chunk, max_length=150, min_length=30, do_sample=False)
                summary.append(chunk_summary[0]['summary_text'].strip())

            final_summary = ' '.join(summary)
            return final_summary           

            #return summary[0]['summary_text']
        except Exception as e:
            return f"Failed to fetch article: {e}"

def main():
    url = 'https://www.bbc.com/'
    response = requests.get(url)

    if response.status_code == 200:
        links = getAllLinks(url, response)
        headers = getAllHeaders(url, response)
        matched = match_titles(links, headers)

        root = tk.Tk()
        app = article_selector(root, matched)
        root.mainloop()
    else:
        print(f"Failed to fetch {url}. Status code: {response.status_code}")
    
if __name__ == "__main__":
    main()
