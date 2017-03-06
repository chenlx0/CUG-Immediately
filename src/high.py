from update import SpiderNet
from bs4 import BeautifulSoup
import requests

app = SpiderNet()


class XuegongInfo(object):
    def __init__(self):
        self.url = "http://www.xuegong.cug.edu.cn"
        source = requests.get(self.url)
        source.encoding = "utf-8"
        self.soup = BeautifulSoup(source.text, "html.parser")

    def news(self):
        info_list = self.soup.find_all("a", {"style": "width:86%;", "target": "_blank"})
        inner = info_list[0]
        return {
            "title": inner["title"],
            "link": inner["href"],
            "unit": "中国地质大学学工处",
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
            "unit": "中国地质大学学工处",
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
def cug_xuegong_infomation():
    X = XuegongInfo()
    return X.get_info()

if __name__ == "__main__":
    app.run(3)
