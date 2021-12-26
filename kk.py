#! python3

import requests, bs4, os, threading, re, time, tkinter, random
import publicDef
from rich import progress

threadFlag = 'start'
doneCaptersNum = 0
threadNum = 8
capterFile = []

def buttonFinish():
    global threadFlag
    threadFlag = 'finish'
    print('finish')
    global window
    window.destroy()

def buttonStop():
    global threadFlag
    threadFlag = 'stop' 
    print('stop')

def buttonStart():
    global threadFlag
    threadFlag = 'start'   
    print('start')

def showWindow():
    global window
    width = 25
    height = 3
    window = tkinter.Tk()
    window.title('down control')
    window.geometry('500x500')
    buttonFh = tkinter.Button(window, bg='red' ,text='停止\n（结束程序并退出）', width=width, height=height, command=buttonFinish)
    buttonSp = tkinter.Button(window, bg='yellow' ,text='暂停\n（使程序暂停）', width=width, height=height, command=buttonStop)
    buttonSt = tkinter.Button(window, bg='green' ,text='开始\n（在按暂停后使程序继续运行）', width=width, height=height, command=buttonStart)
    buttonSt.pack()
    buttonSp.pack()
    buttonFh.pack()
    window.mainloop() 
    

def downCapters(url, id, title, path, pageNum, num):
    global threadFlag
    driver = publicDef.setDriver()
    os.makedirs(path, exist_ok=True)
    jpgFiles = publicDef.getExistFileName(path, '.jpg')
    for i in range(pageNum):
        if threadFlag == 'stop':
            print('%s暂停中。'%(threading.current_thread()))
        while threadFlag == 'stop':            
            time.sleep(1)
        if threadFlag == 'finish':
            print('进去了，正在退出进程%s'%(threading.current_thread()))
            driver.quit()
            return
        pageName = str(i+1) + '.jpg'
        if pageName in jpgFiles:
            continue
        pageUrl = url + id[0:-1] + '-p' + str(i+1) + '/'
        pagePath = os.path.join(path, pageName)
        publicDef.reportInfor(path, '第%s个:%s:%s\n'%(str(num+1), title, pageUrl))
        tryTime = 3
        while(1):
            srcUrl = publicDef.getOneUrl(driver, pageUrl, '#cp_img img', 'src', -1, path)
            if srcUrl != 'fail' or tryTime == 0:
                break
            tryTime -= 1
        if srcUrl == 'fail':
            publicDef.reportInfor(path, '第%s个章节:%s\npageUrl:%s\nsrcUrl:%s\n下载失败!!!!!\n\n'%(str(num+1), title, pageUrl, srcUrl))
        else:
            publicDef.saveImg(srcUrl, pagePath)
            publicDef.reportInfor(path, '第%s个章节:%s\npageUrl:%s\nsrcUrl:%s\n下载成功。\n\n'%(str(num+1), title, pageUrl, srcUrl))
    driver.quit()

def getCapters(Semaphore, url, elems, comicID, i, captersNum):
    Semaphore.acquire()
    print('进入进程%s'%(threading.current_thread()))
    global threadFlag, doneCaptersNum
    if threadFlag == 'finish':
        print('没进去，正在退出进程%s'%(threading.current_thread()))
        Semaphore.release()
        return
    regex = re.compile(r'\d+')
    
    pageNum = elems[i].find('span').get_text()
    pageNum = int(regex.search(pageNum).group())
    title = publicDef.getTitle(elems, i)
    # 处理名称重复的情况
    global capterFile
    if title in capterFile:
        title = title + str(random.randint(100, 199))
    capterFile.append(title)

    title = str(captersNum) + ' ' +title.split('  ')[0] + ' 共' + str(pageNum) + '页'
    id = elems[i].get('href')
    path = os.path.join(comicID, title)
    downCapters(url, id, title, path, pageNum, i)
    Semaphore.release()
    doneCaptersNum += 1

def showMileage(capterNum):
    global threadFlag, doneCaptersNum
    while threadFlag != 'finish':
        if threadFlag == 'start':
            text = str(round(100*doneCaptersNum/capterNum, 2))
            print('%s%s(%d/%d)'%(text, '%', doneCaptersNum, capterNum))
        time.sleep(2)

def main():
    timeStart = time.time()   
    url  = 'https://www.mangabz.com'#
    comicID = '60bz'
    downloadThreads = []
    Semaphore = threading.BoundedSemaphore(threadNum)
    os.makedirs(comicID, exist_ok=True)
    
    elems = publicDef.getElems(url + '/' + comicID, '#chapterlistload a', 'UTF-8', comicID) 
    #print(len(elems))
    for i in range(len(elems)):
        captersNum = len(elems) - i
        downloadThread = threading.Thread(target=getCapters, args=(Semaphore, url, elems, comicID, i, captersNum)) # 'daemon=True' 避免按Ctrl C的时候，无法成功退出
        downloadThreads.append(downloadThread)
        downloadThread.start()
    # 百分比显示进度
    downloadThread = threading.Thread(target=showMileage, args=(len(elems), ))
    downloadThread.start()
    showWindow()
    for downloadThread in downloadThreads:
        downloadThread.join()   
    global threadFlag
    threadFlag = 'finish'
    timeEnd = time.time()       
    totalTime = time.strftime("%H:%M:%S", time.gmtime(round(timeEnd - timeStart)))
    print('共耗时%s'%(totalTime))

if __name__ == '__main__':
    main()
    




