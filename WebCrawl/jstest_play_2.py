from playwright.sync_api import sync_playwright
import time  # 1. time 모듈 추가

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
        
    page.goto("http://www.example.com/")

    print(page.title())
    print(page.content()[:200])
        
    # 결과 확인을 위해 5초간 브라우저 유지
    page.wait_for_timeout(5000)
        
    browser.close()
    
print("크롤링 완료!")