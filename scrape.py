from bs4 import BeautifulSoup
import requests
import basc_py4chan
import discord
import asyncio
from apscheduler.schedulers.background import BackgroundScheduler

#read token from file
token = open("token.txt","r").read()

#searches every hour
scheduler = BackgroundScheduler()

#event loop
loop = asyncio.get_event_loop()

#discord client
client = discord.Client()
#coin watchlist
watchlist = []

#manually returns price of coin
def getPrice(ticker):
    page = requests.get('https://www.coingecko.com/en/coins/'+ticker)
    if(page.status_code == 404):
        return "Error, ticker not found. Use full coin name."
    else:
        soup = BeautifulSoup(page.text, 'html.parser')
        return soup.find('span', class_="no-wrap").text.strip()

#manual search functionality
def findKeywords(keyWord):
    board = basc_py4chan.Board('biz')
    all_thread_ids = board.get_all_thread_ids()
    i=0
    links = []
    for thread in all_thread_ids:
        thread = board.get_thread(all_thread_ids[i])
        if keyWord.lower() in thread.topic.text_comment.lower():
            links.append("https://boards.4channel.org/biz/thread/"+str(thread.topic.post_id))
        i=i+1
    return links

#search that gets run every hour to check for keywords
def autoSearch():
    newcoinalert = client.get_channel(729875530643406848)
    discordSearch = findKeywords("discord")
    ico = findKeywords("ico")
    airdrop = findKeywords("airdrop")
    for element in ico:
        if element not in discordSearch:
            discordSearch.append(element)
    for element2 in airdrop:
        if element2 not in discordSearch:
            discordSearch.append(element2)
    if len(discordSearch) > 0:
        loop.create_task(sendMessage("Here are the posts containing the keywords, discord, ico, and airdrop I found in the last hour", newcoinalert))
    #await newcoinalert.send("Here are the posts containing the keywords, discord, ico, and airdrop I found in the last hour")
    for element3 in discordSearch:
        loop.create_task(sendMessage(element3, newcoinalert))
        #await newcoinalert.send(element3)

#adding and taking coins off of the watchlist
def coinWatchlist(action, coin):
    contains = False
    if action == 'add':
        for elements in watchlist:
            if coin == elements:
                contains = True
        if contains == False:
            testPage = requests.get('https://www.coingecko.com/en/coins/'+coin)
            if(testPage.status_code == 404):
                return False
            else:
                watchlist.append(coin)
                return True
    if action == 'remove':
        watchlist.remove(coin)
        return True

#gets run every hour and checks watchlist
def coinWatchlistAlert():
    main = client.get_channel(729824001219887158)
    for coins in watchlist:
        print(coins)
        page = requests.get('https://www.coingecko.com/en/coins/'+coins)
        if(page.status_code == 404):
            #await main.send("Error, ticker '" + coins + "' not found. Use full coin name and update the watchlist.")
            loop.create_task(sendMessage("Error, ticker '" + coins + "' not found. Use full coin name and update the watchlist.", main))
        else:
            soup = BeautifulSoup(page.text, 'html.parser')
            div = soup.find_all('div', class_="row text-center")
            hourChange = float(div[1].span.text.strip()[:-1])
            if hourChange > 1.0 or hourChange < -1.0:
                #await main.send(coins + " set off a new alert! It's changed " + str(hourChange)+ "% in the last hour")
                loop.create_task(sendMessage(coins + " set off a new alert! It's changed " + str(hourChange)+ "% in the last hour", main))

#send message
async def sendMessage(message, channel):
    await channel.send(message)

#everytime a message is sent in discord
@client.event
async def on_message(message):
    arg = message.content[7:]
    if message.author == client.user:
        return

    if message.content.startswith('$price'):
        async with message.channel.typing():
            await message.channel.send(getPrice(arg))

    if message.content.startswith('$search'):
        async with message.channel.typing():
            links = findKeywords(arg)
            if(len(links)==0):
                await message.channel.send("No posts matching '"+arg+ "' were found")
            for item in links:
                await message.channel.send(item)

    if message.content.startswith('$help'):
        await message.channel.send("$price 'coin full-name' for a coins price")
        await message.channel.send("$search 'keyword' to search 4chan/biz for any posts containing that keyword")
        await message.channel.send("$watchlist 'add' 'coin full-name' to add a coin to the watchlist")
        await message.channel.send("$watchlist 'remove' 'coin full-name' to remove a coin to the watchlist")
        await message.channel.send("$watchlist 'show' to show the watchlist")

    if message.content.startswith('$watchlist'):

        #gets keyword after $watchlist
        function = message.content[11:]
        #gets coin after $watchlist add
        coinAdd = message.content[15:]
        #gets coin after $watchlist remove
        coinSub = message.content[18:]

        if function.startswith('add'):
            success = coinWatchlist("add", coinAdd)
            if success == True:
                await message.channel.send(coinAdd+" was successfully added to the watchlist")
            else:
                await message.channel.send("Error "+ coinAdd +" couldn't be added to the watchlist. Make sure you use the full coin name. ")
        if function.startswith('remove'):
            coinWatchlist("remove", coinSub)
            await message.channel.send("Elements in watchlist: ")
            for elements in watchlist:
                await message.channel.send(elements)

        if function.startswith('show'):
            await message.channel.send("Elements in watchlist: ")
            for elements in watchlist:
                await message.channel.send(elements)

#on login
@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')  # notification of login.

#scheduler to run autsearch and coinwatch every hour
scheduler.add_job(autoSearch, 'interval', hours=1)
scheduler.add_job(coinWatchlistAlert, 'interval', hours=1)
scheduler.start()

client.run(token)
