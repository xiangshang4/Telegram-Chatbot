from iexfinance.refdata import get_symbols
from iexfinance.stocks import Stock
import requests
from datetime import date
import pandas as pd
import os

os.environ["IEX_API_VERSION"] = "iexcloud-beta"
os.environ['IEX_TOKEN'] = 'IEX_TOKEN'


def get_all_symbols():
    temp = get_symbols(output_format='pandas')
    # temp.to_excel("all available company.xlsx")
    return temp[['symbol', 'name']]


company_list = get_all_symbols()


def search_getPrice(name):
    df = company_list[company_list['name'].str.contains(name)]
    if len(df) == 0:
        return "I am sorry. I cannot find company with name {0}.\n".format(name)
    else:
        text = ""
        for index, row in df.iterrows():
            a = Stock(row.symbol)
            text += "Latest stock price of {0}:\n USD {1}\n".format(row['name'], a.get_quote()['latestPrice'])
        return text


def price(sentence):
    entities = sentence.ents
    if len(entities) == 0:
        return "Currently I don't understand."
    output = ""
    for ent in entities:
        output += search_getPrice(str(ent))
    return output


def description(companies):
    output = ''
    if len(companies) == 0:
        return "Which company are you looking for?"
    for i in companies:
        df = company_list[company_list['name'].str.contains(str(i))]
        a = Stock(df.iloc[0]['symbol'])
        output += "Industry: {0}\nWebsite: {1}\n{2}".format(a.get_company()['industry'], a.get_company()['website'],
                                                            a.get_company()['description'])
    return output


def get_news(companies):
    newsapi_key = 'news_api_TOKEN'
    news_source = ['Bloomberg', 'Reuters']
    output = []
    for i in companies:
        url = ('http://newsapi.org/v2/everything?'
               'q={0}&'
               'from={1}&'
               'sortBy=popularity&'
               'apiKey={2}'.format(str(i), str(date.today()), newsapi_key))
        response = requests.get(url)
        for news in response.json()['articles']:
            if news['author'] in news_source or news['source']['name'] in news_source:
                output.append(news['url'])
    return output
