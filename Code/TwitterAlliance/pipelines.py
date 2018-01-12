# -*- coding: utf-8 -*-
import os

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


class TwitterAlliancePipeline(object):
    def process_item(self, item, spider):
        """
        Writes all the accounts list to a file.
        """

        EXPORT_FOLER = 'twitteralgo'

        fileDir = os.path.dirname(os.path.realpath('__file__'))

        with open(os.path.join(EXPORT_FOLER, item['filename']), "w") as export:
            for user in item['user_accounts']:
                export.write(user + '\n')

        return item
