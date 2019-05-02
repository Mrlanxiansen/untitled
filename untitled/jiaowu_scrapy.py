import requests
import re
import sys
from bs4 import BeautifulSoup




class EduAdmin:
    """模拟访问教务

        Attributes：
        user：学号
        passwd：密码
        headers：设置请求头
        login_url：登录时表单提交到的地址
        url：登录后才能访问的网页
        InfoUrl：个人信息页面
        selectedUrl：已选课程页面
        selectUrl：选课页面
        unSelectUrl：退课页面
        xspjUrl：学生评教页面
        courseTableUrl：课表纵式页面
        data：捉包数据，用于向教务发送请求
            login-> 登陆  url解密(gb2312)可得到
    """

    def __init__(self, user, passwd):
        self.user = user
        self.passwd = passwd
        self.data = {
            'username': self.user,
            'passwd': self.passwd,
            'login': '登录'.encode('gb2312')
        }
        self.login_url = 'http://192.168.4.17/student/public/login.asp'  # 登录时表单提交到的地址
        self.url = 'http://192.168.4.17/student/public/menu.asp?menu=mnall.asp'  # 登录后才能访问的网页
        self.InfoUrl = 'http://192.168.4.17/student/studentInfo.asp'  # 个人信息页面
        self.creditUrl = 'http://192.168.4.17/student/Credit.asp'  # 学分信息页面
        self.scoreUrl = 'http://192.168.4.17/student/Score.asp'  # 成绩查询页面
        self.xfjUrl = 'http://192.168.4.17/student/stxuefenji.asp'  # 学分绩查询页面
        self.selectUrl = 'http://192.168.4.17/student/Select.asp'  # 选课页面
        self.selectedUrl = 'http://192.168.4.17/student/Selected.asp'  # 已选课程页面
        self.unSelectUrl = 'http://192.168.4.17/student/UnSelect.asp'  # 退课页面
        self.xspjUrl = 'http://192.168.4.17/student/stjxpg.asp'  # 学生评教页面
        self.courseTableUrl = 'http://192.168.4.17/student/coursetable.asp'  # 课表纵式页面

        self.headers = {
            'User-agent':
                'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'
        }
        self.session = requests.Session()  # 构造Session


    def login(self):
        """模拟登陆
        Args:
            login_url:登陆请求页面
            data: 请求所需数据包
        Returns:
            在session中发送登录请求，此后这个session里就存储了cookie
            可以用print(session.cookies.get_dict())查看
        """
        resp = self.session.post(self.login_url, self.data)
        soup = BeautifulSoup(resp.content.decode("gb2312"), "html.parser")
        content = soup.title.string
        # print(content)
        if '学生选课管理系统' in content:
            return {'status': 2, "msg": "登录成功！"}
        elif '网站防火墙' in content:
            return {'status': 0, "msg": "访问太频繁！"}
        elif '学生用户登录' in content:
            return {'status': 1, "msg": "登录失败！"}


    def info(self):
        """个人信息页面"""

        resp = self.session.get(self.InfoUrl)
        content = resp.content.decode('gb2312')
        if not content:
            return {"status": 1, "msg": "获取个人信息失败"}
        string = r'<td width="25%" height="30".*?>(.*?)</td>'
        pattern = re.compile(string, re.S)
        res = re.findall(pattern, content)

        soup = BeautifulSoup(content, "html.parser")  # 适配页面的全部script
        script_list = soup.find_all('script')

        stu_id = res[0].split('：')[1]  # 学号
        name = res[1].replace('&nbsp;', '').split('：')[1]  # 姓名

        if res[2].find('select') != -1:  # 性别，进入填写模式的适配
            sex_str = r"'sex','(.*?)'"
            sex_pat = re.compile(sex_str, re.S)
            sex_res = re.findall(sex_pat, str(script_list[2]))
            sex = sex_res[0]
        else:
            sex = res[2].replace('\r\n', '').split('：')[1].lstrip()

        soup = BeautifulSoup(res[3], "html.parser")
        image = soup.img['src']  # 照片

        if res[6].find('input'):  # 联系电话，进入填写模式的适配
            phone_str = r"<input.*?value='(.*?)'>"
            phone_pat = re.compile(phone_str, re.S)
            phone_res = re.findall(phone_pat, res[6])
            phone = phone_res[0]
        else:
            phone = res[6].split('：')[1]

        grade = res[7].split('：')[1]  # 年级
        major = res[8].replace('\r\n', '').split('：')[1].lstrip()  # 专业
        class_g = res[9].split('：')[1]  # 班级

        if res[10].find("input") != -1:  # 民族，进入填写模式的适配
            nation_str = r"<input.*?value='(.*?)'>"
            nation_pat = re.compile(nation_str, re.S)
            nation_res = re.findall(nation_pat, res[10])
            nation = nation_res[0]
        else:
            nation = res[10].split('：')[1]

        if res[25].find('input'):  # 宿舍号，进入填写模式的适配
            dorm_str = r"<input.*?value='(.*?)'>"
            dorm_pat = re.compile(dorm_str, re.S)
            dorm_res = re.findall(dorm_pat, res[25])
            dorm = dorm_res[0]
        else:
            dorm = res.split('：')[1]

        stu_type = res[35].split('：')[1]  # 学生类型

        stu_info = {
            '学号': stu_id,
            '姓名': name,
            '性别': sex,
            # '照片': image,
            '联系电话': phone,
            '年级': grade,
            '专业': major,
            '班级': class_g,
            '民族': nation,
            '宿舍号': dorm,
            '学生类型': stu_type
        }
        return {"status": 2, "msg": "获取个人信息成功", "data": stu_info}

    def creadit(self):
        """学分信息"""

        creditResp = self.session.get(self.creditUrl)
        creditContent = creditResp.content.decode('gb2312')
        if not creditContent:
            return {"status": 1, "msg": "获取学分要求失败"}
        creditStr = r'<td>(.*?)</td><td>(.*?)</td><td>(.*?)</td><td>(.*?)</td><td>(.*?)</td>'
        CreditPattern = re.compile(creditStr, re.S)
        creditRes = re.findall(CreditPattern, creditContent)
        return {"status": 2, "msg": "获取学分要求成功", "data": creditRes}

    def score_option(self):
        """成绩查询的选择内容
        :return: 获取学期json信息
        """
        resp = self.session.get(self.scoreUrl)
        content = resp.content.decode("gb2312")
        # 获得学期已学课程数据
        score_str = r'<option value="(\d{5})">(.*?)</option>'
        score_pattern = re.compile(score_str, re.S)
        score_res = re.findall(score_pattern, content)
        lists = []
        for tup in score_res:
            lists.append(dict(value=tup[0], title=tup[1]))
        return {"status": 2, "msg": "获取成绩查询的选择内容成功", "data": lists}

    def score(self, term, ckind):
        """成绩查询

        Args:
            url: 请求页面
            term: 查询的学期 （例如2017-1018上学期为： 20171）一般情况下其与TermList相同
            TermList： 学期列表
            ckind： 课程性质 （考试：1  / 考查：2）
            lwPageSize： 查询行数(默认20)
            lwBtnquery： %B2%E9%D1%AF
        """

        data = {
            'term': term,
            'TermList': term,
            'ckind': ckind,
            'lwPageSize': '20',
            'lwBtnquery': '查询'.encode('gb2312')
        }

        resp = self.session.post(self.scoreUrl, data)
        score_content = resp.content.decode("gb2312")

        # 获得学期已学课程数据
        score_str = \
            r'<td>(.*?)</td><td>(.*?)</td><td>(.*?)</td><td>(.*?)</td><td>(.*?)</td><td>(.*?)</td><td>(.*?)</td><td>(.*?)</td>'
        score_pattern = re.compile(score_str, re.S)
        score_res = re.findall(score_pattern, score_content)

        # 当前学期获取的课程类型及总修学分
        type_str = r'<tr><th.*?>(.*?)</th><th.*?>(.*?)</th><th.*?>(.*?)</th></tr>'
        type_pat = re.compile(type_str, re.S)
        type_res = re.findall(type_pat, score_content)
        return {"status": 2, "msg": "查询成功！", "data": [score_res, type_res]}

    def xfj_option(self):
        """学分绩查询的选择内容
        :return: 查询的学年json信息
        """
        resp = self.session.get(self.xfjUrl)
        content = resp.content.decode("gb2312")
        if not content:
            return {"status": 1, "msg": "获取学分绩查询的选择内容失败"}
        # 获得学分绩
        xfj_str = r'<option value="(\d{4,5})">(.*?)</option>'
        pattern = re.compile(xfj_str, re.S)
        res = re.findall(pattern, content)
        lists = []
        for tup in res:
            lists.append(dict(value=tup[0], title=tup[1]))
        return {"status": 2, "msg": "获取学分绩查询的选择内容成功！", "data": lists}

    def xfj(self, term, course_level, kcfw, jstype, ljtype=''):
        """学分绩查询

        Args:
            term： 学年 （例如 2018）
            course_level： 课程等级（全部:null 正常课程:1 辅修专业课:2 第二专业课:3）
            ljtype：on(默认选择 ‘累计到本学期’) 或者 不添加此条字段
            kcfw：0（默认 按应选课程计算） / 1 （按实选课程计算）
            jstype：jqpjf(默认 按加权平均分计算） / pjxfj(按平均学分绩计算)
            lwOrderBy：是否点击学号（默认点击）
            lwPageSize： 每页行数（默认50）
            lwBtnquery：%B2%E9%D1%AF -> 查询
        """

        data = {
            'term': term,
            'courselevel': course_level,
            'kcfw': kcfw,
            'jstype': jstype,
            'lwOrderBy': 'stid',
            'lwPageSize': '50',
            'lwBtnquery': '查询'.encode('gb2312')
        }

        # ljtype被选中时，往数据包添加，不选择时不存在本条数据
        if (ljtype != ''):
            data['ljtype'] = 'on'

        Resp = self.session.post(self.xfjUrl, data)
        content = Resp.content.decode("gb2312")
        if not content:
            return {"status": 1, "msg": "访问学分绩查询失败"}
        # 获得学分绩
        str = r'<font.*?>\r\n([.\d]*?)</font>'
        pattern = re.compile(str, re.S)
        res = re.findall(pattern, content)
        xfj = res[0]

        # 获取其他相关信息
        other_str = r'<th>(.*?)\u3000</th>'
        other_pat = re.compile(other_str, re.S)
        other_res = re.findall(other_pat, content)

        soup = BeautifulSoup(other_res[1], "html.parser")

        data = {
            '序号': other_res[0],  # 序号
            '学号': soup.a.string,  # 学号
            '姓名': other_res[2],  # 姓名
            '班级': other_res[3],  # 班级
            '加权平均分': xfj  # 加权平均分
        }
        return {"status": 2, "msg": "访问学分绩查询成功", "data": data}

    def select_option(self):
        """选课前准备

        选课页面前先获取下拉菜单的键值
        :return: 选课前选择的可能值的集合list
        """
        resp = self.session.get(self.selectUrl)
        content = resp.content.decode("gb2312")
        # print(content)
        if not content:
            return {"status": 1, "msg": "选课页面访问错误"}

        soup = BeautifulSoup(content, "html.parser")
        select_list = soup.find_all('select')

        major_str = r'<option value="(\d{1,})">(.*?)</option>'
        major_pat = re.compile(major_str, re.S)
        major_res = re.findall(major_pat, str(select_list[0]))  # 2、专业  [('XX', "XX"), ('XX', "XX")...]

        major_list = []
        for tup in major_res:
            major_list.append(dict(title=tup[0], value=tup[1]))

        faculty_str = r'<option value="(\d{1,})">(.*?)</option>'
        faculty_pat = re.compile(faculty_str, re.S)
        faculty_res = re.findall(faculty_pat, str(select_list[1]))  # 4. 院系名称及值 [('XX', "XX"), ('XX', "XX")...]
        faculty_res.insert(0, ('0', "选择部门"))

        select_type_str = r'<option>(.*?)</option>'
        select_type_pat = re.compile(select_type_str, re.S)
        select_type_res = re.findall(select_type_pat, str(select_list[3]))  # 6、选课类型 ['XXX', 'XXX']

        faculty_list = []
        for tup in faculty_res:
            faculty_list.append(dict(title=tup[0], value=tup[1]))

        script_list = soup.find_all('script')

        spno_str = r'(\d{1,})'
        spno_pat = re.compile(spno_str, re.S)
        spno_res = re.findall(spno_pat, str(script_list[4]))  # 1、专业序号 ['XXX']
        # print(spno_res)

        grade_str = r'(\d{4})'
        grade_pat = re.compile(grade_str, re.S)
        grade_res = re.findall(grade_pat, str(script_list[5]))  # 3、年级 ['XXX']

        major_name_str = r'[a-z]{5}\[(\d{1,2})\].*?"(.*?)","(.*?)".*?'
        major_name_pat = re.compile(major_name_str, re.S)  # 5、专业名称 [('XX', 'XX', 'XX'), ('XX', 'XX', 'XX')...]
        major_name_res = re.findall(major_name_pat, str(script_list[2]))

        table_type_str = r'<input type="radio" name="kbys" value="(\d{1})".*?>([\u4e00-\u9fa5]{0,10})'
        table_type_pat = re.compile(table_type_str, re.S)
        table_type_res = re.findall(table_type_pat, content)  # 7、课表类型 [('XX', "XX"), ('XX', "XX")...]

        all_list = [spno_res, major_res, grade_res, faculty_res, major_name_res, select_type_res, table_type_res]
        # print(json.dumps(all_list, ensure_ascii=False))
        return {"status": 2, "msg": "选课前数据接收成功", "data": all_list}

    def select(self, SpecialtyList, grade, selecttype, xueyuan='', spno=''):
        """选课页面

        Args:
            url: 请求页面
            spno_request：专业 第一选项， 默认情况下与 SpecialtyList， 受xueyuan影响
            SpecialtyList：专业 第二选项
            grade：年级
            selecttype：选课类型 -> 两种选择码  重修或者正常
            xueyuan：院系名称， 一般为空
            spno：专业名称 一般和xueyuan相同
            'lwBtnquery'：确认%C8%B7%C8%CF
        """
        if selecttype == 'cx':
            selecttype = '重修'
        elif selecttype == 'zc':
            selecttype = '正常'

        selectData = {
            'lwPageSize': '1000',  # 每行页数
            'spno_request': SpecialtyList,  # 默认和 SpecialtyList 相同， 受xueyuan影响
            'SpecialtyList': SpecialtyList,
            'grade': grade,  # 年级
            'xueyuan': xueyuan,  # 学院 （三系16级 为 1603）
            'spno': spno,
            'selecttype': selecttype.encode('gb2312'),  # %D5%FD%B3%A3<-正常   %D6%D8%D0%DE<- 重修
            'kbys': '0',  # 0 <-列表       kbys: 1 <- 课表
            'lwBtnquery': '确认'.encode('gb2312')
        }

        selectResp = self.session.post(self.selectUrl, selectData)
        selectContent = selectResp.content.decode("gb2312").replace('&nbsp;', '')
        if not selectContent:
            return {"status": 1, "msg": "选课页面访问错误"}
        th_str = r'<th.*?>(.*?)</th>'
        th_pat = re.compile(th_str, re.S)
        th_res = re.findall(th_pat, selectContent)

        selectStr = r'<tr>' \
                    r"<td.*?value='(.*?)'><a.*?>(.*?)</a></td>" \
                    r'<td.*?><a.*?>(.*?)</a></td>' \
                    r'<td.*?>(.*?)</td>' \
                    r'<td.*?>(.*?)</td>' \
                    r'<td.*?>(.*?)</td>' \
                    r'<td.*?>(.*?)</td>' \
                    r'<td.*?>(.*?)</td>' \
                    r'<td.*?>(.*?)</td>' \
                    r'<td.*?>(.*?)</td>' \
                    r'<td.*?>(.*?)</td>' \
                    r'<td.*?>(.*?)</td>' \
                    r'<td.*?>(.*?)</td>' \
                    r'<td.*?>(.*?)</td>' \
                    r'<td.*?>(.*?)</td>' \
                    r'<td.*?>(.*?)</td>' \
                    r'<td.*?>(.*?)</td>' \
                    r'</tr>'

        selectPattern = re.compile(selectStr, re.S)
        selectRes = re.findall(selectPattern, selectContent)
        return {"status": 2, "msg": "选课页面访问成功", "data": [th_res, selectRes]}

    def selectCourse(self, spno_request, grade, selecttype, *courses):
        """进一步选课页面

        Args:
        selectUrl: 选课请求页面
        spno_request: 从函数select获取的传值 spno_request
        selecttype: 从函数select获取的传值 selecttype
        grade: 从函数select获取的传值 grade
        course: 选修的课程  从form表单的获取的传值
        lwBtnselect: 申请同一url与查询课程区分
        """

        # 本来打算使用eval()来处理从ionic返回的字符串类型的courses,使其
        # (str)->(list),但是php接收  {}和[](值两个以上的) 处理失败，故使用不定长参数，
        # 其对应body_value(select-course-three页面)
        course = []
        for c in courses:
            course.append(c)

        # selecttype = selecttype.encode('gb2312').decode('utf-8')
        if selecttype == 'cx':
            selecttype = '重修'
        elif selecttype == 'zc':
            selecttype = '正常'

        # if isinstance(selecttype, str):
        #     val = str(selecttype.encode('gb2312'))
        # else:
        #     val = "other"

        # 选择课程的数据包  kbys spno_request selecttype  grade
        selectCourseData = {
            'kbys': '0',  # 0 <-列表  kbys: 1 <- 课表
            'spno_request': spno_request,
            'selecttype': selecttype.encode('gb2312'),  # select的传值 selecttype
            'grade': grade,  # select的传值 selecttype
            'course': course,
            'lwBtnselect': '提交'.encode('gb2312')
        }

        # course通过抓包分析是个列表
        # 如 course -> ['BS....', 'BS....']

        selCourResp = self.session.post(self.selectUrl, selectCourseData)
        selCourContent = selCourResp.content.decode("gb2312")
        # print(selCourContent)
        if not selCourContent:
            return {"status": 1, "msg": "进一步选课网页加载失败"}

        selCourStr = r'<font color=.*?>(.*?)</font>'
        selCourPattern = re.compile(selCourStr, re.S)
        selCourRes = re.findall(selCourPattern, selCourContent)
        # print(selCourRes)
        return {"status": 2, "msg": "进一步选课网页加载成功", "data": selCourRes, 'test': selecttype}

    def selected_option(self):
        """已选课程的学期选择
        :return: 学期json数据
        """

        resp = self.session.get(self.selectedUrl)
        content = resp.content.decode("gb2312")

        pat = r'<option value="(\d{5})">(.*?)</option>'
        pattern = re.compile(pat, re.S)
        res = re.findall(pattern, content)
        lists = []
        for tup in res:
            lists.append(dict(termCode=tup[0], termName=tup[1]))
        return {"status": 2, "msg": "已选课程的学期选择加载成功", "data": lists}

    def slected(self, term):
        """已选课程

        Args:
            url:：请求页面
            term： 学期
            TermList：学期列表
            lwBtnquery：%C8%B7%C8%CF
        """

        data = {
            'term': term,
            'TermList': term,
            'lwPageSize': '20',
            'lwBtnquery': '确认'.encode('gb2312')
        }
        selectedResp = self.session.post(self.selectedUrl, data)
        selectedContent = selectedResp.content.decode("gb2312")
        # print(selectedContent)
        if not selectedContent:
            return {"status": 1, "msg": "已选课程访问错误"}
        selectedStr = r'<td>(.*?)</td><td>(.*?)</td><td>(.*?)</td><td>(.*?)</td><td>(.*?)</td><td>(.*?)</td><td>(.*?)</td>'
        selectedPattern = re.compile(selectedStr, re.S)
        selectedRes = re.findall(selectedPattern, selectedContent)
        return {"status": 2, "msg": "已选课程页面加载成功", "data": selectedRes}

    def unSelect_option(self):
        """
        退课前获取选课数据
        :return:
        """
        resp = self.session.post(self.unSelectUrl)
        content = resp.content.decode("gb2312").replace('&nbsp;', '')
        # print(content)
        if not content:
            return {"status": 1, "msg": "退课前准备页面访问错误"}

        head_str = r'<th.*?>(.*?)</th>'
        head_pat = re.compile(head_str, re.S)
        head_res = re.findall(head_pat, content)

        body_str = r'<tr>' \
                   r"<td.*?value='(.*?)'>(.*?)</td>" \
                   r'<td.*?>(.*?)</td>' \
                   r'<td.*?>(.*?)</td>' \
                   r'<td.*?>(.*?)</td>' \
                   r'<td.*?>(.*?)</td>' \
                   r'</tr>'
        body_pat = re.compile(body_str, re.S)
        body_res = re.findall(body_pat, content)
        return {"status": 2, "msg": "退课前准备成功", "data": [head_res, body_res]}

    def unSelect(self, course):
        """退课

        Args:
            unSelectUrl: 退课请求页面
            course： 请求退课的字典 格式如下：{'course' : ['课程代号1'， '课程代号2']}
            lwBtnunselect： 请求码之一（url->gb2312解析）
        """
        unSelectData = {
            'course': course,  # 课程代号
            'lwBtnunselect': '提交'.encode('gb2312')  # 提交
        }

        unSelectResp = self.session.post(self.unSelectUrl, unSelectData)
        unSelectContent = unSelectResp.content.decode("gb2312")
        if not unSelectContent:
            return {"status": 1, "msg": "退课页面访问错误"}

        unSelectStr = r'<font color=.*?>(.*?)</font>'
        unSelectPattern = re.compile(unSelectStr, re.S)
        unSelectedRes = re.findall(unSelectPattern, unSelectContent)
        return {"status": 2, "msg": "退课成功", "data": unSelectedRes}

    def xspj(self):
        """学生评教页面
        进入学生评教的首个页面，显示全部可以评教的课程条目
        """
        resp = self.session.get(self.xspjUrl)
        content = resp.content.decode("gb2312")
        if not content:
            return {"status": 1, "msg": "进入学生评教页面失败"}

        pat = r"<td>(.*?)</td><td>(.*?)</td><td>(.*?)</td><td>.*?href='(.*?)'.*?(.{3})</td>"
        pattern = re.compile(pat, re.S)
        res = re.findall(pattern, content)
        return {"status": 2, "msg": "进入学生评教页面成功", "data": res}

    def xspj_enter(self, urls):
        """学生评价评估进入页面
        在页面点击进入后获取的页面，可对指定老师进行评估
        :return:返回评估老师页面的全部数据
        """
        # 第一步，先从xspj(..)的返回值中获取相关老师的评教定向数据，这里的url我们可在xspj-two的http请求获取
        # 第二步，获取url后知该其不完整，故得拼凑

        urls = urls.replace(",", "&")
        url = "http://192.168.4.17/student/" + urls

        resp = self.session.get(url)
        content = resp.content.decode("gb2312")
        if not content:
            return {"status": 1, "msg": "学生评教进入评估失败", "data": ""}
        # print(content)
        pat = r"<tr>" \
              r"<td .*?>(.*?)</td>" \
              r"<td>(.*?)</td>" \
              r"<td>(.*?)</td>" \
              r"<td>(.*?)<td>" \
              r"<input.*?value='(.*?)'>.*?" \
              r"<input.*?value='(.*?)'>" \
              r"<input.*?value='(.*?)'>" \
              r"</td>" \
              r"</tr>"
        pattern = re.compile(pat, re.S)
        res = re.findall(pattern, content)
        # print(res)

        py_str = r'<textarea.*?name="(.*?)">(.*?)</textarea>'
        py_pat = re.compile(py_str, re.S)
        py_res = re.findall(py_pat, content)
        # print(py_res)

        btn_str = r"<input type='submit' name='(.*?)' value='(.*?)'.*?>"
        btn_pat = re.compile(btn_str, re.S)
        btn_res = re.findall(btn_pat, content)
        if len(btn_res):
            status = True
        else:
            status = False

        data = [res, py_res, status]
        return {"status": 2, "msg": "学生评教进入评估成功", "data": data}

    def xspj_enter_req(self, urls, btn_type,  py, *scores):
        """评估页面request
        在教室教学质量测评处有保存和提交请求，该方法为这两个
        请求提供数据处理，模拟教务的保存和提交功能

        Args:
        --------------------
        score: 输入框的内值, 受post请求过程中局限，故传进来的scores为不定长
        id: 评分的选项id，隐藏数据
        qz: 暂时还不知道是什么，隐藏数据
        --------------------以上三个都是文本框共有的值
        py: 评语
        pjlb: 隐藏数据之一，还不知道所代表含义
        gx: 在对页面没有任何的保存和提交操作前其的值为i，之后为 u
        tno: 教室编号
        cno: 课程代码
        term: 学期
        cid: 课程号
        lwBtnbc: 对应 保存 注意在保存到网页前注意encode('gb2312')
            或
        lwBtntijiao: 对应 提交 注意在提交到网页前注意encode('gb2312')
        :return:
        """
        # py很大可能性为汉字，所以注意转码
        # py = py.encode('gb2312').decode('utf-8')
        return py
        urls = urls.replace(",", "&")[2:]
        url = "http://192.168.4.17/student/" + urls

        resp = self.session.get(url)
        content = resp.content.decode("gb2312")
        if not content:
            return {"status": 1, "msg": "学生评教页面进入评估失败", "data": ""}
        # print(content)
        # return content
        pat = r"<tr>" \
              r"<td .*?</td>" \
              r"<td>.*?</td>" \
              r"<td>.*?</td>" \
              r"<td>.*?<td>" \
              r"<input.*?value='.*?'>.*?" \
              r"<input.*?value='(.*?)'>" \
              r"<input.*?value='(.*?)'>" \
              r"</td>" \
              r"</tr>"
        pattern = re.compile(pat, re.S)
        item_res = re.findall(pattern, content)  # 每个评估项的第5第6隐藏值
        # print(item_res)

        hid_str = r'<input type="hidden" name="(.*?)" value="(.*?)">'
        hit_pat = re.compile(hid_str, re.S)
        hid_res = re.findall(hit_pat, content)  # 全局hidden的hidden集合
        # print(hid_res)

        id_list = []  # 课程序号列表
        qz_list = []  # qz暂时不知道是什么（input的hidden之一）

        for item in item_res:
            id_list.append(item[0])
            qz_list.append(item[1])

        score = []
        for s in scores:
            score.append(s)

        data = {
            'score': ['96', '96', '96', '96', '96', '96', '96'],
            'id': ['138', '139', '140', '141', '142', '143', '144'],
            'qz': ['.2', '.15', '.15', '.1', '.1', '.05', '.05'],
            'py': py.encode('gb2312'),
        }

        for item in hid_res:  # 隐藏参数
            data[item[0]] = item[1]

        if btn_type == 'lwBtnbc':
            data[btn_type] = '保存'.encode('gb2312')
        elif btn_type == 'lwBtntijiao':
            data[btn_type] = '提交'.encode('gb2312')

        # print(data)

        rq_resp = self.session.post(url, data)
        rq_content = rq_resp.content.decode("gb2312").replace('&nbsp;', '')
        # print(rq_content)
        # return rq_content

        check_str = r'<form.*?<center>(.*?)</center>'
        check_pat = re.compile(check_str, re.S)
        check_res = re.findall(check_pat, rq_content)
        # print(check_res)
        # return check_res
        if not rq_content:
            return {"status": 1, "msg": "进入学生评教页面失败", "data": "没有任何数据"}

        if check_res[0] == '已保存！':
            return {"status": 2, "msg": "教师评估成功", "data":"保存成功"}
        elif check_res[0] == '已提交！':
            return {"status": 2, "msg": "教师评估成功", "data": "提交成功"}
        return {"status": 2, "msg": "教师评估失败"}

    def course_table_option(self):
        """对课表纵式的学期选择
        :return: 选择的学期json数据
        """
        resp = self.session.get(self.courseTableUrl)
        content = resp.content.decode("gbk")
        if not content:
            return {"status": 1, "msg": "课表前准备失败"}

        pat = r'<option value="(\d{5})">(.*?)</option>'
        pattern = re.compile(pat, re.S)
        res = re.findall(pattern, content)
        lists = []
        for tup in res:
            lists.append(dict(value=tup[0], title=tup[1]))
        return {"status": 2, "msg": "获取课表学期选择成功", "data": lists}

    def course_table(self, term):
        """课表纵式页面

        term 和 termList 相同, 在前端我们只用一种选择即可
        Args:
            url：请求页面
            term：学期
            termList：学期列表
            lwBtnquery：请求码， 通常这类url加密码需要修改
            lwBtnquery： %C8%B7%C8%CF
        """
        data = {
            'term': term,
            'TermList': term,
            'lwBtnquery': '确认'.encode('gb2312')
        }
        resp = self.session.post(self.courseTableUrl, data)
        content = resp.content.decode("gbk").replace('<br>', '').replace('&nbsp;', '')
        if not content:
            return {"status": 1, "msg": "获取课表失败"}

        str = r'<tr>' \
              r'<th>(.*?)</th>' \
              r'<td.*?>(.*?)</td>' \
              r'<td.*?>(.*?)</td>' \
              r'<td.*?>(.*?)</td>' \
              r'<td.*?>(.*?)</td>' \
              r'<td.*?>(.*?)</td>' \
              r'<td.*?>(.*?)</td>' \
              r'<td.*?>(.*?)</td>' \
              r'</tr>'
        pattern = re.compile(str, re.S)
        res = re.findall(pattern, content)
        return {"status": 2, "msg": "获取课表成功", "data": res}