import requests
from datetime import *
import re
from twilio.rest import Client


def cleanhtml(raw_html):
    cleantext = re.sub(CLEANR, '', raw_html)
    return cleantext


STOCK_NAME = "TSLA"
COMPANY_NAME = "Tesla Inc"
CLEANR = re.compile('<.*?>')
STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"
STOCK_API_KEY = 'YOUR STOCK API KEY'
NEWS_API_KEY = 'YOUR NEWS API KEY'

# take yesterday's and before yesterdays dates
yesterday = datetime.now().date() - timedelta(days=1)
before_yesterday = yesterday - timedelta(days=1)

# parsing stock prices
parameters = {'function': 'TIME_SERIES_DAILY',
              'symbol': STOCK_NAME,
              'apikey': STOCK_API_KEY
              }
stock_response = requests.get(url=STOCK_ENDPOINT, params=parameters)
stock_response.raise_for_status()
data = stock_response.json()
datelist = [key for key in data['Time Series (Daily)'].keys()]

# calculating price change between given dates
yesterday_price = float(data['Time Series (Daily)'][datelist[0]]['4. close'])
before_yesterday_price = float(data['Time Series (Daily)'][datelist[1]]['4. close'])

price_change = "{:.2f}".format(abs(yesterday_price / before_yesterday_price - 1)*100)

# parsing news articles
news_params = {
    'q': COMPANY_NAME,
    'from': before_yesterday,
    'sortBy': 'popularity',
    'apiKey': NEWS_API_KEY
}
# Gets 3 most relevant news articles and created a list with 3 dictionaries
news_response = requests.get(url=NEWS_ENDPOINT, params=news_params)
news_response.raise_for_status()
news_data = news_response.json()
message_text = []
for article in news_data['articles'][:3]:
    message_text.append({cleanhtml(article['title']): cleanhtml(article['description'])})

# Twilio message sender
account_sid = 'YOUR TWILIO ID'
auth_token = 'YOUR TWILIO TOKEN'

for message in message_text:
    for key, value in message.items():
        if yesterday_price > before_yesterday_price:
            symbol = '🔺'
        else:
            symbol = '🔻'
        client = Client(account_sid, auth_token)
        message = client.messages \
            .create(
                body=f"TESLA: {symbol}{price_change}%\nHeadline: {key}\nBrief: {value}",
                from_='TWILIO NUMBER',
                to='YOUR NUMBER')
        print(message.status)
