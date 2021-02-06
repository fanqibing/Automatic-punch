# -*- coding: utf8 -*-
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
import time
import smtplib
from email.mime.text import MIMEText
from email.header import Header
##################### 用户信息 #########################
#如需增减人数，请直接修改usernames，passwords，names，receivers字段
usernames = ["XXX","XXX","XXX"]#学号
passwords = ["XXX","XXX","XXX"]#智慧理工密码
names = ['XXX','XXX','XXX']#用户姓名(用于推送给用户)
receivers = ['XXX@qq.com','XXX@qq.com','XXX@qq.com'] # 收件人邮箱，可设置为QQ邮箱或者其他邮箱，发送的邮件可能会进入用户垃圾箱
Errors = [1]*len(usernames)#记录异常
Clocked = [0]*len(usernames)#记录打卡情况
######################################################

############## 浏览器设置  #####################
url = "http://ids.njust.edu.cn/authserver/login?service=http%3A%2F%2Fehall.njust.edu.cn%2Flogin%3Fservice%3Dhttp%3A%2F%2Fehall.njust.edu.cn%2Fnew%2Findex.html"#智慧理工登录网址
chrome_options = Options()
#因为在云服务器上运行，去除可视界面，如需显示可视界面，将下面6行代码注释掉
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('window-size=1920x3000')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--hide-scrollbars')
chrome_options.add_argument('blink-settings=imagesEnabled=false')
chrome_options.add_argument('--headless')
###############################################

################### 发邮件.h ###################
mail_host = "smtp.qq.com"  # 设置qq服务器
mail_user = "XXX@qq.com"  # 发送人邮箱
mail_pass = "XXX"  # 授权码，注意是授权码，非QQ密码，如何获取授权码，请参阅https://jingyan.baidu.com/article/ac6a9a5eb439f36b653eacc0.html
sender = 'XXX@qq.com' # 发件人邮箱,注意和mail_user一致
####################################################
test_times = 1 #打卡失败后重复次数=test_times+1=2
#test(driver)功能：测试系统是否还能填写
def test(driver):
    try:
        # 页面加载前先等待最大20s，每0.5s检测一次是否已经可以定位到元素，若可以，跳过等待，程序继续进行
        # 点击搜索框，进入新页面
        WebDriverWait(driver, 20 , 0.5).until(
            EC.presence_of_element_located((By.ID,"ampHeaderSearchResult"))
        ).click()
        # 鼠标悬停到向”理“报平安按钮上，加载出选项然后点击
        above = WebDriverWait(driver,30,0.5).until(
            EC.presence_of_element_located((By.XPATH,'//*[@id="ampServiceCenterSearchApps"]/div[6]/div/div[22]/div[2]/div[2]/div[2]/div[1]'))
        )
        time.sleep(2)
        ActionChains(driver).move_to_element(above).perform()
        time.sleep(2)
        driver.find_element_by_xpath('//*[@id="ampServiceCenterSearchApps"]/div[6]/div/div[22]/div[2]/div[1]/span').click()
        time.sleep(2)
        #获取当前浏览器标签数
        num = driver.window_handles
        #如果浏览器新打卡了标签页，转换到最新打开的标签页，否则会默认在原来标签页，导致元素搜索失败
        driver.switch_to.window(num[len(num)-1])
        WebDriverWait(driver,30,0.5).until(
            EC.element_to_be_clickable((By.XPATH,'//*[@id="V1_CTRL173"]'))
        )
        return 1
    except:
        return 0
#test_clocked()函数功能：测试是否打卡/是否打卡成功
def test_clocked(driver,test_times):
    while (test_times >= 0 and test(driver) == 0):
        if (test_times == 0):
            return 0 #表示已打卡
        else:
            test_times = test_times - 1
            driver.implicitly_wait(10) #第二次开始隐式等待10s
            driver.get("http://ehall.njust.edu.cn/new/index.html")
    return 1 #表示未打卡
#多个用户打卡程序
for i in range(len(usernames)):
    try:
        driver = webdriver.Chrome(r'/usr/bin/chromedriver', options=chrome_options)#第一个参数是linux驱动安装位置
        driver.get(url)#登录智慧理工
        time.sleep(2)#为网页加载预留时间，防止还没加载完就搜索元素导致搜索不到

        driver.find_element_by_id("username").send_keys(usernames[i])#通过id识别到账号输入框，并输入账号信息

        driver.find_element_by_id("password").send_keys(passwords[i])#通过id识别到密码输入框，并输入密码

        driver.find_element_by_xpath('//*[@id="casLoginForm"]/p[5]/button').click()#通过xpath路径识别”登录“按钮，并模拟点击

        print("登录成功")
        #首先验证是否已经打过卡了
        if(test_clocked(driver,test_times)==0):
            driver.quit()
            print("对不起",names[i],"已经打过卡了")
            Clocked[i]=1
            try:
                mail_content = names[i]+"已经打过卡了"  # 邮件内容
                message = MIMEText(mail_content, 'plain', 'utf-8')
                message['Subject'] = Header('python发邮件', 'utf-8')  # 邮件主题
                message['From'] = Header("FQB's assistant", 'utf-8')  # 发件人昵称
                message['To'] = Header("我是收件人", 'utf-8')  # 收件人昵称
                smtp = smtplib.SMTP_SSL(mail_host)  # SMTP_SSL默认使用465端口
                smtp.login(mail_user, mail_pass)
                smtp.sendmail(sender, receivers[i], message.as_string())  # 发送邮件
                print(names[i],"邮件发送成功")
            except smtplib.SMTPException:
                print("Error: 无法发送邮件")
                Errors[i] = 0
            continue#直接为下一个用户开始打卡
        #打卡程序，此时位于向“理”报平安界面，下述程序的动作仅填写页面中用户需要填写的项，不填写已经默认填写的项
        driver.find_element_by_xpath('//*[@id="V1_CTRL173"]').click()#点击，弹出下拉列表
        time.sleep(2)
        s = Select(driver.find_element_by_xpath('//*[@id="V1_CTRL173"]'))#选择下拉列表37.0
        s.select_by_value("37.0")
        time.sleep(2)
        driver.find_element_by_xpath('//*[@id="V1_CTRL109"]').click()#选择是否出现发热或呼吸道感染症状，选项为否
        time.sleep(2)
        driver.find_element_by_xpath('//*[@id="V1_CTRL126"]').click()#选择是否处于隔离状态，选项为“否”
        time.sleep(2)
        driver.find_element_by_xpath('//*[@id="V1_CTRL179"]').click()#选择所在地是否为中高风险地区，选项为“否”
        time.sleep(2)
        driver.find_element_by_xpath('//*[@id="V1_CTRL183"]').click()#选择所在地是否为中高风险地区所在设区市的其他地区，选项为“否”
        time.sleep(2)
        driver.find_element_by_xpath('//*[@id="V1_CTRL142"]').click()#勾选承诺
        time.sleep(2)
        driver.find_element_by_xpath('//div[@class="btns"]/ul[@class="btn_group btn_toEnd"]/li/a[contains(@id,"infoplus_action")]/nobr').click()#点击提交按钮
        time.sleep(5)
        driver.find_element_by_xpath('//button[@class="dialog_button default fr"]').click()#点击“好”，完成提交
        #通过重新登录->判断是否还能填写，来判断是否打卡成功，为保险起见，设置了循环2次登录
        if(test_clocked(driver,test_times)==0):
            print(names[i],"打卡成功")
            try:
                mail_content = names[i] + "打卡成功！"  # 邮件内容
                Clocked[i]=1
                message = MIMEText(mail_content, 'plain', 'utf-8')
                message['Subject'] = Header('python发邮件', 'utf-8')  # 邮件主题
                message['From'] = Header("FQB's assistant", 'utf-8')  # 发件人昵称
                message['To'] = Header("我是收件人", 'utf-8')  # 收件人昵称
                smtp = smtplib.SMTP_SSL(mail_host)  # SMTP_SSL默认使用465端口
                smtp.login(mail_user, mail_pass)
                smtp.sendmail(sender, receivers[i], message.as_string())  # 发送邮件
                print(names[i], "邮件发送成功")
            except smtplib.SMTPException:
                print("Error: 无法发送邮件")
                Errors[i]=0
        else:
            try:
                mail_content = names[i] + "打卡失败！请手动打卡"  # 邮件内容
                Clocked[i] = 0
                message = MIMEText(mail_content, 'plain', 'utf-8')
                message['Subject'] = Header('python发邮件', 'utf-8')  # 邮件主题
                message['From'] = Header("FQB's assistant", 'utf-8')  # 发件人昵称
                message['To'] = Header("我是收件人", 'utf-8')  # 收件人昵称
                smtp = smtplib.SMTP_SSL(mail_host)  # SMTP_SSL默认使用465端口
                smtp.login(mail_user, mail_pass)
                smtp.sendmail(sender, receivers[i], message.as_string())  # 发送邮件
                print(names[i], "邮件发送成功")
            except smtplib.SMTPException:
                print("Error: 无法发送邮件")
                Errors[i] = 0
    except:
        try:
            mail_content = names[i] + "打卡失败！请手动打卡"  # 邮件内容
            Clocked[i] = 0
            message = MIMEText(mail_content, 'plain', 'utf-8')
            message['Subject'] = Header('python发邮件', 'utf-8')  # 邮件主题
            message['From'] = Header("FQB's assistant", 'utf-8')  # 发件人昵称
            message['To'] = Header("我是收件人", 'utf-8')  # 收件人昵称
            smtp = smtplib.SMTP_SSL(mail_host)  # SMTP_SSL默认使用465端口
            smtp.login(mail_user, mail_pass)
            smtp.sendmail(sender, receivers[i], message.as_string())  # 发送邮件
            print(names[i], "邮件发送成功")
        except smtplib.SMTPException:
            print("Error: 无法发送邮件")
            Errors[i] = 0
    finally:
        driver.quit()
#最后一步，通过serve酱通知某个用户打卡详情，格式XXX1 打卡成功 邮件发送成功 XXX2 打卡成功 邮件发送成功 XXX3 打卡成功 邮件发送成功
try:
    driver = webdriver.Chrome(r'/usr/bin/chromedriver', options=chrome_options)
    states_clocked = ["打卡失败","打卡成功"]
    states = ["邮件发送失败","邮件发送成功"]
    print("已经将打卡统计信息发给FQB")
    #如何使用serve酱为自己推送消息：http://sc.ftqq.com/3.version，请修改下面的链接，否则发到我的微信上就比较尴尬了
    driver.get("https://sc.ftqq.com/SCU157098T204c342f4bb7d4db05fb3ae1fcb1fcb86017bebf171dc.send?text="+names[0]+" "+states_clocked[Clocked[0]]+" "+states[Errors[0]]+" "+names[1]+" "+states_clocked[Clocked[1]]+" "+states[Errors[1]]+" "+names[2]+" "+states_clocked[Clocked[2]]+" "+states[Errors[2]])
except :
    print("Error: 无法推送微信消息")