import json
import scrapy
from scrapy.selector import Selector
from ..items import GameItem


class GameSpider(scrapy.Spider):
    name = "Game"

    start_urls = ['http://0.0.0.0:8050/render.html?url=https://store.steampowered.com/tags/en/Historical#p=4&tab=NewReleases&wait=10'
                  ]

    start = 0
    count = 15
    all_links = []
    tabs = ['NewReleases', 'TopSellers',
            'ConcurrentUsers', 'TopRated', 'ComingSoon']

    items = GameItem()

    def parse(self, response):

        last_pages = []
        for tab in GameSpider.tabs:
            pages = response.xpath(
                '//*[@id="' + str(tab) + '_links"]/span/text()').getall()
            last_page_start = self.getting_last_page_start(pages)
            last_pages.append(last_page_start)

        for tab in range(len(GameSpider.tabs)):
            while GameSpider.start <= last_pages[tab]:
                next_page = 'https://store.steampowered.com/contenthub/querypaginated/tags/' + str(GameSpider.tabs[tab]) + '/render/?query=&start=' + str(
                    GameSpider.start) + '&count=' + str(GameSpider.count) + '&cc=PK&l=english&v=4&tag=Historical'

                if next_page is None:
                    GameSpider.start += GameSpider.count
                    continue

                GameSpider.start += GameSpider.count
                yield response.follow(next_page, callback=self.pages_parse)

            GameSpider.start = 0

    def company_details(self, response):

        company_names = response.xpath('//*[@id="developers_list"]')
        anchors = company_names.xpath('.//a')

        for company in anchors:
            GameSpider.items['company_name'] = company.xpath(
                './/text()').get()
            bad_link = company.xpath(
                './/@href').get()

            if bad_link.find('/search/?developer=') != -1:
                bad_link = bad_link.replace(
                    '/search/?developer=', '/developer/')

            GameSpider.items['company_web_address'] = bad_link
            yield GameSpider.items

    def getting_last_page_start(self, pages):

        last_page = int(pages[-1])
        last_page_start = (last_page * GameSpider.count) - GameSpider.count
        return last_page_start

    def pages_parse(self, response):

        j_obj = json.loads(response.text)
        j_response = Selector(text=j_obj['results_html'])

        links = j_response.xpath(
            '//a/@href').getall()

        for link in links:
            GameSpider.all_links.append(link)

        yield from response.follow_all(GameSpider.all_links, callback=self.company_details)
