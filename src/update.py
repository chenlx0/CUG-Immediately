# -*- coding: utf-8 -*-

import os
import MySQLdb
import datetime
import configparser
import requests
from bs4 import BeautifulSoup
from time import sleep


def get_mysql_info():
    """
    Get MySQL configure information from "spider.conf"
    return a dict contains host, password, user and database name(dbname)
    """
    config = configparser.ConfigParser()
    config.read("../spider.conf")
    mysql_info = dict(config["mysqld"])
    return mysql_info


class CrawlBase(object):
    """
    Base object for Crawling object
    """
    def __init__(self, url, encoding="utf-8"):
        self.url = url
        source = requests.get(url)
        source.encoding = encoding
        self.soup = BeautifulSoup(source.text, "html.parser")


class SpiderNet(object):
    def __init__(self):
        sql_dict = get_mysql_info()

        # These two class are used for connecting mysql server
        self.db = MySQLdb.connect(host=sql_dict["host"], user=sql_dict["user"], port=int(sql_dict["port"]),
                                  password=sql_dict["password"], db=sql_dict["dbname"])
        self.db.set_character_set('utf8')
        self.cursor = self.db.cursor()
        # self.cursor.execute('SET NAMES utf8;')
        # self.cursor.execute('SET CHARACTER SET utf8;')

        # Store function objects in a list
        # And count the number of function objects
        self.function_list = []

    def insert_data(self, info_dict):
        """
        Insert data in dictionary format to database
        """
        grab_time = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        sql = """INSERT INTO CUG_SPIDER_INFO(TITLE,
        UNIT, SITE_URL, LINK, GRAB_TIME, ABSTRACT, CATEGORY)
        VALUES ("%s", "%s", "%s", "%s", "%s", "%s", "%s")""" \
              % (info_dict["title"], info_dict["unit"],
                 info_dict["site_url"], info_dict["link"],
                 grab_time, info_dict["abstract"], info_dict["category"])

        self.cursor.execute(sql)
        self.db.commit()

    def refresh_confirm(self, info_dict):
        """
        return bool type object
        confirm if the same data had been inserted to database
        """
        sql = "SELECT TITLE, LINK FROM CUG_SPIDER_INFO" \
              " WHERE TITLE='%s' AND LINK='%s';" % (info_dict["title"], info_dict["link"])
        self.cursor.execute(sql)
        results = self.cursor.fetchall()
        if len(results) == 0:
            return True
        else:
            return False

    def update(self):
        """
        A decorator is used to register a function which return website parsed information.
        Usage:
            @app.update()
            def site_source_parse():
                return {
                    "title": "Hello, CUG!",
                    "link": "https://www.pointstone.org",
                    "abstract": "Forced Morning Exercises is useless.",
                    "site_url": "https://www.cug.edu.cn",
                    "category": "information",
                    "unit": "NULL"
                }
        Function decorated return a dictionary contains "title", "link", "abstract" and "site_url".
        Attention: site_url, title and link could not be NULL!
        """
        def decorator(function):
            self.function_list.append(function)
            return function
        return decorator

    def call_functions(self):
        """
        Call this member function to call all functions in list
        :return: None
        """
        print("-------Start Crawl on pid: %d-------" % os.getpid())
        for execute_fun in self.function_list:
            print("* Calling function: %s" % execute_fun.__name__)
            try:
                info = execute_fun()
                if isinstance(info, list) or isinstance(info, tuple):
                    for i in info:
                        if self.refresh_confirm(i):
                            self.insert_data(i)
                elif isinstance(info, dict):
                    if self.refresh_confirm(info):
                        self.insert_data(info)
                else:
                    raise TypeError("Function in queue should return a dict or list")
            except Exception as exp:
                print(type(exp), "---> occur in function: %s, more infomation:" %
                      execute_fun.__name__, exp)

    def run(self, sleep_seconds):
        """
        Runs spider on the machine!
        Insert information functions return to database.
        """
        while True:
            self.call_functions()
            sleep(sleep_seconds)

