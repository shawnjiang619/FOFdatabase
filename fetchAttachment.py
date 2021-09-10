# 此程序将邮箱内基金净值附件下载到downloaded文件夹中
import imaplib, email, os
#import pandas as pd
import numpy as np
from email.header import decode_header
from datetime import date
from datetime import timedelta
from datetime import datetime as dt
import zipfile
import rarfile
import shutil
import os
import re
import logging
from datetime import timedelta
from apscheduler.schedulers.blocking import BlockingScheduler

# 邮箱向后搜索天数
num_days = 0

root = 'C:/Users/zhangguanglei/fof/'
downloaded_path = root + 'downloaded/'
comp_material_folder_path = root + 'company_material/'
archive_path = root + '/archive/'

temp_zip_path = downloaded_path + 'zipfolder/'

def append_date(filename):
    name, ext = os.path.splitext(filename)
    return "{name}_{uid}{ext}".format(name=name, uid='附件下载时间'+ str(dt.now().date()), ext=ext)

def validate_title(title):
    rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
    new_title = re.sub(rstr, "_", title)  # 替换为下划线
    return new_title

# unzip a file and get only excels
def handle_zip(zip_name):

    if os.path.splitext(zip_name)[-1] == ".zip":
        # unzip the entire zip file
        z = zipfile.ZipFile(downloaded_path + zip_name, 'r')
        z.extractall(temp_zip_path)
        z.close()
        os.remove(downloaded_path + zip_name)
    else:
        print("handling rar file...................")
        rarfile.UNRAR_TOOL = r"C:\Program Files\WinRar\UnRAR.exe"
        rf = rarfile.RarFile(downloaded_path + zip_name, 'r')
        rf.extractall(temp_zip_path)
        rf.close()
        os.remove(downloaded_path + zip_name)

    # only keep the excels
    for root_path, dir_names, file_names in os.walk(temp_zip_path):
        # print("xx", file_names)

        for fn in file_names:
            # srcDir 下面的所有文件(非目录)
            path = os.path.join(root_path, fn)
            print(path)

            print("before:", fn)
            # 处理文件乱码问题
            try:
                fn = fn.encode('cp437').decode('gbk')
            except:
                fn = fn.encode('utf-8').decode('utf-8')
            print("after:", fn)
            new_path = os.path.join(root_path, fn)
            shutil.move(path, new_path)
            print("new path: ", new_path)

            if fn.endswith(".xls") or fn.endswith(".xlsx"):
                # is excel, put in downloaded folder
                target = downloaded_path + fn
                shutil.move(new_path, target)
            else:
                # not excel, delete
                print(root_path)
                os.remove(new_path)


# 从邮箱下载由emailNum指定的邮件附件并下载到本地路径
# 只下载Excel文档
def download_attachment(emailNum, conn):

    _, data = conn.fetch (emailNum, '(RFC822)')
    print(type(data[0]))
    if data is None or data[0] is None:
        print("exiting b/c data is NONE")
        return
    emailbody = data[0][1]
    mail = email.message_from_bytes(emailbody)

    try:
        email_subject = decode_header(mail['subject'])[0][0].decode(decode_header(mail['subject'])[0][1])
    except:
        pass


    # 新建公司文件夹
    folder_path = comp_material_folder_path + validate_title(email_subject)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # 获取邮件附件名称
    for part in mail.walk():

        print(part.get_content_type())
        # multipart are just containers
        if part.get_content_maintype() == 'multipart': continue
        if part.get('Content-Disposition') is None:
            continue
        fileName = part.get_filename()
        print("got name: ", fileName)

        # 如果文件名为纯数字、字母时不需要解码，否则需要解码
        try:
            fileName = decode_header(fileName)[0][0].decode(decode_header(fileName)[0][1])
        except:
            pass

    # 如果获取到了格式为excel的文件，则将文件保存在指定的目录下
        print("now name: ", fileName)
        if fileName is not None:
            fileName = append_date(fileName)
            # 将文件归档，存入comp_material
            save_file_path = os.path.join(folder_path, fileName)
            if not os.path.isfile(save_file_path) :
                fp = open(save_file_path, 'wb')
                fp.write(part.get_payload(decode=True))
                fp.close()
            else:
                print("附件已经存在，文件名为：" + fileName)
                continue

            if (os.path.splitext(fileName)[-1] == ".xls" or
                                     os.path.splitext(fileName)[-1] == ".xlsx" or
                                     os.path.splitext(fileName)[-1] == ".xlsm" or
                                     os.path.splitext(fileName)[-1] == ".zip" or
                                     os.path.splitext(fileName)[-1] == ".rar"):

                file_path = os.path.join(downloaded_path, fileName)
                # filePath = os.path.join('/Users/jw/txfof/fof/downloaded', fileName)

                if not os.path.isfile(file_path):
                    fp = open(file_path, 'wb')
                    fp.write(part.get_payload(decode=True))
                    fp.close()
                    print("附件已经下载，文件名为：" + fileName)
                    # 如果为zip，处理一下
                    if os.path.splitext(fileName)[-1] == ".zip" or os.path.splitext(fileName)[-1] == ".rar":
                        handle_zip(fileName)
                else:
                    print("附件已经存在，文件名为：" + fileName)

    # 如果存档文件夹为空，删除文件夹
    if len(os.listdir(folder_path)) == 0:
        shutil.rmtree(folder_path)


def fetch_job():
    # 连接到qq企业邮箱，其他邮箱调整括号里的参数
    conn = imaplib.IMAP4_SSL("imap.exmail.qq.com", 993)
    print('已连接服务器')

    # 用户名、密码，登陆
    conn.login("fof@talentim.cn","TXteam2021")
    print('已登陆邮箱')

    # 在下载邮件之前我们必须先选择邮箱中的一个文件夹, 默认INBOX
    readonly = True
    conn.select("INBOX", readonly)

    # 提取了文件夹中自从昨天收到的邮件编号(脚本设置每天跑一次)
    # 通过调节timedelta param 来改变搜索时间范围

    # Get today's new email
    dtt = (date.today()  - timedelta(num_days)).strftime("%d-%b-%Y")
    #date = (date.today() - timedelta(50)).strftime("%d-%b-%Y")
    (_, data) = conn.search(None, "SINCE " + dtt)
    mails=data[0].split()
    print(mails)
    # 遍历搜索返回的邮件num，逐一下载邮件附件
    for i in mails:
        print("正在处理邮件: ", i)
        download_attachment(i, conn)
    # download_attachment(mails[2])
    # 结束连接，退出邮箱登录
    conn.close()
    conn.logout()

def cron_job():
    try:
        fetch_job()
    except Exception as e:
        print('Error occurred ' + str(e))
        logging.error('Error occurred ' + str(e) + "    " + str(dt.now()), exc_info=True)

if __name__ == '__main__':
    #fetch_job()
    logging.basicConfig(filename='fetch_app.log', level=logging.INFO)
    sched = BlockingScheduler()
    # 创建邮箱附件下载任务，每周一至周五的晚上7：00自动执行
    sched.add_job(cron_job, 'cron', day_of_week='mon-fri', hour=19, minute=00)
    sched.start()