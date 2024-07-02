import requests
from bs4 import BeautifulSoup
header={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'}
url='https://www.zdaye.com/free/?ip=&adr=&checktime=&sleep=&cunhuo=&dengji=&nadr=&https=1&yys=&post=&px='
def get_proxes():
    res=requests.get(url=url,headers=header)
    if res.status_code!=200:
        raise Exception('request proxies err')
    soup=BeautifulSoup(res.text,'html.parser')
    trList=soup.select("table[id='ipc'] tbody tr")
    proxies=[]
    for tr in trList:
        ip=tr.select_one("td:nth-child(1)").string
        port=tr.select_one("td:nth-child(2)").string
        post=tr.select_one("td:nth-child(7)").find('div')
        proxies.append({
            'https':f'{ip}:{port}',
            'post':False if post==None else True
        })
    return proxies