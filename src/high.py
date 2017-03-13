from update import SpiderNet
from update import CrawlBase
import requests
from bs4 import BeautifulSoup

app = SpiderNet()


class XuegongInfo(CrawlBase):
    def __init__(self):
        CrawlBase.__init__(self, url="http://www.xuegong.cug.edu.cn/")

    def news(self):
        info_list = self.soup.find_all("a", {"style": "width:86%;", "target": "_blank"})
        inner = info_list[0]
        return {
            "title": inner["title"],
            "link": inner["href"],
            "unit": "学工处",
            "site_url": self.url,
            "abstract": None,
            "category": "学工要闻"
        }

    def get_info(self):
        info_list = self.soup.find_all("a", {"target": "_blank"})
        parse_list = []
        temp_dict = {
            "title": "",
            "link": "",
            "unit": "学工处",
            "site_url": self.url,
            "abstract": None,
            "category": "通知"
        }
        number_type = {
            27: "活动预告",
            35: "热点关注"
        }
        for i in (27, 35):
            temp_dict["category"] = number_type[i]
            temp_dict["link"] = info_list[i]["href"]
            temp_dict["title"] = info_list[i]["title"]
            parse_list.append(temp_dict)
        parse_list.append(self.news())
        return parse_list

@app.update()
def cug_xuegong_information():
    spider = XuegongInfo()
    return spider.get_info()


class JwcInfo(CrawlBase):
    def __init__(self):
        CrawlBase.__init__(self, url="http://jwc.cug.edu.cn/")

    def get_info(self):
        info = self.soup.find("td", {"class": "NewsListTitle"})
        return {
            "title": info.a.contents[0],
            "link": self.url + info.a["href"],
            "unit": "教务处",
            "site_url": self.url,
            "abstract": None,
            "category": "通知\新闻"
        }

@app.update()
def cug_jwc_information():
    spider = JwcInfo()
    return spider.get_info()


class StuUnionInfo(CrawlBase):
    def __init__(self):
        CrawlBase.__init__(self, url="http://su.mycug.net/")

    def get_left_list(self):
        info = self.soup.find("span", {"class": "tlist"})
        return {
            "title": info.a["title"],
            "link": info.a["href"],
            "unit": "学生会",
            "site_url": self.url,
            "abstract": None,
            "category": "通知\新闻"
        }

    def get_middle_list(self):
        info_list = self.soup.find_all("span", {"class": "tlist-m"})
        first = {
            "title": info_list[0].a["title"],
            "link": info_list[0].a["href"],
            "unit": "学生会",
            "site_url": self.url,
            "abstract": None,
            "category": "校园动态"
        }
        second = {
            "title": info_list[8].a["title"],
            "link": info_list[8].a["href"],
            "unit": "学生会",
            "site_url": self.url,
            "abstract": None,
            "category": "校会动态"
        }
        return first, second

    def get_all_info_dict(self):
        first, second = self.get_middle_list()
        return first, second, self.get_left_list()

@app.update()
def get_stu_union_information():
    spider = StuUnionInfo()
    return spider.get_all_info_dict()


class GraduateSchoolInfo(CrawlBase):
    def __init__(self):
        CrawlBase.__init__(self, url="http://graduate.cug.edu.cn/", encoding="gb2312")

    def get_all_info(self):
        info_list = self.soup.find_all("div", {"class": "yy_title"})
        first = {
            "title": info_list[0].a["title"],
            "link": self.url + info_list[0].a["href"],
            "unit": "研究生院",
            "site_url": self.url,
            "abstract": None,
            "category": "通知公告"
        }
        second = {
            "title": info_list[8].a["title"],
            "link": self.url + info_list[8].a["href"],
            "unit": "研究生院",
            "site_url": self.url,
            "abstract": None,
            "category": "工作动态"
        }
        return first, second

@app.update()
def graduate_school_information():
    spider = GraduateSchoolInfo()
    return spider.get_all_info()


@app.update()
def home_page_news():
    url = "http://www.cug.edu.cn/new/News_new8.aspx"
    source = requests.get(url)
    source.encoding = "utf-8"
    soup = BeautifulSoup(source.text, "html.parser")
    info = soup.find("td", {"width": "90%", "height": "22"})
    return {
        "title": info.a.contents[0],
        "link": url + info.a["href"],
        "unit": "地大主页",
        "site_url": url,
        "abstract": None,
        "category": "新闻"
    }


if __name__ == "__main__":
    app.run(300)
