# -*- coding: utf-8 -*-

import sys
import getopt
import scrapy

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy.utils.log import configure_logging

logo = '''
*********************************************************************
*    ______       _ __  __          ___   _____                     *
*   /_  __/    __(_) /_/ /____ ____/ _ | / / (_)__ ____  _______    *
*    / / | |/|/ / / __/ __/ -_) __/ __ |/ / / / _ `/ _ \/ __/ -_)   *
*   /_/  |__,__/_/\__/\__/\__/_/ /_/ |_/_/_/_/\_,_/_//_/\__/\__/    *
*                                                                   *
*                               MADE IN                             *
*                                   Facultad de Informática UCM     *
*********************************************************************
*      Map the relationships between the most followed accounts     *
*********************************************************************
'''


def main(argv):
    target_country = None
    list_countries = None
    limit = None

    try:
        opts, args = getopt.getopt(argv, "c:l:", ["country=", "lcountry=", "limit=", ])
    except getopt.GetoptError:
        print(logo)
        sys.exit(1)
    for opt, arg in opts:
        if opt in ("-c", "--country"):
            target_country = arg
        if opt in ("--lcountry"):
            list_countries = arg
        if opt in ("-l", "--limit"):
            limit = arg

    if target_country:
        print(logo)

        if not limit:
            limit = 100

        filename = 'Top%s_%s.txt' % (limit, target_country)
        start_twchart(target_country=target_country, limit=limit, filename=filename)

    elif list_countries:
        list_countries = list_countries.split()
        print(list_countries)
        if not limit:
            limit = 20

        # Building the filename with the countries initial letter
        countries = ''
        for country in list_countries:
            countries += country[:3] + '_'

        filename = 'Top%s_%s.txt' % (limit, countries)

        start_twchart(list_countries=list_countries, limit=limit, filename=filename)


def start_twchart(limit, filename, target_country=None, list_countries=None):
    configure_logging()
    process = CrawlerProcess(get_project_settings())

    process.crawl('twalliance', target_country=target_country, list_countries=list_countries, limit=limit, file=filename)
    process.start()


if __name__ == "__main__":
    main(sys.argv[1:])
