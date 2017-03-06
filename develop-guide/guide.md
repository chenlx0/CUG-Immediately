# PointStone CUG-Immediately 地大点石即刻项目参与指南
***
### 1. 地大即刻功能简介
地大即刻的目标是使用Python爬虫实时抓取学校官方主页的最新信息，存储在数据库内并第一时间推送到客户端。

### 2.当前进度
目前已经完成了简单的框架搭建，但由于不同网站之间的html样式有巨大的差距，需要各位撰写Python脚本解析学校各网站html代码。

### 3.如何开发
使用requests库请求学校各网站的源代码，借助Python的html解析库(推荐BeautifulSoup)获取最新一条信息，并以字典(dictionary)形式返回数据。在此之前，请导入src/update.py中的SpiderNet对象。使用SpiderNet中的成员函数update装饰抓取函数。请注意，字典中各key是固定不可删改的，如果该key下没有内容请用None表示。示例代码如下:
```Python
#/usr/bin/python3
from update import SpiderNet
from bs4 import BeautifulSoup
import requests

app = SpiderNet()

@app.update()
def cug_xuegong():
    """
    Example usage: return parsed page information
    """
    url = "http://www.xuegong.cug.edu.cn"
    source = requests.get(url)
    source.encoding = "utf-8"
    soup = BeautifulSoup(source.text, "html.parser")
    top_information = soup.find_all("a", {"style": "width:86%;", "target": "_blank"})
    inner = top_information[0]
    return {
        "title": inner["title"],
        "link": inner["href"],
        "unit": "学工处",
        "site_url": url,
        "abstract": None,
        "category": "通知"
    }

if __name__ == "__main__":
    app.run(10)
```

如果你想在本地运行这段代码，请安装MySQL并导入数据库(数据库文件为sql/CUG_CRAWL.sql)。你也可以仅仅测试抓取函数是否正确返回了最新信息。

需要注意的是，如果这个网页上包含了不止一条最新信息——比如这个网页有很多栏目，每个栏目都在实时更新信息，那么你的抓取函数可以返回一个list，这个list中的元素均为类似于示例代码中返回的dict。事实上，为了返回多条信息，我建议你分别将解析不同栏目的代码封装成类的成员函数。update.py中提供了一个基类CrawlBase，你构造的对象可以继承这个基类。基类构造函数有两个参数url和encoding，encoding默认为utf-8。调用构造函数后完成了http请求并构造了一个BeautifulSoup对象self.soup。查看[BeautifulSoup的文档](http://beautifulsoup.readthedocs.io/zh_CN/latest/)了解如何操作这个BeautifulSoup对象以解析html源码。你可以查看high.py了解如何继承这个基类。
对了，请务必在Python3.4及以上版本下进行开发。
如果你对Python3下进行爬虫有任何疑问，不妨先参考《Python网络数据采集》这本书，下载链接: [Python网络数据采集](http://storage.hc1024.me/Python_Web_Ebook.zip) 压缩文件已经加密，密码为站长名字全拼。

### 4.抓取网站列表
不同的网站之间有不同的优先级。根据网站的活跃度及其内容的重要性将网站分为三档，抓取脚本分别写成三个不同的文件，high.py, middle.py, low.py 不同优先级的网站爬虫写在不同的文件内。

欢迎补充新的网页。下列网站中有些可能需要在校园网中才能打开。

| 网站名称       | URL                            | 优先级    |
| ------------- |:-------------:| -----:|
| 校园主页       | http://www.cug.edu.cn/new/     | high     |
| 学生会         | http://su.mycug.net/           | high     |
| 教务处         | http://jwc.cug.edu.cn/         | high     |
| 学工处         | http://www.xuegong.cug.edu.cn/ | high     |
| 研究生院       | http://graduate.cug.edu.cn/     | high    |
| 地大之声       | http://voice.cug.edu.cn/indexone.shtml | high |
| 保卫处         | http://bwc.cug.edu.cn/              | middle |
| 办公室         | http://office.cug.edu.cn/Index.aspx | middle |
| 校医院         | http://xyy.cug.edu.cn/          | middle    |
| 地大信息公开网   | http://cuggroup.cug.edu.cn/xxgk/ |middle   |
| 图书馆          | http://www.lib.cug.edu.cn/      | middle   |
| 共青团委员会     | http://www.youth.cug.edu.cn/    | middle   |
| 党委组织部       | http://zzb.cug.edu.cn/          | middle   |
| 人事处           | http://rsc.cug.edu.cn/          | middle   |
| 财务处           | http://cw.cug.edu.cn/           | middle    |
| 国际合作处       | http://gjhzc.cug.edu.cn/indexone.shtml  | middle |
| 采购与招标管理中心| http://cgzb.cug.edu.cn/inet/inet_news/inet_index.html | middle |
| 各学院官方网站    | http://graduate.cug.edu.cn/ 网页底部的学院链接内| low|
| 海洋学院          | http://cmst.cug.edu.cn/      | low |
| 朴石(信工学院门户) | http://pustone.com/          | low |
| 设备处            | http://sbc.cug.edu.cn/       | low |
| 基建处            | http://jjc.cug.edu.cn/       | low |
| 档案馆           | http://dag.cug.edu.cn/          | low      |
| 网络与教育技术中心 | http://wlzx.cug.edu.cn/        | low      |
| 纪检监察处        | http://jjw.cug.edu.cn/         | low      |
| 科学技术发展院    | http://kjc.cug.edu.cn/          | low      |
| 后勤保障处        | http://hqbzc.cug.edu.cn/       | low       |
