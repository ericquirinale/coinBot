# coinBot
Discord Bot with crypto functionality
Add token to token.txt and install the required dependencies

$help for a list of commands

$price 'coin full-name' for a coins price

$search 'keyword' to search 4chan/biz for any posts containing that keyword

$watchlist 'add' 'coin full-name' to add a coin to the watchlist")

$watchlist 'remove' 'coin full-name' to remove a coin to the watchlist

$watchlist 'show' to show the watchlist

Coins on the watchlist get checked every hour, and if they have changed 1% or more in the last hour a message is sent.
Every hour a generic search is also run to search 4chan for any posts containing the words 'discord', 'ico', or 'airdrop'
