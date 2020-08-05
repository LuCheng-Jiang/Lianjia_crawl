from django.shortcuts import render

# Create your views here.
from homelink.forms import HouseChoiceForm

from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from .models import  HouseInfo
import re
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

import aiohttp   #启用异步爬虫
import asyncio
import time

def house_index(request):
    form = HouseChoiceForm()
    house_list = HouseInfo.objects.all().order_by('-add_date')
    if house_list:
        paginator = Paginator(house_list, 20)
        page = request.GET.get('page',1) #默认为1
        #每页显示20个
        currentPage = int(page)
        if currentPage - 5 < 1:
            pageRange = range(1, 15)  # 定义页码范围
        elif currentPage + 5 > paginator.num_pages:  # paginator.num_pages为总页数
            pageRange = range(currentPage - 14, paginator.num_pages + 1)
        else:
            pageRange = range(currentPage - 7, currentPage + 8)

        page_obj = paginator.get_page(page)

        Paginator.page_range = pageRange
        # print(paginator.num_pages)
        return render(request, 'homelink/index.html',
                      {'page_obj': page_obj, 'paginator': paginator,
                       'is_paginated': True, 'form': form,})
    else:
        return render(request,'homelink/index.html', {'form': form,})


def house_spider(request):
    if request.method == 'POST':
        form = HouseChoiceForm(request.POST)
        if form.is_valid():
            district = form.cleaned_data.get('district')
            price = form.cleaned_data.get('price')
            bedroom = form.cleaned_data.get('bedroom')
            url = 'https://sh.lianjia.com/ershoufang/{}/{}{}'.format(district, price, bedroom)

            #设置布隆过滤器
            from homelink.utils.filter_class import get_filter_class
            filter_obj = get_filter_class("memory")()

            if not filter_obj.is_exists(url):

                filter_obj.save(url)
                print("映射保存成功", url)

                home_spider = HomeLinkSpider(url)
                home_spider.get_max_page()
                home_spider.parse_page()
                home_spider.save_data_to_model()
                return HttpResponseRedirect('/homelink/')

            else:
                print("发现重复数据", url)
                # filter_obj.save(url)
                # # print("映射保存成功", url)
                #
                # home_spider = HomeLinkSpider(url)
                # home_spider.get_max_page()
                # home_spider.parse_page()
                # home_spider.save_data_to_model()
                # return HttpResponseRedirect('/homelink/')
                return HttpResponseRedirect('/homelink/')
        else:
            return HttpResponseRedirect('/homelink/')


class HomeLinkSpider(object):
    def __init__(self, url):
        self.ua = UserAgent()
        self.headers = {"User-Agent": self.ua.random}
        self.data = list()
        self.url = url


    def get_max_page(self):
        response = requests.get(self.url, headers=self.headers)
        if response.status_code == 200:

            soup = BeautifulSoup(response.text, 'html.parser')
            a = soup.select('div[class="page-box house-lst-page-box"]')
            max_page = eval(a[0].attrs["page-data"])["totalPage"] # 使用eval是字符串转化为字典格式
            return max_page
        else:
            print("请求失败 status:{}".format(response.status_code))
            return None

    # def parse_page(self):
    #     max_page = self.get_max_page()
    #     start =time.time()
    #     for i in range(1, max_page + 1):
    #         url = "{}pg{}/".format(self.url, i)
    #
    #         response = requests.get(url, headers=self.headers)
    #         soup = BeautifulSoup(response.text, 'html.parser')
    #         ul = soup.find_all("ul", class_="sellListContent")
    #         li_list = ul[0].select("li")
    #         for li in li_list:
    #             detail = dict()
    #             detail['title'] = li.select('div[class="title"]')[0].get_text()
    #
    #             # 大华锦绣华城(九街区)  | 3室2厅 | 76.9平米 | 南 | 其他 | 无电梯
    #             house_info = li.select('div[class="houseInfo"]')[0].get_text()
    #             house_info_list = house_info.split(" | ")
    #
    #             detail['house'] = house_info_list[0]
    #             detail['bedroom'] = house_info_list[1]
    #             detail['area'] = house_info_list[2]
    #             detail['direction'] = house_info_list[3]
    #
    #             # 低楼层(共7层)2006年建板楼  -  张江. 提取楼层，年份和板块
    #             position_info = li.select('div[class="positionInfo"]')[0].get_text().split(' - ')
    #
    #             floor_pattern = re.compile(r'.+\)')
    #             match1 = re.search(floor_pattern, position_info[0])  # 从字符串任意位置匹配
    #             if match1:
    #                 detail['floor'] = match1.group()
    #             else:
    #                 detail['floor'] = "未知"
    #
    #             year_pattern = re.compile(r'\d{4}')
    #             match2 = re.search(year_pattern, position_info[0])  # 从字符串任意位置匹配
    #             if match2:
    #                 detail['year'] = match2.group()
    #             else:
    #                 detail['year'] = "未知"
    #             detail['location'] = position_info[1]
    #
    #             # 650万，匹配650
    #             price_pattern = re.compile(r'\d+')
    #             total_price = li.select('div[class="totalPrice"]')[0].get_text()
    #             detail['total_price'] = re.search(price_pattern, total_price).group()
    #
    #             # 单价64182元/平米， 匹配64182
    #             unit_price = li.select('div[class="unitPrice"]')[0].get_text()
    #             detail['unit_price'] = re.search(price_pattern, unit_price).group()
    #             self.data.append(detail)
    #
    #     end = time.time()
    #     print("总共花了", end - start)

    async def parse(self,html):
        soup = BeautifulSoup(html, 'html.parser')
        ul = soup.find_all("ul", class_="sellListContent")
        li_list = ul[0].select("li")
        for li in li_list:
            detail = dict()
            detail['title'] = li.select('div[class="title"]')[0].get_text()

            # 大华锦绣华城(九街区)  | 3室2厅 | 76.9平米 | 南 | 其他 | 无电梯
            house_info = li.select('div[class="houseInfo"]')[0].get_text()
            house_info_list = house_info.split(" | ")

            detail['house'] = house_info_list[0]
            detail['bedroom'] = house_info_list[1]
            detail['area'] = house_info_list[2]
            detail['direction'] = house_info_list[3]

            # 低楼层(共7层)2006年建板楼  -  张江. 提取楼层，年份和板块
            position_info = li.select('div[class="positionInfo"]')[0].get_text().split(' - ')

            floor_pattern = re.compile(r'.+\)')
            match1 = re.search(floor_pattern, position_info[0])  # 从字符串任意位置匹配
            if match1:
                detail['floor'] = match1.group()
            else:
                detail['floor'] = "未知"

            year_pattern = re.compile(r'\d{4}')
            match2 = re.search(year_pattern, position_info[0])  # 从字符串任意位置匹配
            if match2:
                detail['year'] = match2.group()
            else:
                detail['year'] = "未知"
            detail['location'] = position_info[1]

            # 650万，匹配650
            price_pattern = re.compile(r'\d+')
            total_price = li.select('div[class="totalPrice"]')[0].get_text()
            detail['total_price'] = re.search(price_pattern, total_price).group()

            # 单价64182元/平米， 匹配64182
            unit_price = li.select('div[class="unitPrice"]')[0].get_text()
            detail['unit_price'] = re.search(price_pattern, unit_price).group()
            self.data.append(detail)

    async def fetch(self,session,url):
        async with session.get(url) as response:
            return await response.text()

    async def download(self,url):
        async with aiohttp.ClientSession() as session:
            html = await self.fetch(session,url)
            await self.parse(html)

    def parse_page(self):
        # max_page = self.get_max_page()
        #
        # loop = asyncio.get_event_loop()
        #
        # urls = ["{}pg{}/".format(self.url, i) for i in range(1,max_page + 1)]
        #
        # tasks = [asyncio.ensure_future(self.download(url)) for url in urls]
        #
        # tasks = asyncio.gather(*tasks)
        #
        # loop.run_until_complete(tasks)
        # start = time.time()

        max_page = self.get_max_page()
        #解决async 运行多线程时报错RuntimeError: There is no current event loop in thread 'Thread-3'
        """
        在主线程中，调用get_event_loop总能返回属于主线程的event loop对象，如果是处于非主线程中，还需要调用set_event_loop方法指定一个event loop对象，这样get_event_loop才会获取到被标记的event loop对象：
        """
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)


        loop = asyncio.get_event_loop()
        urls = ["{}pg{}/".format(self.url, i) for i in range(1,max_page + 1)]
        tasks = [asyncio.ensure_future(self.download(url)) for url in urls]
        tasks = asyncio.gather(*tasks)
        loop.run_until_complete(tasks)

        # end = time.time()
        # print("总共花了",end-start)


    def save_data_to_model(self):
        for item in self.data:
            new_item = HouseInfo()
            new_item.title = item['title']
            new_item.house = item['house']
            new_item.bedroom = item['bedroom']
            new_item.area = item['area']
            new_item.direction = item['direction']
            new_item.floor = item['floor']
            new_item.year = item['year']
            new_item.location = item['location']
            new_item.total_price = item['total_price']
            new_item.unit_price = item['unit_price']

            from homelink.utils.filter_class import get_filter_class
            filter_obj = get_filter_class("bloom")(salts=["1","2","3"],redis_host="192.168.2.102")

            new_item_str ="".join([v for v in item.values()])

            if not filter_obj.is_exists(new_item_str):

                filter_obj.save(new_item_str)
                print("映射保存成功", new_item_str)
                new_item.save()