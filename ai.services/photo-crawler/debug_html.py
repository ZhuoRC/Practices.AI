"""
Debug script to analyze the HTML structure of a realtor.ca listing.
"""

import httpx
from bs4 import BeautifulSoup
from pathlib import Path


def analyze_html(url: str):
    """Analyze the HTML structure of a realtor.ca listing."""
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://www.realtor.ca/',
        'Connection': 'keep-alive',
    }
    
    print(f"正在访问: {url}\n")
    
    with httpx.Client(headers=headers, timeout=30.0, follow_redirects=True, http2=True) as client:
        response = client.get(url)
        print(f"状态码: {response.status_code}\n")
        
        # Save HTML for inspection
        output_file = Path("debug_page.html")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"✓ HTML已保存到: {output_file}\n")
        
        # Parse and analyze
        soup = BeautifulSoup(response.text, 'lxml')
        
        # Find all images
        print("=" * 60)
        print("图片分析:")
        print("=" * 60)
        all_imgs = soup.find_all('img')
        print(f"找到 {len(all_imgs)} 个 <img> 标签\n")
        
        for i, img in enumerate(all_imgs[:10], 1):  # Show first 10
            src = img.get('src') or img.get('data-src') or img.get('data-original')
            alt = img.get('alt', '')
            classes = ' '.join(img.get('class', []))
            print(f"{i}. src: {src[:80] if src else 'None'}...")
            print(f"   alt: {alt}")
            print(f"   class: {classes}\n")
        
        # Find headings
        print("=" * 60)
        print("标题分析:")
        print("=" * 60)
        for tag in ['h1', 'h2', 'h3']:
            elements = soup.find_all(tag)
            print(f"\n{tag.upper()} 标签 ({len(elements)} 个):")
            for elem in elements[:5]:
                text = elem.get_text(strip=True)[:100]
                classes = ' '.join(elem.get('class', []))
                print(f"  - {text}")
                print(f"    class: {classes}")
        
        # Find price-like elements
        print("\n" + "=" * 60)
        print("价格相关元素:")
        print("=" * 60)
        price_keywords = ['price', 'amount', 'dollar', 'cost']
        for keyword in price_keywords:
            elements = soup.find_all(class_=lambda x: x and keyword in x.lower())
            if elements:
                print(f"\n包含 '{keyword}' 的class ({len(elements)} 个):")
                for elem in elements[:3]:
                    text = elem.get_text(strip=True)[:100]
                    classes = ' '.join(elem.get('class', []))
                    print(f"  - {text}")
                    print(f"    class: {classes}")
        
        # Check for JSON-LD structured data
        print("\n" + "=" * 60)
        print("结构化数据 (JSON-LD):")
        print("=" * 60)
        json_ld = soup.find_all('script', type='application/ld+json')
        print(f"找到 {len(json_ld)} 个 JSON-LD 脚本\n")
        for i, script in enumerate(json_ld, 1):
            content = script.string[:200] if script.string else "None"
            print(f"{i}. {content}...\n")


if __name__ == "__main__":
    url = "https://www.realtor.ca/real-estate/29106905/4583-rue-roger-montreal-pierrefonds-roxboro-pierrefondswest"
    analyze_html(url)
