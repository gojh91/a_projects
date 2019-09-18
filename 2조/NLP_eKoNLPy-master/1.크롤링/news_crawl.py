# -*- coding: utf-8 -*-
import re
import scrapy
from newscrawl.items import NewscrawlItem
from datetime import timedelta, date
from urllib import parse
import time
import random
from time import sleep



start_date = date(2015, 11, 1)
end_date = date(2017, 12, 31)
cnt_per_page = 10
keyword = "금리"

url_format = "https://search.naver.com/search.naver?date_from={0}&date_option=8&date_to={0}&dup_remove=1&nso=so%3Add%2Cp%3Afrom{0}to{0}&query={1}&sm=tab_pge&srchby=all&st=date&where=news&start={2}"
#https://search.naver.com/search.naver?date_from=20190712&date_option=8&date_to=20190712&dup_remove=1&nso=so%3Add%2Cp%3Afrom20190712to20190712&query=금리&sm=tab_pge&srchby=all&st=date&where=news&start=1
#https://search.naver.com/search.naver?date_from={0}&date_option=8&date_to={0}&dup_remove=1&nso=so%3Add%2Cp%3Afrom{0}to{0}&query={1}&sm=tab_pge&srchby=all&st=date&where=news&start={2}

class news_crawlSpider(scrapy.Spider):
    
    def daterange(start_date, end_date):
        for n in range(int ((end_date - start_date).days)):
            yield start_date + timedelta(n)
    name = 'newscrawl'
    allowed_domains = ['naver.com','yna.co.kr', 'einfomax.co.kr', 'edaily.co.kr']
    start_urls = []
    
    for single_date in daterange(start_date, end_date):
        start_urls.append(url_format.format(single_date.strftime("%Y%m%d"), keyword, 1))
    
    def parse(self, response):
        
        for href in response.xpath("//ul[@class='type01']/li/dl/dt/a/@href").extract() :
            #print(href)
            yield response.follow(href, self.parse_details)

        total_cnt = int(re.sub('[()전체건,]', '', response.xpath("//div[@class='title_desc all_my']/span/text()").get().split('/')[1]))
        query_str = parse.parse_qs(parse.urlsplit(response.url).query)
        currpage = int(query_str['start'][0]) 

        startdate = query_str['date_from'][0]
        print("=================== [" + startdate + '] ' + str(currpage) + '/' + str(total_cnt) + "===================") 
        if currpage  < total_cnt : 
            yield response.follow(url_format.format(startdate, keyword, currpage+10)   , self.parse)


    def parse_details(self, response):  
        item = NewscrawlItem()
        item['url'] = response.url
        content = ""
        title = ""
        if 'news.naver.com' in response.url:
            if (str(response.xpath("//div[@class= 'press_logo']/a/img/@title").get()) == '연합뉴스')  or (str(response.xpath("//div[@class= 'press_logo']/a/img/@title").get()) == '이데일리'):#or (str(response.xpath("//div[@class= 'press_logo']/a/img/@title").get()) == '연합인포맥스')
                title = str(response.xpath("//h3[@id = 'articleTitle']/text()").get())
                item['date'] = response.xpath("//span[@class= 't11']/text()").get().split(' ')[0]
                content = str(response.xpath("//div[@class='_article_body_contents']").extract())
                item['news_media'] = str(response.xpath("//div[@class= 'press_logo']/a/img/@title").extract())
            else:
                pass
        if 'yna' in response.url :
            if 'news.naver.com' in response.url:
                title = str(response.xpath("//h3[@id = 'articleTitle']/text()").get())
                item['date'] = response.xpath("//span[@class= 't11']/text()").get().split(' ')[0]
                content = str(response.xpath("//div[@class='_article_body_contents']").extract())
                item['news_media'] = str(response.xpath("//div[@class= 'press_logo']/a/img/@title").extract())
        
            title = str(response.xpath("//h1[@class='tit-article']/text()").get())
            item['date'] = response.xpath("//span[@class ='tt']/em/text()").get()
            content = str(response.xpath("//div[@class='article']/p/text()").extract())
            item['news_media'] = '연합뉴스'

        # elif 'einfomax' in response.url:
  
        #     title = str(response.xpath("//div[@class= 'article-head-title']/text()").get())
        #     item['date'] = response.xpath("//ul[@class = 'no-bullet auto-marbtm-0 line-height-6']/li[2]/text()").get().split(' ')[2]
        #     content = str(response.xpath("//div[@id = 'article-view-content-div']/text()").extract())
        #     item['news_media'] = '연합인포멕스'
        elif 'edaily' in response.url:
            if 'news.naver.com' in response.url:
                title = str(response.xpath("//h3[@id = 'articleTitle']/text()").get())
                item['date'] = response.xpath("//span[@class= 't11']/text()").get().split(' ')[0]
                content = str(response.xpath("//div[@class='_article_body_contents']").extract())
                item['news_media'] = str(response.xpath("//div[@class= 'press_logo']/a/img/@title").extract())
        
            content = str(response.xpath("//div[@class= 'news_body']").extract())
            title = str(response.xpath("//div[@class= 'news_titles']/h2").extract())
            item['news_media'] = '이데일리'
            item['date'] = str(response.xpath('//*[@id="contents"]/section[1]/section[1]/div[1]/div[1]/div/div/ul/li[1]/p[1]/text()').extract()).split(' ')[1]


        else:
            pass
            #yield response.request(self.parse)
        title = re.sub(' +', ' ', str(re.sub(re.compile('<.*?>'), ' ', title.replace('"','')).replace('\r\n','').replace('\n','').replace('\t','').replace('\u200b','').replace('\\n','').replace('\\r', '').replace('\\t','').strip()))
        content = re.sub(' +', ' ', str(re.sub(re.compile('<.*?>'), ' ', content.replace('"','')).replace('\r\n','').replace('\n','').replace('\t','').replace('\u200b','').replace('\\n','').replace('\\r', '').replace('\\t','').strip()))
        
        item['content'] = content
        item['title'] = title
        if title != '':
            yield item
