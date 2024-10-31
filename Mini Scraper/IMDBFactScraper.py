from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
import argparse



parser = argparse.ArgumentParser(description='Search IMDB and find 3 facts')
parser.add_argument('--name', type = str, required=True, 
                    help = 'Movie name')

args = parser.parse_args()


try:
    
    link = "https://www.imdb.com/find/?s=tt&q=" + args.name

    driver = webdriver.Firefox()
    sleep(3)

    driver.get(link)

    sleep(2)


    searchResults = driver.find_element(By.XPATH, "/html/body/div[2]/main/div[2]/div[3]/section/div/div[1]/section[2]/div[2]")
    movies = searchResults.find_elements(By.TAG_NAME, "a")

    driver.get(movies[0].get_attribute("href"))

    sleep(2)

    name = driver.find_element(By.XPATH, "/html/body/div[2]/main/div/section[1]/section/div[3]/section/section/div[2]/div[1]/h1/span")
    print(name.text)


    fact1 = driver.find_element(By.XPATH, "/html/body/div[2]/main/div/section[1]/section/div[3]/section/section/div[3]/div[2]/div[1]/section/div[2]/div/ul/li[1]/div/ul/li/a")
    print(f"Director or Creator: {fact1.text}")

    fact2 = driver.find_element(By.XPATH, "/html/body/div[2]/main/div/section[1]/section/div[3]/section/section/div[2]/div[1]/ul/li[3]")
    print(f"Run time: {fact2.text}")

    fact3 = driver.find_element(By.XPATH, "/html/body/div[2]/main/div/section[1]/section/div[3]/section/section/div[2]/div[2]/div/div[1]/a/span/div/div[2]/div[1]/span[1]")
    print(f"IMDB rating: {fact3.text}/10")


    driver.quit()

except:
    print("Movie not found")



"""
tiko@Tikos-MacBook-Pro COMP_467 % /usr/local/bin/python3 "/Users/tiko/Documents/GitHub/COMP_467/Mini Scraper/IMDBFactScraper.py" --name "The Dark Knight"  
Director or Creator: Christopher Nolan
Run time: 2h 32m
IMDB rating: 9.0/10
"""