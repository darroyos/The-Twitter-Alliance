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

    try:
        opts, args = getopt.getopt(argv, "c:", ["country=", ])
    except getopt.GetoptError:
        print(logo)
        sys.exit(1)
    for opt, arg in opts:
        if opt in ("-c", "--country"):
            target_country = arg

    if target_country:
        print(logo)
        filename = 'Top100_%s.txt' % target_country
        start_twchart(target_country, filename)


def start_twchart(target_country, filename):
    configure_logging()
    process = CrawlerProcess(get_project_settings())

    process.crawl('twalliance', country=target_country, file=filename)
    process.start()


if __name__ == "__main__":
    main(sys.argv[1:])
