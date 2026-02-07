"""
Debug script using Playwright to analyze the rendered HTML.
"""

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from pathlib import Path
import time


def debug_with_playwright(url: str):
    """Debug the HTML structure using Playwright."""
    
    print(f"正在启动浏览器...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Show browser for debugging
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = context.new_page()
        
        try:
            print(f"正在访问: {url}")
            page.goto(url, wait_until='networkidle', timeout=60000)
            
            # Wait for content
            print("等待页面加载...")
            time.sleep(5)
            
            # Get HTML
            html_content = page.content()
            
            # Save HTML
            output_file = Path("debug_playwright.html")
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"\n✓ HTML已保存到: {output_file}")
            
            # Parse and analyze
            soup = BeautifulSoup(html_content, 'lxml')
            
            print("\n" + "="*60)
            print("页面分析:")
            print("="*60)
            
            # Count elements
            print(f"\n总共的 <img> 标签: {len(soup.find_all('img'))}")
            print(f"总共的 <h1> 标签: {len(soup.find_all('h1'))}")
            print(f"总共的 <h2> 标签: {len(soup.find_all('h2'))}")
            print(f"总共的 <div> 标签: {len(soup.find_all('div'))}")
            
            # Show first few images
            print("\n前10个图片:")
            for i, img in enumerate(soup.find_all('img')[:10], 1):
                src = img.get('src', '')[:100]
                alt = img.get('alt', '')[:50]
                print(f"  {i}. src={src}... alt={alt}")
            
            # Show headings
            print("\n所有 H1 标签:")
            for h1 in soup.find_all('h1'):
                print(f"  - {h1.get_text(strip=True)[:100]}")
            
            print("\n所有 H2 标签:")
            for h2 in soup.find_all('h2')[:5]:
                print(f"  - {h2.get_text(strip=True)[:100]}")
            
            # Take screenshot
            screenshot_path = "debug_screenshot.png"
            page.screenshot(path=screenshot_path, full_page=True)
            print(f"\n✓ 截图已保存到: {screenshot_path}")
            
            print("\n按Enter键关闭浏览器...")
            input()
            
        finally:
            browser.close()


if __name__ == "__main__":
    url = "https://www.realtor.ca/real-estate/29106905/4583-rue-roger-montreal-pierrefonds-roxboro-pierrefondswest"
    debug_with_playwright(url)
