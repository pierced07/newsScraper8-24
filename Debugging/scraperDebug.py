import requests

#TO-DO LIST
#1. Create getTitles&Links(), getTime() functions and make sure entry variables are correct
#2. Create getTitles&Links() function. Make sure to go through a bunch of different websites to see what kind of entry variables I need

def getArticleList(list): #need to find article title and link first, then time. use concurrent features to find time
    fullArticleDict = {} #at end of category loop, creates a dictionary with 'World' type 1st layer and adds all sources with their respective articles

    for category, entries in list.items(): #first level {'World' : []}
        tempFullSourceList = [] #full list of source dictionarys in category
        
        for entry in entries: #second level [{'Source': 'BBC'}, {'Source': 'Reuters'}]
            response = requests.get(entry['URL'])
            tempArticleList = [] #list of article dictionarys. added to 'Source' dictionary or 2nd level
            tempSourceDict = {} #temporary dict for all 'Sources' in category. Appended at end of outer for loop to add list to 'World', or Category

            if response.status_code == 200:
                articles = getTitles&Links(entry['URL'], entry['Header'], entry['Class'], entry['Link']) #returns [{'Title', 'Link', 'Time': 'none'}]
                
                for article in articles:
                    article['Time'] = getTime(article['Link'], entry['Time'])
                    tempArticleList.append(article)
                tempSourceDict[entry['Source']] = tempArticleList #{'Source': []} append this to list of sources under category

            else:
                tempSourceDict[entry['Source']] = 'request error'

            tempFullSourceList.append(tempSourceDict) #adds all sources to source list


        fullArticleDict[category] = tempFullSourceList #adds all sources to category
                

    return fullArticleDict

mainList = {'World': [{'Source': 'BBC', 'URL': 'https://www.bbc.com/', 'Header': 'h4', 'Time': 'idk', 'Class': 'idk', 'Link': 'idk'}]} #header, time, class, link used to help functions
articleList = {'World': [{'Source': [{'Title': 'title', 'Time': 'time', 'Link': 'link'}]}]}

list = getArticleList(mainList)

print(list)

