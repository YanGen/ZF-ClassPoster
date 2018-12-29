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
        allowATime = datetime.datetime(2018, 12, 26, 1, 10, 10)  # ����ʹ��
        allowBTime = datetime.datetime(2018, 12, 27, 1, 10, 10)
        if datetime.datetime.now() > allowATime and datetime.datetime.now() < allowBTime:
            pass
        else:
            print("�����ܳ׿���ʱ�Σ�")
            Key(input("�������ܳ�: "))
    else:
        if key != "7ae7778c9ae86d2ded133e891995dc9e":
            if key != "36963":
                print("����")
                Key(input("�������ܳ�: "))

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
    print("������֤��", DstDir + "code.jpg")
    try:
        with open(DstDir + "code.jpg", "wb") as jpg:
            jpg.write(image)
    except IOError:
        print("IO Error\n")
    print("ʶ����...")
    if codeReco:
        code = TestFunc("code.jpg")
        print("���",code)

    else:
        code = input("�ֶ�������֤��: ")
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
        name = nameTag.get_text().replace("ͬѧ","")
    else:
        print("ʶ��ʧ��...")
        return Login(studentnumber,password,ip,codeReco = False)
    print ("��¼״̬��",res.status_code)
    print ("ȷ������--> ",name)
    if(res.status_code!=200):
        print ("��¼ʧ��,�˳�")
        return "logerr"
    return [req,name]


def CrawlCourse(req,name,studentnumber,ip,totalPageNum): # ѡ��
    print ("����׼���γ�����...")

    # ���ѧ��ѡ��
    # url = "http://10.10.240.26/xsxk.aspx?xh=%s&xm=%s&gnmkdm=N121101"%(studentnumber,str(name))
    url = "http://10.10.240.%s/xsxk.aspx?xh=%s&gnmkdm=N121101"%(ip,studentnumber)

    req.headers['Referer'] = "http://10.10.240.%s/xs_main.aspx?xh=%s" % (ip,studentnumber)
    req.headers['User-Agent'] = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36"
    res = req.get(url)
    value = re.compile("<input type=\"hidden\" name=\"__VIEWSTATE\" value=\"(.*?)\" />")
    value = re.findall(value,str(res.content))[0]
    zymc = re.compile("<input name=\"zymc\" type=\"text\" value=\"(.*?)\" readonly")
    zymc = re.findall(zymc, str(res.content))[0]


    # ���ѡ�޿γ�
    postdata = {
        "__VIEWSTATE": value,
        "zymc":zymc,
        "Button2":"ѡ�޿γ�",
    }
    req.headers['Referer'] = url
    res = req.post(url, data=postdata)
    value = re.compile("<input type=\"hidden\" name=\"__VIEWSTATE\" value=\"(.*?)\" />")
    value = re.findall(value, str(res.content))[0]
    # ���ѡ�޿γ�
    postdata = {
        "__VIEWSTATE": value,
        "Button7": "����ѡ��",
    }
    waitClas = []
    # �������ѡ��
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
    print ("��:"+str(len(Page)+1)+"ҳ")

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
        print ("���к�:"+str(ind+1)+" �γ�:"+str(waitClas[ind].get_text()))
        Link = re.compile("window.open\(\'(.*?)\',")
        link = re.findall(Link,str(waitClas[ind]['onclick']))[0]
        url = "http://10.10.240."+ip+"/"+ link
        Url.append(url)
    print("---------------------------------")
    return Url

def CrawlSportsCourse(req,name,studentnumber,ip):
    print("���ڲɼ���ѡʱ��...")
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
        print("���к�: "+str(i)+"."+option["value"])
    num = input("����ʱ�����к�:")
    option = Option[int(num) - 1]
    print("ѡ��" + option['value'])
    print("����׼���������б�...")
    # ģ����ʱ��ѡ��
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
        print("���к�: "+str(i+1)+"."+str(Td[2*i].get_text()+"---"+Td[2*i+1].get_text()))
    print("-----------------------------------")
    num = int(input("ѡ��:"))
    postdata = {
        "__VIEWSTATE":value,
        "kj":option['value'],
        "Button1": " �� �� ",
        "kcmcGrid:_ctl%s:xk"%str(num+1):"on",
    }
    Y = int(datetime.datetime.now().year)
    M = int(datetime.datetime.now().month)
    D = int(datetime.datetime.now().day)
    startTime = datetime.datetime(Y, M, D, 12, 58, 40)  # ��������ʱ��
    print(str(startTime) + "��ִ��ѡ�β���")
    while datetime.datetime.now() < startTime:
        time.sleep(0.5)
    print('Action now starts on %s' % startTime)
    while (1):
        try:
            res = req.post(url, data=postdata, timeout=1)
            html = str(res.content, "utf-8")
        except:
            print("���ӳ�ʱ,��������")
        if html.count("�ɹ�") != 0:
            print("����ɹ�������")
            print("����ɹ�������")
            print("����ɹ�������")
            break
        elif html.count("ѡ��ʱ��") != 0:
            print("ϵͳ��ʾʱ��δ��,�ٴ�����")
        elif html.count("����") != 0:
            print("������������,ʧ��~")
            break

def CrawlPage(req,name,studentnumber,postdata,ip):
    url = "http://10.10.240.%s/xsxk.aspx?xh=%s&xm=%s&gnmkdm=N121101"%(ip,studentnumber,name)
    res = req.post(url,data=postdata)
    value = re.compile("<input type=\"hidden\" name=\"__VIEWSTATE\" value=\"(.*?)\" />")
    value = re.findall(value, str(res.content))[0]
    soup = BeautifulSoup(res.content, 'html.parser')
    Td = soup.find_all("a", href="#")
    return [value,Td]

# ׼������
def PreparaParam(req,url):
    print("\n3������")
    time.sleep(3)
    req.headers['Referer'] = url
    res = req.get(url)
    html = str((res.content), "utf-8")
    if "�����ˢ" in html:
        return "s"
    classNameSearch = re.compile("�γ����ƣ�(.*?)ѧ��").findall(html)
    className = ""
    if len(classNameSearch)!=0:
        className = classNameSearch[0].replace("&nbsp;","")
    print("���� "+className+" �Ĵ�ѡʱ�����к�")
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
            print("���к�: " + str(j) + "." + str(Teacher[j - 1]))
        except:
            print("���к�: " + str(j) + "���������޷���ʾ")
        Axkkh.append(xkkh)
    num = int(input("���к�:"))
    return num

# ִ��ѡ��
def ExecutePost(req,url,num):
    req.headers['Referer'] = url
    res = req.get(url)
    html = str((res.content),"utf-8")
    if "�����ˢ" in html:
        print("�����ˢ...")
    classNameSearch = re.compile("�γ����ƣ�(.*?)ѧ��").findall(html)
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
    startTime = datetime.datetime(2018, M, D, 12, 58, 50)  # ����ʱ��
    print(className+" ѡ�β���׼�����!",str(startTime)+"��ִ��ѡ�β���")

    while datetime.datetime.now() < startTime:
        time.sleep(0.5)

    print(className ,'�߳����� %s' % datetime.datetime.now())

    while(1):
        try:
            res = req.post(url,data=postdata,timeout=1)
            html = str(res.content,"utf-8")
        except:
            print("���ӳ�ʱ,��������")
            pass
        if html.count("�ɹ�") != 0:
            print(className ,"ѡ�γɹ�������")
            print(className ,"ѡ�γɹ�������")
            print(className ,"ѡ�γɹ�������\n")
            break
        elif html.count("ѡ��ʱ��")!=0:
            print (className ,"ϵͳ��ʾʱ��δ��,�ٴ�����\n")
        elif html.count("����")!=0:
            print (className ,"������������,ʧ��~\n")
            break

def SaveClass(req,name,studentnumber,ip):
    # ��ӡ�α�

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
    # ����Ҫ����ʱ��ע�͵���־�Ϳ�����
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
    # API�ӿڵ�����
    # ������appID��appKey��pdID��pdKey��
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
    # ��ѯ���
    # ��������
    # ����ֵ��
    #   rsp.ret_code����������0
    #   rsp.cust_val���û����
    #   rsp.err_msg���쳣ʱ�����쳣����
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
    # ��ѯ�����ӳ�
    # ������pred_type:ʶ������
    # ����ֵ��
    #   rsp.ret_code����������0
    #   rsp.err_msg�� �쳣ʱ�����쳣����
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
    # ʶ����֤��
    # ������pred_type:ʶ������  img_data:ͼƬ������
    # ����ֵ��
    #   rsp.ret_code����������0
    #   rsp.request_id��Ψһ������
    #   rsp.pred_rsp.value��ʶ����
    #   rsp.err_msg���쳣ʱ�����쳣����
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
    # ���ļ�������֤��ʶ��
    # ������pred_type;ʶ������  file_name:�ļ���
    # ����ֵ��
    #   rsp.ret_code����������0
    #   rsp.request_id��Ψһ������
    #   rsp.pred_rsp.value��ʶ����
    #   rsp.err_msg���쳣ʱ�����쳣����
    #
    def PredictFromFile( self, pred_type, file_name, head_info = ""):
        with open(file_name, "rb") as f:
            data = f.read()
        return self.Predict(pred_type,data,head_info=head_info)

    #
    # ʶ��ʧ�ܣ������˿�����
    # ������request_id����Ҫ�˿�Ķ�����
    # ����ֵ��
    #   rsp.ret_code����������0
    #   rsp.err_msg���쳣ʱ�����쳣����
    #
    # ע��:
    #    Predictʶ��ӿڣ�����ret_code == 0ʱ�Ż���пۿ����Ҫ�����˿����󣬷�����������˿����
    # ע��2:
    #   �˿��������ʶ���������޷�ͨ����վ��֤�����������Ƿ��������ã�������ܽ��з�Ŵ���
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
    # ��ֵ�ӿ�
    # ������cardid����ֵ����  cardkey����ֵ��ǩ����
    # ����ֵ��
    #   rsp.ret_code����������0
    #   rsp.err_msg���쳣ʱ�����쳣����
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
    # ��ֵ��ֻ�����Ƿ�ɹ�
    # ������cardid����ֵ����  cardkey����ֵ��ǩ����
    # ����ֵ�� ��ֵ�ɹ�ʱ����0
    ##
    def ExtendCharge(self, cardid, cardkey):
        return self.Charge(cardid,cardkey).ret_code

    ##
    # �����˿ֻ�����Ƿ�ɹ�
    # ������ request_id����Ҫ�˿�Ķ�����
    # ����ֵ�� �˿�ɹ�ʱ����0
    #
    # ע��:
    #    Predictʶ��ӿڣ�����ret_code == 0ʱ�Ż���пۿ����Ҫ�����˿����󣬷�����������˿����
    # ע��2:
    #   �˿��������ʶ���������޷�ͨ����վ��֤�����������Ƿ��������ã�������ܽ��з�Ŵ���
    ##
    def JusticeExtend(self, request_id):
        return self.Justice(request_id).ret_code

    ##
    # ��ѯ��ֻ�������
    # ��������
    # ����ֵ��rsp.cust_val�����
    ##
    def QueryBalcExtend(self):
        rsp = self.QueryBalc()
        return rsp.cust_val

    ##
    # ���ļ�ʶ����֤�룬ֻ����ʶ����
    # ������pred_type;ʶ������  file_name:�ļ���
    # ����ֵ�� rsp.pred_rsp.value��ʶ��Ľ��
    ##
    def PredictFromFileExtend( self, pred_type, file_name, head_info = ""):
        rsp = self.PredictFromFile(pred_type,file_name,head_info)
        return rsp.pred_rsp.value

    ##
    # ʶ��ӿڣ�ֻ����ʶ����
    # ������pred_type:ʶ������  img_data:ͼƬ������
    # ����ֵ�� rsp.pred_rsp.value��ʶ��Ľ��
    ##
    def PredictExtend(self,pred_type, img_data, head_info = ""):
        rsp = self.Predict(pred_type,img_data,head_info)
        return rsp.pred_rsp.value



def TestFunc(path):
    pd_id           = "103604"     #�û�����ҳ���Բ�ѯ��pd��Ϣ
    pd_key          = "/Zea0wnIFe/cIivYNVpu4yjc+p/xEgk9"
    app_id          = "100001"     #�����߷ֳ��õ��˺ţ��ڿ��������Ŀ��Բ�ѯ��
    app_key         = "123456"
    #ʶ�����ͣ�
    #�������Ϳ��Բ鿴�ٷ���վ�ļ۸�ҳѡ���������ͣ���������͵ģ�������ѯ�ͷ�
    pred_type       = "30400"
    api             = FateadmApi(app_id, app_key, pd_id, pd_key)
    # ��ѯ���
    balance 		= api.QueryBalcExtend()   # ֱ�ӷ����
    # api.QueryBalc()

    # ͨ���ļ���ʽʶ��
    file_name       = path
    # result =  api.PredictFromFileExtend(pred_type,file_name)   # ֱ�ӷ���ʶ����
    rsp             = api.PredictFromFile(pred_type, file_name)  # ������ϸʶ����
    return rsp.pred_rsp.value

if __name__ == "__main__":
    ip = SelectionIP()
    DOMTree = xml.dom.minidom.parse("inf.xml")
    collection = DOMTree.documentElement
    print("����ʹ������...")
    xmlUse = collection.getElementsByTagName("use")[0]
    key = xmlUse.getElementsByTagName("key")[0].childNodes[0].data
    Key(key)
    xmlUser = collection.getElementsByTagName("user")[0]
    studentnumber = xmlUser.getElementsByTagName('username')[0].childNodes[0].data
    print("�˺�", studentnumber)
    password = xmlUser.getElementsByTagName('password')[0].childNodes[0].data
    xmlClassNum = collection.getElementsByTagName('classPageNum')[0]
    totalPageNum = xmlClassNum.getElementsByTagName('totalNum')[0].childNodes[0].data
    info = Login(studentnumber,password,ip)
    if(info!="loerr"):
        xmlClassType = collection.getElementsByTagName("classType")[0]
        sports = xmlClassType.getElementsByTagName('type')[0].childNodes[0].data
        if(sports=="1"):
            Url = CrawlCourse(info[0],info[1],studentnumber,ip,totalPageNum)
            numListInput = input("����γ����к�(���ж���������Ӣ�� , ����):")
            if "," in numListInput:
                numList = numListInput.split(",")
                waitSelectList = []
                for num in numList:
                    url = Url[int(num) - 1]
                    try:
                        timeListNum = PreparaParam(info[0], url)
                    except:
                        print("�������󣡴�ѡ����ԣ�")
                        timeListNum = None
                    if timeListNum == "s":
                        print("��ҳ�����ˢ..����..�����ɹ�������...")
                        try:
                            timeListNum = PreparaParam(info[0], url)
                        except:
                            print("�������󣡴�ѡ����ԣ�")
                            timeListNum = None
                    if timeListNum:
                        waitSelectList.append([url, timeListNum])
                print("�������,��ʼ׼�������б�...")
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
                    print("�������󣡴�ѡ����ԣ�")
                    timeListNum = None
                if timeListNum == "s":
                    print("��ҳ�����ˢ..����..�����ɹ�������...")
                    try:
                        timeListNum = PreparaParam(info[0], url)
                    except:
                        print("��������")
                        timeListNum = None
                if timeListNum:
                    ExecutePost(info[0], url, timeListNum)

        elif(sports=="2"):
            CrawlSportsCourse(info[0],info[1],studentnumber,ip)

        else:print("������Ч��")
        # select = input("�Ƿ��ӡ��ǰ�α�(�־û�����ǰĿ¼),��������1:")
        # if select == "1":
        #     SaveClass(info[0],info[1],studentnumber,ip)
