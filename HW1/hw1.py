from bs4 import BeautifulSoup
from time import sleep
import requests
from random import randint
import csv
import time
import json
import urllib.parse

USER_AGENT = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'}

class SearchEngine:
    
    def load_queries(fileName):
        with open(fileName, "r") as f:
            queries = [query.strip() for query in f.read().splitlines()]
        return queries


    def perform_duckduckgo_search(queries):
        duckduckResults = {}
        for i, query in enumerate(queries, start=1):
            duckduckResults[query] = SearchEngine.search(query)
        
            if i % 5 == 0:
                delay = randint(10, 100)
                print(f"Sleeping for {delay} seconds after {i} queries...")
                time.sleep(delay)
    
        return duckduckResults    


    def search(query):
        temp_url = '+'.join(query.split())  
        url = 'https://www.duckduckgo.com/html/?q=' + temp_url
        soup = BeautifulSoup(requests.get(url, headers=USER_AGENT).text, "html.parser")
        newResults = SearchEngine.scrape_search_result(soup)
        return newResults
 
    def scrape_search_result(soup):
        rawResults = soup.find_all("a", attrs={"class": "result__a"})
        duckduckResults = []
        
        for result in rawResults[:10]:  
            link = result.get('href')
            cleanedLink = SearchEngine.cleanURL(link)
            if cleanedLink and cleanedLink not in duckduckResults:  
                duckduckResults.append(cleanedLink)
                print(cleanedLink)
        return duckduckResults

    def cleanURL(url):
        if url.startswith("//duckduckgo.com/l/?uddg="):
            decodedURL = urllib.parse.unquote(url.split("uddg=")[1])
            cleanURL = decodedURL.split('&')[0]
            return cleanURL
        return url

    def save_results_to_json(results, fileName):
        with open(fileName, "w") as f:
            json.dump(results, f, indent=4)

    def cleanLinks(link):
        x = link.lower().rstrip(" /").replace("www.", "").replace("https://", "").replace("http://", "").replace(".aspx", "")
        print(x)
        return x

    def writeCSV(queryStatistics,totalOverlaps,totalPercent,totalRHO,queries):
        with open("hw1.csv", "w", newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Queries", "No of Overlapping Results", "Percent Overlap", "Spearman Coefficient"])
            writer.writerows(queryStatistics)
            writer.writerow(["Averages", "Average No.of Overlapping Results","Average Percent Overlap", "Average Spearman Coefficient"])   
            writer.writerow([" ", totalOverlaps/len(queries),(totalPercent/len(queries))* 100, totalRHO/len(queries)])
            print(f"No of Queries are {len(queries)}")        

    def calculate_statistics(queries, duckduckResults, googleResults):
        queryStatistics = []
        totalOverlaps, totalPercent, totalRHO = 0, 0, 0

        for ids, query in enumerate(queries):
            queryLinks = duckduckResults[query]
            googleLinks = googleResults[query]

            queryLinksMap = {}
            for pos, val in enumerate(queryLinks):
                val = SearchEngine.cleanLinks(val)
                queryLinksMap[val] = pos

            overlaps, sum = 0, 0
            matchingOverlap = False
            for pos, val in enumerate(googleLinks):
                val = SearchEngine.cleanLinks(val)
                if val in queryLinksMap:
                    overlaps += 1
                    sum += (pos - queryLinksMap[val]) ** 2
                    if pos == queryLinksMap[val]:
                        matchingOverlap = True
                    else:
                        matchingOverlap = False

            if overlaps == 0:
                rho = 0
            elif overlaps == 1:
                rho = 1 if matchingOverlap else 0
            else:
                rho = 1 - ((6 * sum) / (overlaps * (overlaps ** 2 - 1)))

            queryStatistics.append([f"Query{ids + 1}", overlaps, (overlaps / len(googleLinks)) * 100, rho])
            totalOverlaps += overlaps
            totalPercent += overlaps / len(googleLinks)
            totalRHO += rho

        return queryStatistics, totalOverlaps, totalPercent, totalRHO



def main():
    queries = SearchEngine.load_queries("queryset.txt")

    duckduckResults = SearchEngine.perform_duckduckgo_search(queries)
    
    SearchEngine.save_results_to_json(duckduckResults, "hw1.json")

    with open("Google_Result4.json", "r") as file:
        googleResults = json.load(file)

    queryStatistics, totalOverlaps, totalPercent, totalRHO = SearchEngine.calculate_statistics(queries, duckduckResults, googleResults)

    SearchEngine.writeCSV(queryStatistics,totalOverlaps,totalPercent,totalRHO,queries)    

if __name__ == "__main__":
    main()
