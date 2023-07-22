
from fake_useragent import UserAgent
import csv
import time
import random
import requests
import traceback
from lxml import etree
import pandas as pd


def main():
    # define the page number in each area
    for page in range(1,2):
        url = f'https://www.trademe.co.nz/a/property/residential/rent/canterbury/christchurch-city?page={page}'
        try:
            time.sleep(random.uniform(1, 2))
            response = requests.get(url, headers=headers, timeout=25)
            print(response)
            # response = requests.get(url, timeout=5)
            response.raise_for_status()
        except requests.exceptions.Timeout:
            print("Timeout error, website took too long to respond.")
        except requests.exceptions.RequestException as e:
            print("Error: ", e)
        else:
            html = response.text

            root = etree.HTML(html)
            hrefs = ''.join(root.xpath('/html/body/tm-root/div[1]/main/div/tm-property-search-component/div/div[1]/tm-property-search-results/div/div[3]/tm-search-results/div/div[2]/tg-row/tg-col[3]/tm-search-card-switcher/tm-property-premium-listing-card/div/a/@href'))

            # output
            print(hrefs)

if __name__ == '__main__':
    ua = UserAgent(verify_ssl=False)

    # debug only
    #headers = {"User-Agent": ua.random}

    # debug only
    # headers= {
    # "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",}

    #ok 
    headers = {
    'User-Agent': "Mozilla / 5.0(Windows NT 10.0;Win64;x64) AppleWebKit / 537.36(KHTML, likeGecko) Chrome / 96.0.4664 .93 Safari / 537.36",
    # "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
    }

    # url = f'https://www.fz0752.com/project/list.shtml?state=&key=&qy=46&area=&danjia=&func=&fea=&type=&kp=&mj=&sort=&pageNO=1'
    # response = requests.get(url, headers=headers)#之前请求房屋网站的请求
    # print(response.text)



    print(headers)
    # time.sleep(random.uniform(1, 2))
    main()



