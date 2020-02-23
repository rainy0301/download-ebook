# -*- coding:utf-8 -*-

from requests import Session
import time 
import json
from urllib import parse
from bs4 import BeautifulSoup 
from send_email import send_mail

s = Session()

def search_book(name):
    headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36'
    ,'Host':'www.jiumodiary.com',
    'Origin': 'https://www.jiumodiary.com'
    }
    data = {
        'q': name+' mobi',
        'remote_ip':'' ,
        'time_int': int(time.time())*1000
    }
    url1 = 'https://www.jiumodiary.com/init_hubs.php'
    p = s.post(url1, headers=headers, data=data)
    id1 = json.loads(p.text)['id']
    url2 = 'https://www.jiumodiary.com/ajax_fetch_hubs.php'
    search_result = []
    js1 = {
            'id': id1,
            'set': 0
                }
    p2 = s.post(url2,headers=headers,data=js1)
    js2 = json.loads(p2.text)['sources']
    # print(u,len(js2))
    for x in range(len(js2)):
        dts = js2[x]['details']['data']
        for i in range(len(dts)):
            result = dts[i]
            title = result.get('title')
            link = result.get('link')
            size = result.get('des')
            if name in title:
                search_result.append([title,size,link])
                # print(x, title,size,link)

    return search_result

# 下载 ctfile
def get_ctfile_download_url(dow_url):
    # dow_url = 'https://u15169360.ctfile.com/fs/15169360-371840128'
    u_fid = dow_url.split('/')[-1]
    
    s = Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36'
        }
    p = s.get(dow_url,headers=headers)

    headers2 = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36'
        ,'Host': 'webapi.400gb.com',
        'Origin': 'https://545c.com',
        'Referer': 'https://545c.com/file/15169360-371840128'
    }
    dow_url2 = f'https://webapi.400gb.com/getfile.php?f={u_fid}&passcode=&ref='
    p = s.get(dow_url2,headers=headers2)
    file_info = json.loads(p.text)
    
    # uid, fid = u_fid.split('-')
    file_data = {
        'uid': file_info['userid'],
        'fid': file_info['file_id'],
        'folder_id': 0,
        'file_chk': file_info['file_chk'],
        'mb': 0,
        'app': 0,
        'acheck': 1,
        'verifycode':'',
        'rd': 0.4682700509051265
    }

    dow_url3 = 'https://webapi.400gb.com/get_file_url.php'
    p2 = s.get(dow_url3,headers=headers2,params=file_data)
    dow_url4 = json.loads(p2.text)['downurl']
    l = dow_url4.split('?')[0].split('/')[-1].split('.')
    ext = l[-1]
    name = '.'.join(l[:-1])
    # name,ext = dow_url4.split('?')[0].split('/')[-1].split('.')
    name = parse.unquote(name)
    name = name+'.'+ext
    return dow_url4, name


def DownOneFile(srcUrl, localFile):
    print('\n Downloading--->>>\n  %s' % (localFile))
    
    startTime = time.time()
    with s.get(srcUrl, stream=True) as r:
        contentLength = int(r.headers['content-length'])
        line = 'content-length: %dB/ %.2fKB/ %.2fMB'
        line = line % (contentLength, contentLength/1024, contentLength/1024/1024)
        print(line)
        downSize = 0
        with open('./books/'+localFile, 'wb') as f:
            for chunk in r.iter_content(8192):
                if chunk:
                    f.write(chunk)
                downSize += len(chunk)
                line = '%d KB/s - %.2f MB， 共 %.2f MB'
                line = line % (downSize/1024/(time.time()-startTime), downSize/1024/1024, contentLength/1024/1024)
                print(line, end='\r')
                if downSize >= contentLength:
                    break
        timeCost = time.time() - startTime
        line = '共耗时: %.2f s, 平均速度: %.2f KB/s'
        line = line % (timeCost, downSize/1024/timeCost)
        print(line)
        return 'ok'

def down_libgen_book(book_url):
    headers = {
    # 'Host': 'libgen.is',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36'
    }
    s = Session()
    # book_url = books[0][2]
    p = s.get(book_url,headers=headers)
    bs = BeautifulSoup(p.text,'lxml')
    a_list = bs.find_all('td')
    for idx, x in enumerate(a_list):
        if 'Title' in x.text:
            title = a_list[idx+1].text
        if 'Extension' in x.text:
            ext = a_list[idx+1].text
    name = title+'.'+ext
    tb = bs.find('table').find_all('table')[-1]
    d_url_list = tb.find_all('a')[:2]
    for u in d_url_list:
        print('try: ',u.text)
        durl = u['href']
        main_url = '/'.join(durl.split('/')[:3])
        p1 = s.get(durl,headers=headers)
        bs1 = BeautifulSoup(p1.text,'lxml')
        if u.text=='Z-Library':
            u1 = main_url + bs1.find('table').find('table').find('h3').find('a')['href']
            p2 = s.get(u1,headers=headers)
            bs2 = BeautifulSoup(p2.text,'lxml')
            u2 = main_url+bs2.find(attrs={'class':"btn-group"}).find('a')['href']

        else:
            a = bs1.find('a')
            if 'http' in a['href']:
                dow_url4=a['href']
            else:
                dow_url4 = main_url+a['href']
            r = DownOneFile(dow_url4,name)
            if r=='ok':
                break

    return 'ok',name


if __name__ == "__main__":
    bname = input('Please input book name: ')
    books = search_book(bname)
    for idx, x in enumerate(books):
        print(idx,x[0],x[1],x[2])
    
    no = int(input('Please select a number: '))
    book_url = books[no][2]
    if 'ctfile.com' in book_url:
        d_url,name = get_ctfile_download_url(book_url)
        r = DownOneFile(d_url,name)
    elif 'libgen' in book_url:
        r,name = down_libgen_book(book_url)
    if r=='ok':
        print('发送邮件')
        ok = send_mail('test',att_file=[name],has_att=1,receiver='ivy_wangchen_5TJk0m@kindle.com')
        print(ok)



