# -*- coding: utf-8 -*-
"""
 ______       _ __  __          ___   _____
/_  __/    __(_) /_/ /____ ____/ _ | / / (_)__ ____  _______
 / / | |/|/ / / __/ __/ -_) __/ __ |/ / / / _ `/ _ \/ __/ -_)
/_/  |__,__/_/\__/\__/\__/_/ /_/ |_/_/_/_/\_,_/_//_/\__/\__/
________________________________________________________________________________

DESCRIPTION:
    Web spider for extracting the Twitter most followed accounts

AUTHORS:
    David Arroyo
    Adrián Camacho
    Paula Muñoz
    Carla Paola Peñarrieta

    Facultad de Informática - Universidad Complutense de Madrid

WHAT IT DOES:
    It extracts from TwitterCounter.com the 100 Twitter most followed accounts
    of a given country. It can also extracts the most followed accounts of a list
    of countries. The script exports the results inside the 'twitteralgo' folder.
"""
import scrapy

from items import TwCounterSpiderItem


class TwchartSpider(scrapy.Spider):
    name = 'twalliance'
    url = 'https://twittercounter.com/pages/100/'

    def start_requests(self):
        self.target_country = getattr(self, 'target_country', None)
        self.list_countries = getattr(self, 'list_countries', None)
        self.limit = int(getattr(self, 'limit', 100))
        self.filename = getattr(self, 'file', None)

        if self.target_country:
            # In this website web extract the country most famous users
            url = TwchartSpider.url + self.target_country
            request = scrapy.Request(url=url, callback=self.parse, errback=self.handle_error)
            request.meta['country'] = self.target_country

            yield request
        elif self.list_countries:

            for country in self.list_countries:
                url = TwchartSpider.url + country
                request = scrapy.Request(url=url, callback=self.parse, errback=self.handle_error)
                request.meta['country'] = country

                yield request

    def parse(self, response):
        my_selector = response.css("span[itemprop=alternateName]::text")
        tw_accounts = my_selector.extract()
        tw_accounts = tw_accounts[:self.limit]

        # Create an item
        users = TwCounterSpiderItem()
        users['user_accounts'] = tw_accounts  # pass the accounts list
        users['filename'] = self.filename
        users['country'] = response.meta['country']

        yield users  # send it to the pipelines (write it to a file)

    def handle_error(self, failure):
        if failure.check(HttpError):
            # these exceptions come from HttpError spider middleware
            # you can get the non-200 response
            response = failure.value.response
            print('HttpError on %s', response.url)

        elif failure.check(DNSLookupError):
            # this is the original request
            request = failure.request
            print.logger.error('DNSLookupError on %s', request.url)

        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            print('TimeoutError on %s', request.url)
