from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

test_url = "http://quotes.toscrape.com/"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
        
    page.goto(test_url)

    print(page.title())
    
    soup = BeautifulSoup(page.content(), 'lxml')
        
    # 결과 확인을 위해 5초간 브라우저 유지
   
    # print(soup.find('span', class_='text').get_text())
    
    selector_next = "body > div > div:nth-child(2) > div.col-md-8 > nav > ul > li.next > a"
    
    print('*'*80)
    for pg in range(0, 5) :
        for seq in range(1, 11) :
            selector_author = f"body > div > div:nth-child(2) > div.col-md-8 > div:nth-child({seq}) > span:nth-child(2) > small"
            selector_maxim  = f"body > div > div:nth-child(2) > div.col-md-8 > div:nth-child({seq}) > span.text"
    
            print(soup.select_one(selector_maxim).text)
            print(f"-- by {soup.select_one(selector_author).text}")
            print('-'*80)
        
        print("Go to Next")
        
        link = soup.select_one(selector_next)['href'] # like "/page/2/"
        page.goto(test_url + link)                    # http://quotes.toscrape.com/page/2/
        soup = BeautifulSoup(page.content(), 'lxml')
        
        # if pg > 0 :
        #     page.click(selector_next_1)
        # else :
        #     page.click(selector_next_0)
        
    page.wait_for_timeout(5000)
    browser.close()
    
print("jobs Done!")