#! python3
import os, requests, bs4, re, time, tkinter, threading
from selenium import webdriver
import kk


def getExistFileName(keyWord, judgeId):
    pdfFiles = []
    for filename in os.listdir(os.path.join(keyWord, '.')):
        if filename.endswith(judgeId):
            pdfFiles.append(filename)
    return pdfFiles

def saveImg(url, path):
    res = requests.get(url)
    res.raise_for_status
    with open(path,'wb') as imageFile:
        for chunk in res.iter_content(100000):
            imageFile.write(chunk)



def  reportInfor(keyWord, str):
    print(str) 
    with open(os.path.join(keyWord, 'report.txt'), 'a') as reportFile:
        reportFile.write(str)

def getOneUrl(driver, url, selectAl, getAl, pos, path):
    try:
        driver.get(url)
        time.sleep(5)
        data = driver.page_source
        soup = bs4.BeautifulSoup(data, 'html.parser')
        return soup.select(selectAl)[pos].get(getAl) 
    except Exception as err:
        with open(os.path.join(path, 'err.txt'), 'a') as reportFile:
            reportFile.write('错误是:%s'%(str(err)))
        return 'fail'

def getElems(url, selectAL, codingWord, path):
    try:
        res = requests.get(url)
        res.encoding = codingWord
        res.raise_for_status
        soup = bs4.BeautifulSoup(res.text, features="html.parser")
        return soup.select(selectAL)
    except Exception as err:
        with open(os.path.join(path, 'err.txt'), 'a') as reportFile:
            reportFile.write('错误是:%s'%(str(err)))
        return 'fail'


def getTitle(elems, i):
    regex = re.compile(r'[/:*?"<>|]')  # \ 处理不了
    name = elems[i].get('title')
    if not name:
        name = elems[i].get_text()
    name = name.strip()
    name = regex.sub('_',name)
    return name


def setDriver():
    options = webdriver.ChromeOptions()
    options.headless = True # 使浏览器不打开界面运行
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    return webdriver.Chrome(options=options) 


