from playwright.sync_api import sync_playwright
import time, random
from urllib.parse import urljoin
import pandas as pd
import os
from urllib.request import urlretrieve   

def run(playwright):
    browser = playwright.chromium.launch(headless=False)   

    # ✅ Create a context with a custom User-Agent
    context = browser.new_context(
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    )
    page = context.new_page()

    page.goto("https://www.quillaudits.com/web3-hacks-database")
    page.wait_for_selector("table tbody tr",timeout=2000)     #if there is network issue extent timeout to 30000(30 sec)
    
    all_data=[]
    page_num = 1
    # max_pages = 2
    # counter=1
    # folder_name="QuillAudits"  # to save images into folder

    file ="quillaudits.csv"
    while True:
        print(f"\n--- Page {page_num} ---")
        base_url=page.url

        rows = page.query_selector_all("table tbody tr")
        for row in rows:
            name = row.query_selector("td:nth-child(1)")
            name = name.inner_text().strip() if name else None


            date = row.query_selector("td:nth-child(2)")
            date = date.inner_text().strip() if date else None

            issue = row.query_selector("td:nth-child(3)")
            issue = issue.inner_text().strip() if issue else None

            amount = row.query_selector("td:nth-child(4)")
            amount = amount.inner_text().strip() if amount else None

            chains = row.query_selector("xpath=//img[contains(@loading,'lazy')]")
            chains = chains.get_attribute("src") if chains else None
            chains_images= urljoin(base_url,chains) if chains else None

            category = row.query_selector("td:nth-child(6)")
            category = category.inner_text().strip() if category else None

            all_data.append([name, date, issue, amount, chains_images, category])
            
#            ✅ Download and save images
        #     if chains:
        #         img_path = os.path.join(folder_name, f"{counter}.jpg")
        #         try:
        #             urlretrieve(chains, img_path)
        #             print(f"Saved image {img_path}")        

        #         except Exception as e:
        #             print(f"Failed to save {chains}: {e}")
        #         counter += 1   


        # if page_num >= max_pages:      #to check 3 or 4 pages for trial
        #     break
        

        next_btn= page.query_selector("button:has(img[src*='rightarrow.svg'])")
        if not next_btn:
            print("No more pages to click Next button.")
            break

        # scroll + click
        # ab_url=urljoin(base_url,next_btn)
        next_btn.scroll_into_view_if_needed()
        page.wait_for_timeout(2000)
        next_btn.click()

        # wait for next page content
        page.wait_for_load_state("networkidle")

        page_num += 1
        time.sleep(random.uniform(1.5, 3))  # ✅ human-like pause upto 3 sec



    browser.close()
    df = pd.DataFrame(all_data, columns=["NAME", "DATE", "ISSUE", "AMOUNT LOST", "CHAINS_IMAGES", "CATEGORY"])
    print(df.head(10))  # to watch 1st 10 rows of dataset

    # ---- Export to multiple formats ----
    df.to_csv(file, index=False)
    # df.to_csv("quillaudits.json", index=False)
    # df.to_csv("quillaudits.xlsx", index=False)

    print(f"Scraped data saved into {file}")


if __name__ == "__main__":
    with sync_playwright() as p:
        run(p)


