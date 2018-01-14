# -*- coding: utf-8 -*-
import os

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


class TwCounterSpiderPipeline(object):
    def process_item(self, item, spider):
        """
        Writes all the accounts list to a file.
        """

        script_dir = os.path.dirname(__file__)  # absolute dir the script is in
        EXPORT_FILE = "../TwitterAlliance/top_users/%s" % item['filename']

        with open(os.path.join(script_dir, EXPORT_FILE), "w") as export:
            for user in item['user_accounts']:
                export.write(user + '\n')

        return item
