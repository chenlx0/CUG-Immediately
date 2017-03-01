import time
import MySQLdb
import datetime
import configparser
import multiprocessing


def get_running_argument():
    """
    Get threads and sleep seconds from "spider.conf"
    """
    config = configparser.ConfigParser()
    config.read("../spider.conf")
    run_info = dict(config["runinfo"])
    return int(run_info["sleep_seconds"]), int(run_info["threads"])


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
        self.db = MySQLdb.connect(host=sql_dict["host"], user=sql_dict["user"], port=int(sql_dict["port"]),
                                  password=sql_dict["password"], db=sql_dict["dbname"])
        self.db.set_character_set('utf8')
        self.cursor = self.db.cursor()
        # self.cursor.execute('SET NAMES utf8;')
        # self.cursor.execute('SET CHARACTER SET utf8;')

        # threads and sleep seconds
        self.threads, self.sleep_seconds = get_running_argument()

        # Store function objects in a queue
        # And count the number of function objects
        self.queue = multiprocessing.Queue()
        self.fun_num = 0

    def insert_data(self, info_dict):
        """
        Insert data in dictionary format to database
        """
        grab_time = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        sql = """INSERT INTO CUG_SPIDER_INFO(TITLE,
        UNIT, SITE_URL, LINK, GRAB_TIME, ABSTRACT)
        VALUES ("%s", "%s", "%s", "%s", "%s", "%s")""" \
              % (info_dict["title"], info_dict["unit"],
                 info_dict["site_url"], info_dict["link"],
                 grab_time, info_dict["abstract"])

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
                    "unit": "NULL"
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
        Insert information functions return to database.
        """
        while True:
            for i in range(self.fun_num):
                execute_foo = self.queue.get()
                print("Calling function: %s" % execute_foo.__name__)
                info_dict = execute_foo()
                if self.refresh_confirm(info_dict):
                    self.insert_data(info_dict)
                self.queue.put(execute_foo)
            time.sleep(self.sleep_seconds)
