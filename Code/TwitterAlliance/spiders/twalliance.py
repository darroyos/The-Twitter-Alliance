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
    of a given country. If it isn't given any country it just extracts the
    worldwide top 100. The script exports the results inside the 'twitteralgo'
    folder.
"""
import scrapy

from items import TwitterAllianceItem


class TwchartSpider(scrapy.Spider):
    name = 'twalliance'

    def start_requests(self):
        self.country = getattr(self, 'country', 'global')
        self.filename = getattr(self, 'file', None)

        # In this website web extract the country most famous users
        url = 'https://twittercounter.com/pages/100/%s' % self.country

        yield scrapy.Request(url=url, callback=self.parse, errback=self.handle_error)

    def parse(self, response):
        my_selector = response.css("span[itemprop=alternateName]::text")
        tw_accounts = my_selector.extract()

        # Create an item
        users = TwitterAllianceItem()
        users['user_accounts'] = tw_accounts  # pass the accounts list
        users['filename'] = self.filename

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
