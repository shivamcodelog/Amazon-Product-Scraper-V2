from playwright.sync_api import sync_playwright, Playwright
import pandas as pd
import time
import random



query=input("Product you want to Scrape: ")
target_count = int(input("Number of product want to scrape: "))
fileName=input("Name of EXTRACTED file:")

def run(playwright: Playwright):
    d = {"Title": [], "Price": [], "Link": [], "Page": []}
    current_page = 1
    
    browser = playwright.chromium.launch(headless=False)
    page = browser.new_page()

    print(f"🎯 Starting scrape. Goal: {target_count} unique products.")

    while len(d["Title"]) < target_count:
        url = f"https://www.amazon.in/s?k={query}&page={current_page}"
        print(f"👾 Navigating to Page {current_page}...")
        
        try:
            page.goto(url, timeout=60000)
            
            try:
                page.wait_for_selector('div[data-cy="asin-faceout-container"]', timeout=15000)
            except:
                print("⚠️ No products found (Timeout).")
                break
            
            # 2. Get ALL product containers
            products = page.locator('div[data-cy="asin-faceout-container"]').all()
            
            if not products:
                break

            for pdt in products:
                if len(d["Title"]) >= target_count: break
                
                try:
                    if not pdt.is_visible(): continue

                    # --- TITLE ---
                    # Inside this container
                    title_loc = pdt.locator("h2 span")
                    if title_loc.count() == 0: continue
                    title = title_loc.first.text_content().strip()
                    
                    if title in d["Title"]: continue

                    # --- LINK ---
                    link_loc = pdt.locator('div[data-cy="title-recipe"] a')



                    if link_loc.count() > 0:
                        l=link_loc.first.get_attribute("href")
                    else:
                        l=None

                    #----FILTERING THE FALSE LINKS----------------------------------------

                    if not l or "javascript:void(0)" in l:
                        continue

                    link = "https://amazon.in" + l



                    # --- PRICE ---
               
                    price = "N/A"
                    price_loc = pdt.locator('.a-price .a-offscreen')
                    if price_loc.count() > 0:
                        price = price_loc.first.text_content().strip()



                    # SAVE
                    d["Title"].append(title)
                    d["Price"].append(price)
                    d["Link"].append(link)
                    d["Page"].append(current_page)
                    
                    print(f"[{len(d['Title'])}/{target_count}]    Collected: {title[:20]}... | {price} | ")

                except Exception:
                    continue

            current_page += 1
            time.sleep(random.uniform(2, 4))

        except Exception as e:
            print(f"Error: {e}")
            break

    browser.close()
    
    if d["Title"]:
        df = pd.DataFrame(d)
        df.to_csv(f"{fileName}.csv", index=False, encoding="utf-8-sig")
        df.to_excel(f"{fileName}.xlsx", index=False)
        print("✅ Done.")

with sync_playwright() as playwright:
    run(playwright)

#--------Made by SHIVAM KUMAR----------------