import scrapy
from scrapy_playwright.page import PageMethod
import os

class QSpiderSpider(scrapy.Spider):
    name = "q_spider"

    def start_requests(self):
        url = "https://books.toscrape.com/catalogue/page-1.html"
        yield scrapy.Request(
            url,
            meta={
                "playwright": True,
                "playwright_include_page":True,
                "playwright_page_methods": [
                    PageMethod("wait_for_load_state","networkidle"),
                    PageMethod("wait_for_selector", ".product_pod img"),
                    
                ],
            },
            callback=self.parse,
        )

    async def parse(self, response):
        folder = "downloaded_books2"
        os.makedirs(folder, exist_ok=True)

        image_urls = response.css(".product_pod img::attr(src)").getall()
        for idx, img in enumerate(image_urls, start=100):
            img = response.urljoin(img)
            filename = os.path.join(folder, f"{idx}.jpg")
            yield scrapy.Request(
                img,
                callback=self.save_image,
                meta={"filename": filename},
                dont_filter=True
            )

    def save_image(self, response):
        filename = response.meta["filename"]
        with open(filename, "wb") as f:
            f.write(response.body)
        self.log(f"Saved {filename}")
