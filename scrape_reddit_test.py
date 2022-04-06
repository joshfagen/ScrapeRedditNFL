#Import packages to use
import praw
from psaw import PushshiftAPI
import bs4 as bs
import pandas as pd
import datetime as dt

#Create Reddit instance
reddit = praw.Reddit(client_id = 'xGk-bzKpGwjnj1gPHpIaxQ', 
                     client_secret='lYdKaupR1btCWrst8uCg9R1mnpWw2g',
                     user_agent='Scrape Test')

api = PushshiftAPI(reddit)

#Scrape posts, arbitrarily set limit at 1200 (around start of 2020 season) 
gamedaythread_posts = api.search_submissions(author='nfl_gamethread', limit=1200)

#Initialize empty data array
data = []

#Setup counts
gameCount = 0
underCount = 0
overCount = 0
underdogCount = 0
favoriteCount = 0
gameDayThreadCount = 0

#Iterate through posts
for post in gamedaythread_posts:
    #Only post game threads
    gameDayThreadCount = gameDayThreadCount + 1
    print('Post #' + str(gameDayThreadCount))
    if(post.title[1] is 'o'):
        
        #Get Game Title, Time, increment game count
        gameCount = gameCount + 1
        print("GAME #: " + str(gameCount))
        print(post.title[18:] + " " + post.shortlink)
        dateCreated = dt.date.fromtimestamp(post.created)
        
        #Get structure of post
        soup = bs.BeautifulSoup(post.selftext_html, 'lxml')
        
        #Create list of all table cells
        tdList = soup.find_all('td')
        print('Td List Length - ' + str(len(tdList)))
        #For error-handling purposes
        if(len(tdList) < 17):
            print('Error, unable to parse')
            continue

        #Handle OT Games:
        if(len(tdList) is 34):
            #Get Home team and Score
            home = tdList[7].text
            homeScore = tdList[13].text

            #Get Away team and Score
            away = tdList[14].text 
            awayScore = tdList[20].text

        #Non-OT Games
        else:
            #Get Home team and Score
            home = tdList[6].text
            homeScore = tdList[11].text

            #Get Away team and Score
            away = tdList[12].text 
            awayScore = tdList[17].text

        #Get odds
        odds = soup.find_all('td', align="right")
        odds = odds[1].text
        if odds is '':
            print('No Odds Available!')
            continue
        #Get line, convert to float
        predictedLine = odds[:-8]
        if '+' in predictedLine:
            points = predictedLine[predictedLine.find('+') + 1:]
            points = float(points)
        else:
            points = predictedLine[predictedLine.find('-') + 1:]
            points = float(points) * -1

        #Get O/U
        predictedTotal = odds[odds.find('U') + 2:]
        
        #Get actual total, create empty overUnder variable
        actualTotal = int(homeScore) + int(awayScore)
        overUnder = ''

        #Print final score
        print(home + " " + homeScore + " " + away + " " + awayScore)
        
        #Print line create empty outcome variable
        print(predictedLine)
        outcome = ''
        
        #Assess and Print outcome against the spread, increment corresponding count
        print(str(points))
        if points > 0 :
            adjustedHomeScore = int(homeScore) + points
            if adjustedHomeScore > int(awayScore):
                print('Home underdog won at least after points adjustment')
                underdogCount = underdogCount + 1
                outcome = 'Underdog'
            else:
                print('Home underdog lost even with extra points')
                favoriteCount = favoriteCount + 1
                outcome = 'Favourite'
        else:
            adjustedHomeScore = int(homeScore) + points
            if adjustedHomeScore > int(awayScore):
                print('Home favorite won even ATS')
                favoriteCount = favoriteCount + 1
                outcome = 'Favorite'
            else:
                print('Home favorite lost, at least ATS')
                underdogCount = underdogCount + 1
                outcome = 'Underdog'
        
        #Assess and Print O/U outcome and increment corresponding count
        print("predicted O/U: " + predictedTotal + " actual total: " + str(actualTotal))
        if(float(predictedTotal) > actualTotal):
            print("Under")
            underCount = underCount + 1
            overUnder = 'Under'
        else:
            print("Over")
            overCount = overCount + 1
            overUnder = 'Over'

        data.append([post.shortlink, dateCreated, home, int(homeScore), away, int(awayScore), points,  outcome, predictedTotal, actualTotal, overUnder])
        print("------------------------------------------")

#Data Frame!
df = pd.DataFrame(data, columns = ['Link', 'Date Created', 'Home Team', 'Home Team Score', 'Away Team', 'Away Team Score', 'Points For Home Team', 
                                'Adjusted Winner', 'Predicted Total Points', 'Actual Total', 'Total Outcome'])

df.to_csv('table.csv')
print('Data Frame Size: ' + str(len(df)))    
with(pd.option_context('display.max_rows', None, 'display.max_columns', None)):    
    print(df.to_string())

#Print spread and O/U overall totals
print("------------------------------------------")
print("Games: " + str(gameCount))
print("Overs: " + str(overCount) + " Unders: " + str(underCount))
print("Favorites: " + str(favoriteCount) + " Underdogs: " + str(underdogCount))