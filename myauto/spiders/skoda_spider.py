import scrapy
from unidecode import unidecode


class MainSpider(scrapy.Spider):
    name = 'skoda'
    start_urls = ['https://www.myauto.ge/ka/s/00/0/38/00/00/00/00/00/skoda?'
                  'stype=0&marka=38&currency_id=3&det_search=0&ord=7&keyword'
                  '=&category_id=m0&page=1']

    def parse(self, response, **kwargs):
        pages = response.xpath('//figure/a/@href')
        yield from response.follow_all(pages, callback=self.parse_single)

        next_page = response.css('.pag-next a::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_single(self, response):
        url = 'https://www.myauto.ge/ka/pr/SaveFeedback'
        method = 'POST'
        headers = {'X-Requested-With': 'XMLHttpRequest',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                                 'AppleWebKit/537.36 (KHTML, like Gecko) '
                                 'Chrome/87.0.4280.88 Safari/537.36',
                   'Content-Type': 'application/x-www-form-urlencoded; '
                                   'charset=UTF-8'}

        pr_id = response.css('.detail-top-item~ .detail-top-item+ '
                             '.detail-top-item::text').get()
        body = f'PrID={pr_id}&type_id=0'

        author_name = response.css('.user-name::text').get()
        if author_name:
            author_name = unidecode(author_name).replace('`', '')
        else:
            author_name = 'N/A'

        yield scrapy.Request(url, method=method, body=body, headers=headers,
                             callback=self.parse_phone,
                             meta={'name': author_name})

    def parse_phone(self, response):
        yield {'phone': eval(response.text)['phone'][3:],
               'name': response.meta.get('name')}
