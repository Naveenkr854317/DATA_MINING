import scrapy
from scrapy.utils.response import open_in_browser
from scrapy_playwright.page import PageMethod
from scrapy.selector import Selector
import pandas as pd 

class QuotesScrollSpider(scrapy.Spider):
    name = 'scroll'
    
    def start_requests(self):
        yield scrapy.Request(
            url="http://quotes.toscrape.com/scroll",
            meta={
                "playwright": True,
                "playwright_page_methods": [PageMethod("wait_for_load_state","networkidle"),
                    PageMethod("wait_for_selector", ".quote")
                ],
                "playwright_include_page": True
            },
            errback=self.close_page
        )


    async def parse(self, response):
        page = response.meta['playwright_page']
        for i in range(2,11):  
            await page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
            quotes_count = 10*i
            await page.wait_for_selector(f'.quote:nth-child({quotes_count})')
        s  = Selector(text=await page.content())
        await page.close()
        all_data=[]
        for q in s.css('.quote'):
                author= q.css('.author ::text').get(),
                quote = q.css('.text ::text').get()       
                all_data.append([author,quote])

        df=pd.DataFrame(all_data,columns=["AUTHOR","QUOTE"])
        df.to_csv("quote_scroll.csv",index=False)
        print(df.head())
        
    async def close_page(self, failure):
        page = failure.request.meta["playwright_page"]
        await page.close()


