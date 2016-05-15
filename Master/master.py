# coding=utf-8
#!/usr/bin/python
import Queue
import sys
import webbrowser
import re
import request
import time
import bloomFilter
import urlparse
import formParse
import crawler
import checkVuln
import config.config as config
import scripts.sqli.bsqli_response_diff as bsqlitf
import scripts.sqli.bsqli_time_delay as bsqlitd
import scripts.sqli.sqli as sqli
from color_printer import colors
from bs4 import BeautifulSoup
from posixpath import normpath

def create_logfile(seedUrl):
    tup = urlparse.urlparse(seedUrl)
    host = tup.netloc
    now = time.localtime()
    dirName = 'log/'
    logName =dirName + host + '_'+ time.strftime('%Y%m%d%H%M%S',now)
    logfile = open(logName,'w')
    logfile .write('Target: '+ seedUrl + ' (GET)\n')
    logfile.close()
    return logName

def getCookie(loginUrl):
    colors.green('Do you want recording cookie?(y/N)')
    while True: 
        finish = raw_input('')
        i = finish.lower().lower() 
        if i == 'n' or i == '\n' or i == '\r' or i=='':
            return  {}
        else:
            break

    if loginUrl == '':
        return ''
    # recording cookie
    try:
        webbrowser.open_new(loginUrl)
    except Exception as err:
        pass
    colors.yellow( 'Please enter "Y" if you finishing recording cookie.')
    while True: 
        finish = raw_input('')
        if finish.lower() == 'y':
            break
        else:
            finish = ''
    # read cookie from cookieFile
    #print config.conf
    #cookieFileName = config.conf['CookieFileName']
    # cookieFileName = '/root/cntzapfile.txt'
    #print 'Read cookie from file: ',cookieFileName
    
    cookieTmp = open('cookie.txt','r').read()
    cookie = {}
    try:
        if len(cookieTmp.strip()) != 0:
            for line in cookieTmp.split(';'):
                name,value = line.strip().split('=',1)
                cookie[name] = value
        print 'cookie is:',cookie
    except Exception as err:
        pass
    return cookie


def start(baseUrl,seedUrl):
    #seed = Request(base='http://192.168.42.131/dvwa/index.php',url='http://192.168.42.131/dvwa/index.php',method='get')
    seed = request.Request(base=baseUrl,url=seedUrl,query={},method='get')
    #seed = request.Request(base='http://192.168.42.132/dvwa/',url='http://192.168.42.132/dvwa/',query={},method='get')
    colors.green( 'seed url: %s'%seed._url)
    logfileName = create_logfile(seed._url)
    cookie = getCookie(seed._url)
    # begin crawler
    tup = urlparse.urlparse(seed._url)
    netloc = tup.netloc # seed url 
    count = 0
    q = Queue.Queue()
    q.put(seed)
    bf = bloomFilter.BloomFilter(0.001,100000)
    # !!! need deal with seed._url
    bf.insert(seed._url)
    while(not q.empty()):
        req = q.get()
        req._cookies = cookie

        count += 1 
        print '------'
        if req._query != {} :
            colors.yellow('Check Vuln')
            checkVuln.start(req,logfileName)
        print '------'
        
        reqs = crawler.crawl(req)
        # test sqli vuln
        # prase url by bloomFilter and treeFilter ?++?
        for x in reqs:
            if not bf.exist(x._BFUrl):
                bf.insert(x._BFUrl)
                q.put(x)

    print "Number of url:",count
    f = open(logfileName,'r')
    x  = f.read()
    colors.green(x)


#if __name__ == "__main__":
if len(sys.argv) == 2:
    start(sys.argv[1],sys.argv[1])
else:
    colors.red('please input url!')
    sys.exit()