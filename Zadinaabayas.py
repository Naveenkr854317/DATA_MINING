import scrapy
from scrapy_playwright.page import PageMethod

class AbhayaSpider(scrapy.Spider):
    name = "Abhaya"

    url= "https://www.zadinaabayas.com/#ca20/fullscreen/m=and&p=4&q=black+abaya"  #request must be str here

    def start_requests (self):
# request  website and looks for specific tag element
            yield scrapy.Request(self.url,meta=dict(
                playwright=True,
                
                # to access every page methods 
                playwright_page_methods=[
                    #  PageMethod("wait_for_selector","networkidle"),     #for good network condition
                     PageMethod("wait_for_selector","div.dfd-results")],
                playwright_include_page=True,
                
                errback=self.errback))
                

    async def parse(self, response):
# grab every link then will reach to every product to fetch required data
        links= response.xpath("//a[contains(@class,'dfd-card-link')]/@href").getall()

        for link in links:
            ab_url=response.urljoin(link)

            yield scrapy.Request(ab_url, callback=self.parse_details )

# getting required data(scraping)
    async def parse_details (self, response):

        Name= response.css(".pb-2 ::text")
        Name= Name.get() if Name else "Not available"

        Price= response.css(".variant-price ::text")
        Price= Price.get() if Price else "Not availble"


        Image_url= response.css("div.item img ::attr(src)")
        Image_url= Image_url.get() if Image_url else "Not availabe"


        yield {"Name": Name,
               "Price": Price,
               "Image_link": Image_url,
               "Product_link": response.url   #to get every product link
               }

# when page request failed page stopped 
    async def errback(self,failure):
        page=failure.request.meta["playwright_page"] 
        await page.close()   #Closing the Playwright page ensures the browser doesn’t keep too many tabs open.

# run the script on terminal
#  scrapy crawl Abhaya -o Abhaya.csv    to get in csv because here i didn't create dataframe 
#  scrapy crawl Abhaya -o Abaya.json    to get in json


