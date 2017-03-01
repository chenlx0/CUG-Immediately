import time
import pymysql
import datetime
import configparser
import multiprocessing

SLEEP_TIME = 15


def get_mysql_info():
    """
    Get MySQL configure information from "spider.conf"
    return a dict contains host, password, user and database name(dbname)
    """
    config = configparser.ConfigParser()
    config.read("../spider.conf")
    mysql_info = dict(config["mysqld"])
    return mysql_info


class SpiderNet(object):
    def __init__(self):
        sql_dict = get_mysql_info()

        # These two class are used for connecting mysql server
        self.db = pymysql.connect(sql_dict["host"], sql_dict["user"],
                                  sql_dict["password"], sql_dict["dbname"])
        self.cursor = self.db.cursor()

        # Store function objects in a queue
        # And count the number of function objects
        self.queue = multiprocessing.Queue()
        self.fun_num = 0

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
                    "site_url": "https://www.cug.edu.cn"
                }
        Function decorated return a dictionary contains "title", "link", "abstract" and "site_url".
        Attention: site_url, title and link could not be NULL!
        """
        def decorator(foo):
            self.queue.put(foo)
            self.fun_num += 1
            return foo
        return decorator

    def run(self):
        """
        Runs spider on the machine!
        """
        while True:
            for i in range(self.fun_num):
                execute_foo = self.queue.get()
                info_dict = execute_foo()
                grab_time = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                sql = """INSERT INTO CUG_SPIDER_INFO(TITLE,
                UNIT, SITE_URL, LINK, GRAB_TIME, ABSTRACT)
                VALUES ("%s", "%s", "%s", "%s", "%s", "%s")""" % (info_dict["title"], info_dict["unit"],
                                                                  info_dict["site_url"], info_dict["link"],
                                                                  grab_time, info_dict["abstract"])

                self.cursor.execute(sql)
                self.db.commit()
                self.queue.put(execute_foo)
            time.sleep(SLEEP_TIME)
