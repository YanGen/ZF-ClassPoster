# -*- coding:gbk -*-
import os,datetime
import requests,re,random
from bs4 import BeautifulSoup
import xml.dom.minidom
import json
import threading
import hashlib
import time


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36",
}

def SelectionIP():
    IP = ['34']
    return IP[random.randint(0,len(IP)-1)]

def Key(Key):
    Y = int(datetime.datetime.now().year)
    M = int(datetime.datetime.now().month)
    D = int(datetime.datetime.now().day)
    if key == "8ae7778c9ae86d2ded133e891995dc9e":
        allowATime = datetime.datetime(2018, 12, 26, 1, 10, 10)  # 允许使用
        allowBTime = datetime.datetime(2018, 12, 27, 1, 10, 10)
        if datetime.datetime.now() > allowATime and datetime.datetime.now() < allowBTime:
            pass
        else:
            print("不在密匙可用时段！")
            Key(input("请输入密匙: "))
    else:
        if key != "7ae7778c9ae86d2ded133e891995dc9e":
            if key != "36963":
                print("错误！")
                Key(input("请输入密匙: "))

def Login(studentnumber,password,ip,codeReco = True):
    req = requests.session()
    url = "http://10.10.240.%s/default2.aspx"%ip
    response = req.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    __VIEWSTATE = soup.find_all("input", type="hidden")[0]['value']
    imgUrl = "http://10.10.240.%s/CheckCode.aspx?"%ip
    imgresponse = req.get(imgUrl, stream=True)
    image = imgresponse.content
    DstDir = os.getcwd() + "\\"
    print("保存验证码", DstDir + "code.jpg")
    try:
        with open(DstDir + "code.jpg", "wb") as jpg:
            jpg.write(image)
    except IOError:
        print("IO Error\n")
    print("识别中...")
    if codeReco:
        code = TestFunc("code.jpg")
        print("结果",code)

    else:
        code = input("手动输入验证码: ")
    os.remove("code.jpg")
    postdata = {
        "__VIEWSTATE": __VIEWSTATE,
        "txtUserName": studentnumber,
        "TextBox2": password,
        "txtSecretCode": code,
        "Button1": "",
    }

    res = req.post(url, data=postdata, headers=headers)
    Dsoup = BeautifulSoup(res.content,"html.parser")
    nameTag = Dsoup.find("span",id="xhxm")
    if nameTag:
        name = nameTag.get_text().replace("同学","")
    else:
        print("识别失败...")
        return Login(studentnumber,password,ip,codeReco = False)
    print ("登录状态码",res.status_code)
    print ("确认姓名--> ",name)
    if(res.status_code!=200):
        print ("登录失败,退出")
        return "logerr"
    return [req,name]


def CrawlCourse(req,name,studentnumber,ip,totalPageNum): # 选课
    print ("正在准备课程序列...")

    # 点击学生选课
    # url = "http://10.10.240.26/xsxk.aspx?xh=%s&xm=%s&gnmkdm=N121101"%(studentnumber,str(name))
    url = "http://10.10.240.%s/xsxk.aspx?xh=%s&gnmkdm=N121101"%(ip,studentnumber)

    req.headers['Referer'] = "http://10.10.240.%s/xs_main.aspx?xh=%s" % (ip,studentnumber)
    req.headers['User-Agent'] = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36"
    res = req.get(url)
    value = re.compile("<input type=\"hidden\" name=\"__VIEWSTATE\" value=\"(.*?)\" />")
    value = re.findall(value,str(res.content))[0]
    zymc = re.compile("<input name=\"zymc\" type=\"text\" value=\"(.*?)\" readonly")
    zymc = re.findall(zymc, str(res.content))[0]


    # 点击选修课程
    postdata = {
        "__VIEWSTATE": value,
        "zymc":zymc,
        "Button2":"选修课程",
    }
    req.headers['Referer'] = url
    res = req.post(url, data=postdata)
    value = re.compile("<input type=\"hidden\" name=\"__VIEWSTATE\" value=\"(.*?)\" />")
    value = re.findall(value, str(res.content))[0]
    # 点击选修课程
    postdata = {
        "__VIEWSTATE": value,
        "Button7": "快速选课",
    }
    waitClas = []
    # 点击快速选课
    res = req.post(url, data=postdata)
    soup = BeautifulSoup(res.content, 'html.parser')
    Td = soup.find_all("a",href="#")
    for i in range(1,int(len(Td)/3)+1):
        ind = i*3 - 2
        waitClas.append(Td[ind])
    # PagePara = re.compile("<a href=\"javascript:__doPostBack('(.*?)','')\">.*?</a>")
    # Page = re.findall(PagePara,res.content)
    Psoup = BeautifulSoup(res.content,"html.parser")
    B = str(Psoup.find("td",colspan="15"))
    Bsoup = BeautifulSoup(B,"html.parser")
    A = Bsoup.find_all("a")
    Page = []
    for a in A:
        Page.append(str(a['href']).replace("javascript:__doPostBack('","").replace("','')",""))
    if len(Page)>=10:
        addPageNum = int(totalPageNum)-11
        addPageBeforeNum = int(addPageNum/10)
        addPageAfterNum = addPageNum%10
        for i in range(0,addPageBeforeNum):
            for j in range(2,12):
                Page.append("kcmcgrid$_ctl14$_ctl"+str(j))
        for i in range(11-addPageAfterNum,11):
            Page.append("kcmcgrid$_ctl14$_ctl"+str(i))


    value = re.compile("<input type=\"hidden\" name=\"__VIEWSTATE\" value=\"(.*?)\" />")
    value = re.findall(value, str(res.content))[0]
    print ("共:"+str(len(Page)+1)+"页")

    for page in Page:
        # print(page)

        # kcmcgrid$_ctl14$_ctl6'
        postdata = {
            "__EVENTTARGET": page.replace("$",":"),
            "__VIEWSTATE":value
        }
        content = CrawlPage(req,name,studentnumber,postdata,ip)
        value = content[0]
        for i in range(1, int(len(content[1]) / 3) + 1):
            ind = i * 3 - 2
            waitClas.append(content[1][ind])

    Url = []
    for ind in range(0,len(waitClas)):
        print ("---------------------------------")
        print ("序列号:"+str(ind+1)+" 课程:"+str(waitClas[ind].get_text()))
        Link = re.compile("window.open\(\'(.*?)\',")
        link = re.findall(Link,str(waitClas[ind]['onclick']))[0]
        url = "http://10.10.240."+ip+"/"+ link
        Url.append(url)
    print("---------------------------------")
    return Url

def CrawlSportsCourse(req,name,studentnumber,ip):
    print("正在采集可选时间...")
    url = "http://10.10.240.%s/xf_xstyxk.aspx?xh=%s&gnmkdm=N121102"%(ip,studentnumber)
    req.headers['Referer'] = "http://10.10.240.%s/xs_main.aspx?xh=%s"%(ip,studentnumber)
    res = req.get(url)
    value = re.compile("<input type=\"hidden\" name=\"__VIEWSTATE\" value=\"(.*?)\" />")
    value = re.findall(value, str(res.content,"utf-8"))[0]
    soup = BeautifulSoup(str(res.content,"utf-8"),"html.parser")
    Option = soup.find_all("option")
    i = 0
    for option in Option:
        i+=1
        print("序列号: "+str(i)+"."+option["value"])
    num = input("输入时间序列号:")
    option = Option[int(num) - 1]
    print("选择" + option['value'])
    print("正在准备体育课列表...")
    # 模拟点击时间选项
    postdata = {
        "__EVENTTARGET":"kg",
        "__VIEWSTATE":value,
        "kj":option,
    }
    url = "http://10.10.240.%s/xf_xstyxk.aspx?xh=%s&gnmkdm=N121102"%(ip,studentnumber)
    req.headers["Referer"] = url
    res = req.post(url, data=postdata)
    value = re.compile("<input type=\"hidden\" name=\"__VIEWSTATE\" value=\"(.*?)\" />")
    value = re.findall(value, str(res.content))[0]
    soup = BeautifulSoup(res.content, 'html.parser')
    Td = soup.find_all("a", href="#")
    for i in range(0,int(len(Td)/2)):
        print("-----------------------------------")
        print("序列号: "+str(i+1)+"."+str(Td[2*i].get_text()+"---"+Td[2*i+1].get_text()))
    print("-----------------------------------")
    num = int(input("选择:"))
    postdata = {
        "__VIEWSTATE":value,
        "kj":option['value'],
        "Button1": " 提 交 ",
        "kcmcGrid:_ctl%s:xk"%str(num+1):"on",
    }
    Y = int(datetime.datetime.now().year)
    M = int(datetime.datetime.now().month)
    D = int(datetime.datetime.now().day)
    startTime = datetime.datetime(Y, M, D, 12, 58, 40)  # 输入启动时间
    print(str(startTime) + "将执行选课操作")
    while datetime.datetime.now() < startTime:
        time.sleep(0.5)
    print('Action now starts on %s' % startTime)
    while (1):
        try:
            res = req.post(url, data=postdata, timeout=1)
            html = str(res.content, "utf-8")
        except:
            print("链接超时,重新请求")
        if html.count("成功") != 0:
            print("保存成功！！！")
            print("保存成功！！！")
            print("保存成功！！！")
            break
        elif html.count("选课时间") != 0:
            print("系统提示时间未到,再次请求！")
        elif html.count("限制") != 0:
            print("人数超过限制,失败~")
            break

def CrawlPage(req,name,studentnumber,postdata,ip):
    url = "http://10.10.240.%s/xsxk.aspx?xh=%s&xm=%s&gnmkdm=N121101"%(ip,studentnumber,name)
    res = req.post(url,data=postdata)
    value = re.compile("<input type=\"hidden\" name=\"__VIEWSTATE\" value=\"(.*?)\" />")
    value = re.findall(value, str(res.content))[0]
    soup = BeautifulSoup(res.content, 'html.parser')
    Td = soup.find_all("a", href="#")
    return [value,Td]

# 准备参数
def PreparaParam(req,url):
    print("\n3秒后操作")
    time.sleep(3)
    req.headers['Referer'] = url
    res = req.get(url)
    html = str((res.content), "utf-8")
    if "三秒防刷" in html:
        return "s"
    classNameSearch = re.compile("课程名称：(.*?)学分").findall(html)
    className = ""
    if len(classNameSearch)!=0:
        className = classNameSearch[0].replace("&nbsp;","")
    print("输入 "+className+" 的待选时间序列号")
    Xkkh = re.compile('value="(.*?)" name=xkkh')
    Xkkh = re.findall(Xkkh, html)
    Teacher = []
    soup = BeautifulSoup(html, "html.parser")
    TR = soup.find_all("tr")
    TR.remove(TR[0])
    TR.remove(TR[len(TR) - 1])
    for tr in TR:
        Dsoup = BeautifulSoup(str(tr), "html.parser")
        TD = Dsoup.find_all("td")
        name = TD[1].get_text()
        dtime = TD[5].get_text()
        content = name + " *** " + dtime
        Teacher.append(content)

    Axkkh = []
    j = 0
    for xkkh in Xkkh:
        j += 1
        try:
            print("序列号: " + str(j) + "." + str(Teacher[j - 1]))
        except:
            print("序列号: " + str(j) + "编码问题无法显示")
        Axkkh.append(xkkh)
    num = int(input("序列号:"))
    return num

# 执行选课
def ExecutePost(req,url,num):
    req.headers['Referer'] = url
    res = req.get(url)
    html = str((res.content),"utf-8")
    if "三秒防刷" in html:
        print("三秒防刷...")
    classNameSearch = re.compile("课程名称：(.*?)学分").findall(html)
    className = ""
    if len(classNameSearch) != 0:
        className = classNameSearch[0].replace("&nbsp;", "")

    value = re.compile('name="__VIEWSTATE" value="(.*?)" />')
    value = re.findall(value, html)[0]
    Xkkh = re.compile('value="(.*?)" name=xkkh')
    Xkkh = re.findall(Xkkh, html)
    Teacher = []
    soup = BeautifulSoup(html,"html.parser")
    TR = soup.find_all("tr")
    TR.remove(TR[0])
    TR.remove(TR[len(TR)-1])
    for tr in TR:
        Dsoup = BeautifulSoup(str(tr),"html.parser")
        TD = Dsoup.find_all("td")
        name = TD[1].get_text()
        dtime = TD[5].get_text()
        content = name+" *** "+dtime
        Teacher.append(content)


    num = int(num)
    clas = Xkkh[num-1]
    book = "0"
    postdata = {
        "__EVENTTARGET": "Button1",
        "__VIEWSTATE": value,
        "RadioButtonList1":book,
        "xkkh":clas,
    }
    M = int(datetime.datetime.now().month)
    D = int(datetime.datetime.now().day)
    startTime = datetime.datetime(2018, M, D, 12, 58, 50)  # 启动时间
    print(className+" 选课参数准备完成!",str(startTime)+"将执行选课操作")

    while datetime.datetime.now() < startTime:
        time.sleep(0.5)

    print(className ,'线程启动 %s' % datetime.datetime.now())

    while(1):
        try:
            res = req.post(url,data=postdata,timeout=1)
            html = str(res.content,"utf-8")
        except:
            print("链接超时,重新请求")
            pass
        if html.count("成功") != 0:
            print(className ,"选课成功！！！")
            print(className ,"选课成功！！！")
            print(className ,"选课成功！！！\n")
            break
        elif html.count("选课时间")!=0:
            print (className ,"系统提示时间未到,再次请求！\n")
        elif html.count("限制")!=0:
            print (className ,"人数超过限制,失败~\n")
            break

def SaveClass(req,name,studentnumber,ip):
    # 打印课表

    url = "http://10.10.240.%s/xskb.aspx?xh=%s&xhxx=%s2017-20182"%(ip,studentnumber,studentnumber)
    req.headers['Referer'] = "http://10.10.240.%s/xs_main.aspx?xh=%s"%(ip,studentnumber)
    req.headers['User-Agent'] = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36"
    res = req.get(url)
    soup = BeautifulSoup(str(res.content,'utf-8'),"html.parser")
    with open("class.txt",'w') as f:
        clas2 = soup.find_all("td",rowspan="2")
        for each in clas2:
            print (each.get_text())
            f.write(each.get_text()+"\n")
        clas3 = soup.find_all("td", rowspan="3")
        for each in clas3:
            print (each.get_text())
            f.write(each.get_text()+"\n")
        f.write("----------------------------------------------\n")
        f.close()


FATEA_PRED_URL  = "http://pred.fateadm.com"

def LOG(log):
    # 不需要测试时，注释掉日志就可以了
    # print(log)
    log = None

class TmpObj():
    def __init__(self):
        self.value  = None

class Rsp():
    def __init__(self):
        self.ret_code   = -1
        self.cust_val   = 0.0
        self.err_msg    = "succ"
        self.pred_rsp   = TmpObj()

    def ParseJsonRsp(self, rsp_data):
        if rsp_data is None:
            self.err_msg     = "http request failed, get rsp Nil data"
            return
        jrsp                = json.loads( rsp_data)
        self.ret_code       = int(jrsp["RetCode"])
        self.err_msg        = jrsp["ErrMsg"]
        self.request_id     = jrsp["RequestId"]
        if self.ret_code == 0:
            rslt_data   = jrsp["RspData"]
            if rslt_data is not None and rslt_data != "":
                jrsp_ext    = json.loads( rslt_data)
                if "cust_val" in jrsp_ext:
                    data        = jrsp_ext["cust_val"]
                    self.cust_val   = float(data)
                if "result" in jrsp_ext:
                    data        = jrsp_ext["result"]
                    self.pred_rsp.value     = data

def CalcSign(pd_id, passwd, timestamp):
    md5     = hashlib.md5()
    md5.update((timestamp + passwd).encode())
    csign   = md5.hexdigest()

    md5     = hashlib.md5()
    md5.update((pd_id + timestamp + csign).encode())
    csign   = md5.hexdigest()
    return csign

def CalcCardSign(cardid, cardkey, timestamp, passwd):
    md5     = hashlib.md5()
    md5.update(passwd + timestamp + cardid + cardkey)
    return md5.hexdigest()

def HttpRequest(url, body_data, img_data=""):
    rsp         = Rsp()
    post_data   = body_data
    files       = {
        'img_data':('img_data',img_data)
    }
    header      = {
            'User-Agent': 'Mozilla/5.0',
            }
    rsp_data    = requests.post(url, post_data,files=files ,headers=header)
    rsp.ParseJsonRsp( rsp_data.text)
    return rsp

class FateadmApi():
    # API接口调用类
    # 参数（appID，appKey，pdID，pdKey）
    def __init__(self, app_id, app_key, pd_id, pd_key):
        self.app_id     = app_id
        if app_id is None:
            self.app_id = ""
        self.app_key    = app_key
        self.pd_id      = pd_id
        self.pd_key     = pd_key
        self.host       = FATEA_PRED_URL

    def SetHost(self, url):
        self.host       = url

    #
    # 查询余额
    # 参数：无
    # 返回值：
    #   rsp.ret_code：正常返回0
    #   rsp.cust_val：用户余额
    #   rsp.err_msg：异常时返回异常详情
    #
    def QueryBalc(self):
        tm      = str( int(time.time()))
        sign    = CalcSign( self.pd_id, self.pd_key, tm)
        param   = {
                "user_id": self.pd_id,
                "timestamp":tm,
                "sign":sign
                }
        url     = self.host + "/api/custval"
        rsp     = HttpRequest(url, param)
        if rsp.ret_code == 0:
            LOG("query succ ret: {} cust_val: {} rsp: {} pred: {}".format( rsp.ret_code, rsp.cust_val, rsp.err_msg, rsp.pred_rsp.value))
        else:
            LOG("query failed ret: {} err: {}".format( rsp.ret_code, rsp.err_msg.encode('utf-8')))
        return rsp

    #
    # 查询网络延迟
    # 参数：pred_type:识别类型
    # 返回值：
    #   rsp.ret_code：正常返回0
    #   rsp.err_msg： 异常时返回异常详情
    #
    def QueryTTS(self, pred_type):
        tm          = str( int(time.time()))
        sign        = CalcSign( self.pd_id, self.pd_key, tm)
        param       = {
                "user_id": self.pd_id,
                "timestamp":tm,
                "sign":sign,
                "predict_type":pred_type,
                }
        if self.app_id != "":
            #
            asign       = CalcSign(self.app_id, self.app_key, tm)
            param["appid"]     = self.app_id
            param["asign"]      = asign
        url     = self.host + "/api/qcrtt"
        rsp     = HttpRequest(url, param)
        if rsp.ret_code == 0:
            LOG("query rtt succ ret: {} request_id: {} err: {}".format( rsp.ret_code, rsp.request_id, rsp.err_msg))
        else:
            LOG("predict failed ret: {} err: {}".format( rsp.ret_code, rsp.err_msg.encode('utf-8')))
        return rsp

    #
    # 识别验证码
    # 参数：pred_type:识别类型  img_data:图片的数据
    # 返回值：
    #   rsp.ret_code：正常返回0
    #   rsp.request_id：唯一订单号
    #   rsp.pred_rsp.value：识别结果
    #   rsp.err_msg：异常时返回异常详情
    #
    def Predict(self, pred_type, img_data, head_info = ""):
        tm          = str( int(time.time()))
        sign        = CalcSign( self.pd_id, self.pd_key, tm)
        param       = {
                "user_id": self.pd_id,
                "timestamp": tm,
                "sign": sign,
                "predict_type": pred_type,
                "up_type": "mt"
                }
        if head_info is not None or head_info != "":
            param["head_info"] = head_info
        if self.app_id != "":
            #
            asign       = CalcSign(self.app_id, self.app_key, tm)
            param["appid"]     = self.app_id
            param["asign"]      = asign
        url     = self.host + "/api/capreg"
        files = img_data
        rsp     = HttpRequest(url, param, files)
        if rsp.ret_code == 0:
            LOG("predict succ ret: {} request_id: {} pred: {} err: {}".format( rsp.ret_code, rsp.request_id, rsp.pred_rsp.value, rsp.err_msg))
        else:
            LOG("predict failed ret: {} err: {}".format( rsp.ret_code, rsp.err_msg))
            if rsp.ret_code == 4003:
                #lack of money
                LOG("cust_val <= 0 lack of money, please charge immediately")
        return rsp

    #
    # 从文件进行验证码识别
    # 参数：pred_type;识别类型  file_name:文件名
    # 返回值：
    #   rsp.ret_code：正常返回0
    #   rsp.request_id：唯一订单号
    #   rsp.pred_rsp.value：识别结果
    #   rsp.err_msg：异常时返回异常详情
    #
    def PredictFromFile( self, pred_type, file_name, head_info = ""):
        with open(file_name, "rb") as f:
            data = f.read()
        return self.Predict(pred_type,data,head_info=head_info)

    #
    # 识别失败，进行退款请求
    # 参数：request_id：需要退款的订单号
    # 返回值：
    #   rsp.ret_code：正常返回0
    #   rsp.err_msg：异常时返回异常详情
    #
    # 注意:
    #    Predict识别接口，仅在ret_code == 0时才会进行扣款，才需要进行退款请求，否则无需进行退款操作
    # 注意2:
    #   退款仅在正常识别出结果后，无法通过网站验证的情况，请勿非法或者滥用，否则可能进行封号处理
    #
    def Justice(self, request_id):
        if request_id == "":
            #
            return
        tm          = str( int(time.time()))
        sign        = CalcSign( self.pd_id, self.pd_key, tm)
        param       = {
                "user_id": self.pd_id,
                "timestamp":tm,
                "sign":sign,
                "request_id":request_id
                }
        url     = self.host + "/api/capjust"
        rsp     = HttpRequest(url, param)
        if rsp.ret_code == 0:
            LOG("justice succ ret: {} request_id: {} pred: {} err: {}".format( rsp.ret_code, rsp.request_id, rsp.pred_rsp.value, rsp.err_msg))
        else:
            LOG("justice failed ret: {} err: {}".format( rsp.ret_code, rsp.err_msg.encode('utf-8')))
        return rsp

    #
    # 充值接口
    # 参数：cardid：充值卡号  cardkey：充值卡签名串
    # 返回值：
    #   rsp.ret_code：正常返回0
    #   rsp.err_msg：异常时返回异常详情
    #
    def Charge(self, cardid, cardkey):
        tm          = str( int(time.time()))
        sign        = CalcSign( self.pd_id, self.pd_key, tm)
        csign       = CalcCardSign(cardid, cardkey, tm, self.pd_key)
        param       = {
                "user_id": self.pd_id,
                "timestamp":tm,
                "sign":sign,
                'cardid':cardid,
                'csign':csign
                }
        url     = self.host + "/api/charge"
        rsp     = HttpRequest(url, param)
        if rsp.ret_code == 0:
            LOG("charge succ ret: {} request_id: {} pred: {} err: {}".format( rsp.ret_code, rsp.request_id, rsp.pred_rsp.value, rsp.err_msg))
        else:
            LOG("charge failed ret: {} err: {}".format( rsp.ret_code, rsp.err_msg.encode('utf-8')))
        return rsp

    ##
    # 充值，只返回是否成功
    # 参数：cardid：充值卡号  cardkey：充值卡签名串
    # 返回值： 充值成功时返回0
    ##
    def ExtendCharge(self, cardid, cardkey):
        return self.Charge(cardid,cardkey).ret_code

    ##
    # 调用退款，只返回是否成功
    # 参数： request_id：需要退款的订单号
    # 返回值： 退款成功时返回0
    #
    # 注意:
    #    Predict识别接口，仅在ret_code == 0时才会进行扣款，才需要进行退款请求，否则无需进行退款操作
    # 注意2:
    #   退款仅在正常识别出结果后，无法通过网站验证的情况，请勿非法或者滥用，否则可能进行封号处理
    ##
    def JusticeExtend(self, request_id):
        return self.Justice(request_id).ret_code

    ##
    # 查询余额，只返回余额
    # 参数：无
    # 返回值：rsp.cust_val：余额
    ##
    def QueryBalcExtend(self):
        rsp = self.QueryBalc()
        return rsp.cust_val

    ##
    # 从文件识别验证码，只返回识别结果
    # 参数：pred_type;识别类型  file_name:文件名
    # 返回值： rsp.pred_rsp.value：识别的结果
    ##
    def PredictFromFileExtend( self, pred_type, file_name, head_info = ""):
        rsp = self.PredictFromFile(pred_type,file_name,head_info)
        return rsp.pred_rsp.value

    ##
    # 识别接口，只返回识别结果
    # 参数：pred_type:识别类型  img_data:图片的数据
    # 返回值： rsp.pred_rsp.value：识别的结果
    ##
    def PredictExtend(self,pred_type, img_data, head_info = ""):
        rsp = self.Predict(pred_type,img_data,head_info)
        return rsp.pred_rsp.value



def TestFunc(path):
    pd_id           = "103604"     #用户中心页可以查询到pd信息
    pd_key          = "/Zea0wnIFe/cIivYNVpu4yjc+p/xEgk" #mark
    app_id          = "100001"     #开发者分成用的账号，在开发者中心可以查询到
    app_key         = "123456"
    #识别类型，
    #具体类型可以查看官方网站的价格页选择具体的类型，不清楚类型的，可以咨询客服
    pred_type       = "30400"
    api             = FateadmApi(app_id, app_key, pd_id, pd_key)
    # 查询余额
    balance 		= api.QueryBalcExtend()   # 直接返余额
    # api.QueryBalc()

    # 通过文件形式识别：
    file_name       = path
    # result =  api.PredictFromFileExtend(pred_type,file_name)   # 直接返回识别结果
    rsp             = api.PredictFromFile(pred_type, file_name)  # 返回详细识别结果
    return rsp.pred_rsp.value

if __name__ == "__main__":
    ip = SelectionIP()
    DOMTree = xml.dom.minidom.parse("inf.xml")
    collection = DOMTree.documentElement
    print("解析使用密码...")
    xmlUse = collection.getElementsByTagName("use")[0]
    key = xmlUse.getElementsByTagName("key")[0].childNodes[0].data
    Key(key)
    xmlUser = collection.getElementsByTagName("user")[0]
    studentnumber = xmlUser.getElementsByTagName('username')[0].childNodes[0].data
    print("账号", studentnumber)
    password = xmlUser.getElementsByTagName('password')[0].childNodes[0].data
    xmlClassNum = collection.getElementsByTagName('classPageNum')[0]
    totalPageNum = xmlClassNum.getElementsByTagName('totalNum')[0].childNodes[0].data
    info = Login(studentnumber,password,ip)
    if(info!="loerr"):
        xmlClassType = collection.getElementsByTagName("classType")[0]
        sports = xmlClassType.getElementsByTagName('type')[0].childNodes[0].data
        if(sports=="1"):
            Url = CrawlCourse(info[0],info[1],studentnumber,ip,totalPageNum)
            numListInput = input("输入课程序列号(如有多门则需用英文 , 隔开):")
            if "," in numListInput:
                numList = numListInput.split(",")
                waitSelectList = []
                for num in numList:
                    url = Url[int(num) - 1]
                    try:
                        timeListNum = PreparaParam(info[0], url)
                    except:
                        print("操作有误！此选择忽略！")
                        timeListNum = None
                    if timeListNum == "s":
                        print("网页三秒防刷..重试..若不成功将忽略...")
                        try:
                            timeListNum = PreparaParam(info[0], url)
                        except:
                            print("操作有误！此选择忽略！")
                            timeListNum = None
                    if timeListNum:
                        waitSelectList.append([url, timeListNum])
                print("输入完毕,开始准备参数列表...")
                time.sleep(5)
                threads = []
                for waitSelectInfo in waitSelectList:
                    url = waitSelectInfo[0]
                    timeListNum = waitSelectInfo[1]
                    newThread = threading.Thread(target=ExecutePost,args=(info[0], url, timeListNum))
                    newThread.start()
                    threads.append(newThread)
                    time.sleep(5)
                for thread in threads:
                    thread.join()
            else:
                url = Url[int(numListInput) - 1]
                try:
                    timeListNum = PreparaParam(info[0], url)
                except:
                    print("操作有误！此选择忽略！")
                    timeListNum = None
                if timeListNum == "s":
                    print("网页三秒防刷..重试..若不成功将忽略...")
                    try:
                        timeListNum = PreparaParam(info[0], url)
                    except:
                        print("操作有误！")
                        timeListNum = None
                if timeListNum:
                    ExecutePost(info[0], url, timeListNum)

        elif(sports=="2"):
            CrawlSportsCourse(info[0],info[1],studentnumber,ip)

        else:print("输入无效！")
        # select = input("是否打印当前课表(持久化至当前目录),是则输入1:")
        # if select == "1":
        #     SaveClass(info[0],info[1],studentnumber,ip)
