import requests
from re import search
from bs4 import BeautifulSoup
from encoder import encode
from json import loads
from prettytable import PrettyTable
from urllib.parse import urlencode
from typing import Literal

public_key = "04d0c9e1ae89279fe05b435d63e3eba437bf510e09da5f71558974a19dc596724227f08dc2fc6e74bbb9d8b468d4dd5205e9b6793a3bbc48df3fdf219b3ea140e3"
finger_print = "b8d1ef2760eedac6b1aea370cf84ca38"  # 最后一位本来是6
finger_gen_print = "1fc53a9910e84c3e9c8721201bb64bc3"  # 最后一位本来是1


class LoginError(Exception):
    pass


class SecondVerificationError(Exception):
    pass


class TrickUrlSession(requests.Session):
    def set_trick_url(self, url):
        setattr(self, '_trick_url', url)

    def send(self, request, **kwargs):
        if getattr(self, '_trick_url', None):
            request.url = getattr(self, '_trick_url')
            setattr(self, '_trick_url', None)
        return super(TrickUrlSession, self).send(request, **kwargs)


class Spider:
    def __init__(self, username, password, time):
        self.username = username
        self.password = password
        self.encode_password = encode(password, public_key)
        self.time = time
        self.session = TrickUrlSession()
        self.session.headers.update({
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/120.0.0.0 Safari/537.36',
        })

        self.login_data = {"i_user": self.username, "i_pass": self.encode_password, "fingerPrint": finger_print,
                           "fingerGenPrint": finger_gen_print, "fingerGenPrint3": finger_gen_print, "i_captcha": None}

    def second_verify(self, method: Literal["wechat", "mobile", None] = None, vericode=None):
        if method:
            self.session.post("https://id.tsinghua.edu.cn/b/doubleAuth/login",
                              data={"action": "SEND_CODE", "type": method}, )
        elif vericode:
            self.session.post("https://id.tsinghua.edu.cn/b/doubleAuth/login",
                              data={"action": "VERITY_CODE", "vericode": vericode})
            self.session.post("https://id.tsinghua.edu.cn/b/doubleAuth/personal/saveFinger",
                              data={"radioVal": "是", "fingerprint": finger_print, "deviceName": "windows,Chrome/124",
                                    "singleLogin": ""})
            self.login()

    def login(self):
        self.session.get("http://zhjwxk.cic.tsinghua.edu.cn/xklogin.do")
        response = self.session.post("https://id.tsinghua.edu.cn/do/off/ui/auth/login/check", data=self.login_data)
        # print(response.text)
        if search("您的用户名或密码不正确，请重试！", response.text):
            raise LoginError("用户名或密码错误")
        if search("二次认证", response.text):
            raise SecondVerificationError('需要二次认证')

        href = search(r"window.location.replace\(\"(.+)\"\)", response.text).group(1)
        self.session.get(href)
        print('Login Success')

    def search_course(self, course_id: str = '', course_name: str = '', teacher_name: str = '',
                      is_general: bool = '', max_page: int = 3):
        url = f"https://zhjwxk.cic.tsinghua.edu.cn/xkBks.vxkBksJxjhBs.do?m=kkxxSearch&p_xnxq={self.time}"
        response = self.session.get(url)
        if search("用户登陆超时或访问内容不存在。请重试，如访问仍然失败，请与系统管理员联系。", response.text):
            self.login()
            response = self.session.get(url)
        soup = BeautifulSoup(response.text, "lxml")
        token = soup.find("input", attrs={"name": "token"})["value"]
        labels = list(map(lambda x: x.text.replace('\n', '').replace('\t', '').strip(),
                          soup.find("tr", attrs={"class": "trr1"}).find_all("td")))
        pretty_table = PrettyTable(labels)

        page, last_page = -1, 1
        while True:
            search_dict = {"m": "kkxxSearch", "page": str(page), "token": token, "p_sort.p1": '', "p_sort.p2": '',
                           "p_sort.asc1": "true", "p_sort.asc2": "true", "p_xnxq": self.time,
                           "pathContent": '一级课开课信息', "showtitle": '',
                           "p_kch": course_id, "p_kcm": course_name,
                           "p_zjjsxm": teacher_name, "p_kkdwnm": '', "p_kcflm": '',
                           "p_skxq": '', "p_skjc": '', "p_xkwzsm": '', "p_rxklxm": '',
                           "p_cktsm": "18" if is_general else '', "p_ssnj": '', "p_bkskyl_ig": '',
                           "p_yjskyl_ig": '', "goPageNumber": str(last_page)}

            trick_url = "https://zhjwxk.cic.tsinghua.edu.cn/xkBks.vxkBksJxjhBs.do?" + urlencode(search_dict,
                                                                                                encoding="gbk")
            self.session.set_trick_url(trick_url)
            response = self.session.post("https://zhjwxk.cic.tsinghua.edu.cn/xkBks.vxkBksJxjhBs.do")
            soup = BeautifulSoup(response.text, "lxml")
            page_message = soup.find("p", attrs={"class": "yeM yahei"}).text
            page, page_number, message_number = (
                search(r"第 (.+) 页 / 共 (.+) 页（共 (.+) 条记录）", page_message).group(1, 2, 3))
            page, page_number = int(page), int(page_number)

            for tr in soup.find_all("tr", attrs={"class": "trr2"}):
                td = list(map(lambda x: x.text.replace('\n', '').replace('\t', '').strip(), tr.find_all("td")))
                pretty_table.add_row(td)

            token = soup.find("input", attrs={"name": "token"})["value"]
            last_page = page
            page += 1
            if page > page_number or page > max_page:
                break

        description = f"""
共查找到 {message_number} 条结果，分为 {page_number} 页。以下内容是前 {min(max_page, page_number)} 页
结果如下：
{pretty_table}
"""
        return description

    def search_situation(self, course_id: str = '', course_name: str = '', course_rank: str = '', max_page: int = 3,
                         backdoor=False):
        url = f"https://zhjwxk.cic.tsinghua.edu.cn/xkBks.vxkBksXkbBs.do?m=xkqkSearch&p_xnxq=2025-2026-2"
        response = self.session.get(url)
        if search("用户登陆超时或访问内容不存在。请重试，如访问仍然失败，请与系统管理员联系。", response.text):
            self.login()
            response = self.session.get(url)
        soup = BeautifulSoup(response.text, "lxml")
        token = soup.find("input", attrs={"name": "token"})["value"]
        labels = list(map(lambda x: x.text.replace('\n', '').replace('\t', '').strip(),
                          soup.find("tr", attrs={"class": "trr1"}).find_all("td")))
        pretty_table = PrettyTable(labels)
        page, last_page = -1, 1
        while True:
            search_dict = {"m": "kylSearch", "page": str(page), "token": token, "p_sort.p1": '', "p_sort.p2": '',
                           "p_sort.asc1": '', "p_sort.asc2": '', "p_xnxq": self.time, "pathContent": '课余量查询',
                           "p_kch": course_id, "p_kxh": course_rank, "p_kcm": course_name,
                           "p_skxq": '', "p_skjc": '', "goPageNumber": str(last_page)}

            trick_url = "https://zhjwxk.cic.tsinghua.edu.cn/xkBks.vxkBksJxjhBs.do?" + urlencode(search_dict,
                                                                                                encoding="gbk")
            self.session.set_trick_url(trick_url)
            response = self.session.post("https://zhjwxk.cic.tsinghua.edu.cn/xkBks.vxkBksJxjhBs.do")

            soup = BeautifulSoup(response.text, "lxml")

            page_message = soup.find("p", attrs={"class": "yeM yahei"}).text
            page, page_number, message_number = search(
                r"第 (.+) 页 / 共 (.+) 页（共 (.+) 条记录）", page_message).group(1, 2, 3)
            page, page_number = int(page), int(page_number)

            course_messages = []
            for tr in soup.find_all("tr", attrs={"class": "trr2"}):
                td = list(map(lambda x: x.text.replace('\n', '').replace('\t', '').strip(), tr.find_all("td")))
                course_messages.append(td)

            if backdoor:
                return course_messages

            dlcds = soup.find_all(attrs={"class": "dlcd"})
            assert dlcds
            message = ";".join(list(map(lambda x: x["id"][5:], dlcds)) + [''])

            response = self.session.post("https://zhjwxk.cic.tsinghua.edu.cn/xkBks.vxkBksXkbBs.do",
                                         data={"m": "selectBksDlCount", "kc_message": message})
            for m, queue in zip(course_messages, loads(response.text)):
                if queue.get("dlrs"):
                    m[5] = queue["dlrs"]

            pretty_table.add_rows(course_messages)

            token = soup.find("input", attrs={"name": "token"})["value"]
            last_page = page
            page += 1
            if page > page_number or page > max_page:
                break

        description = f"""
共查找到 {message_number} 条结果，分为 {page_number} 页。以下内容是前 {min(max_page, page_number)} 页: 
结果如下：
{pretty_table}
"""
        return description

    def search_teacher(self, teacher: str):
        url = "https://yourschool.cc/thucourse_api/api/search/"
        response = self.session.get(url, params={"q": teacher, "page": 1, "size": 20, "only": 1})
        results = loads(response.text)["results"]
        courses = []
        for result in results:
            course_id = result["id"]
            response = (
                self.session.get(f"https://yourschool.cc/thucourse_api/api/course/{course_id}/review/?&page=1&size=20"))
            reviews = loads(response.text)["results"]
            review_messages = PrettyTable(["评分", "内容"])
            review_messages.align["内容"] = "l"
            for review in reviews:
                review_messages.add_row([review["rating"], review["comment"]])
            courses.append({"课程名": result["name"], "评价人数": result["rating"]["count"],
                            "平均分": result["rating"]["avg"], "具体评价": review_messages})
        final_response = f"""
{teacher} 老师共有 {len(courses)} 门课程有人评价。
"""
        for course in courses:
            final_response += f"""
课程名：{course["课程名"]}，评价人数： {course["评价人数"]}，平均分：{course["平均分"]}。具体评价如下：
{course["具体评价"]}
"""
        return final_response

    def search_user_table(self):
        url = f"http://zhjwxk.cic.tsinghua.edu.cn/xkBks.vxkBksXkbBs.do?p_xnxq={self.time}"
        response = self.session.get(url)
        if search("用户登陆超时或访问内容不存在。请重试，如访问仍然失败，请与系统管理员联系。", response.text):
            self.login()
            response = self.session.get(url)
        soup = BeautifulSoup(response.text, "lxml")
        table = soup.find("table")
        labels = [td.text for td in table.find("tr", {"class": "trr1"}).find_all("td")]
        pretty_table = PrettyTable(labels)
        for tr in soup.find_all("tr", {"class": "trr2"}):
            contents = [td.text.replace('\n', '').replace('\t', '').strip()
                        for td in tr.find_all("td")]
            situation = self.search_situation(course_id=contents[3], course_rank=contents[4], backdoor=True)
            situation = list(filter(lambda x: x[1] == contents[4], situation))
            contents[7] = situation[0][7].replace('\n', '').replace('\t', '').strip()
            pretty_table.add_row(contents)

        return f"""用户当前选课情况为：
{pretty_table}
"""


if __name__ == '__main__':
    spider = Spider("2025013622", "dice123456", "2025-2026-2")
    # try:
    #     spider.login()
    # except SecondVerificationError as e:
    #     spider.second_verify("wechat", input)
    print(spider.search_user_table())
    # print(spider.search_course("10691342"))
