"""
Web scraper for realtor.ca property listings using Playwright.
Handles JavaScript-rendered content and CDN protection.
"""

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from bs4 import BeautifulSoup
from pathlib import Path
import time
from typing import Dict, List
import re


class RealtorScraper:
    """Scraper for realtor.ca property listings using Playwright."""
    
    def __init__(self, output_dir: str = "output/photos"):
        """
        Initialize the scraper.
        
        Args:
            output_dir: Directory to save downloaded photos
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def scrape_property(self, url: str) -> Dict:
        """
        Scrape property information from a realtor.ca listing.
        
        Args:
            url: The URL of the property listing
            
        Returns:
            Dictionary containing property information and photo paths
        """
        print(f"正在启动浏览器...")
        
        with sync_playwright() as p:
            # Launch browser with more realistic settings
            browser = p.chromium.launch(
                headless=False,  # Use visible browser to avoid detection
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-web-security',
                    '--disable-features=IsolateOrigins,site-per-process'
                ]
            )
            
            # Create context with realistic browser fingerprint
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                locale='en-US',
                timezone_id='America/New_York',
                permissions=['geolocation'],
                geolocation={'longitude': -73.567256, 'latitude': 45.501689},  # Montreal coordinates
                color_scheme='light',
                extra_http_headers={
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                    'Sec-Fetch-Site': 'none',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-User': '?1',
                    'Sec-Fetch-Dest': 'document',
                    'Upgrade-Insecure-Requests': '1'
                }
            )
            
            page = context.new_page()
            
            # Add script to remove webdriver property
            page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                
                // Override the navigator.plugins to make it look real
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
                
                // Override navigator.languages
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en']
                });
                
                // Chrome runtime
                window.chrome = {
                    runtime: {}
                };
            """)
            
            try:
                print(f"正在访问: {url}")
                
                # Navigate to the page
                page.goto(url, wait_until='domcontentloaded', timeout=60000)
                
                print("等待页面渲染...")
                # Wait for specific content to appear
                try:
                    # Wait for main content
                    page.wait_for_selector('body', timeout=10000)
                    time.sleep(5)  # Additional wait for JavaScript
                    
                    # Scroll down to trigger lazy loading
                    print("滚动页面以加载图片...")
                    for i in range(3):
                        page.evaluate('window.scrollBy(0, window.innerHeight)')
                        time.sleep(1)
                    
                    # Scroll back to top
                    page.evaluate('window.scrollTo(0, 0)')
                    time.sleep(2)
                    
                    print("✓ 页面加载完成")
                except Exception as e:
                    print(f"⚠ 页面加载警告: {e}")
                
                # Get the page HTML after JavaScript execution
                html_content = page.content()
                
                # Debug: Save HTML to file
                debug_file = Path("debug_page_content.html")
                with open(debug_file, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                print(f"  调试: HTML已保存到 {debug_file}")
                
                # Parse HTML with BeautifulSoup
                soup = BeautifulSoup(html_content, 'lxml')
                
                # Debug: Check what we got
                print(f"  调试: HTML长度: {len(html_content)} 字符")
                print(f"  调试: 找到 {len(soup.find_all('img'))} 个img标签")
                print(f"  调试: 找到 {len(soup.find_all('h1'))} 个h1标签")
                print(f"  调试: 找到 {len(soup.find_all('div'))} 个div标签")
                
                # Extract property information
                property_data = self._extract_all_data(soup)
                
                print(f"\n房产信息:")
                print(f"  标题: {property_data['title']}")
                print(f"  价格: {property_data['price']}")
                print(f"  地址: {property_data['address']}")
                print(f"  卧室: {property_data['bedrooms']}")
                print(f"  浴室: {property_data['bathrooms']}")
                
                # Download photos using Playwright's page object
                photo_urls = self._extract_photo_urls(soup, page)
                print(f"\n找到 {len(photo_urls)} 张照片，开始下载...")
                
                property_data['photos'] = self._download_photos_playwright(photo_urls, page)
                
                return property_data
                
            finally:
                browser.close()
    
    def _extract_all_data(self, soup: BeautifulSoup) -> Dict:
        """Extract all property data from JSON-LD and meta tags."""
        import json
        
        data = {
            'url': '',
            'title': 'Property Listing',
            'price': 'Price not available',
            'address': '',
            'property_type': 'Unknown',
            'bedrooms': 'Unknown',
            'bathrooms': 'Unknown',
            'description': '',
            'features': []
        }
        
        # Try to extract from JSON-LD structured data
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        for script in json_ld_scripts:
            if script.string:
                try:
                    json_data = json.loads(script.string)
                    
                    # Check if it's a Product type (property listing)
                    if json_data.get('@type') == 'Product':
                        # Extract name/title
                        if 'name' in json_data:
                            data['title'] = json_data['name']
                            data['address'] = json_data['name']
                        
                        # Extract description
                        if 'description' in json_data:
                            data['description'] = json_data['description']
                        
                        # Extract category (property type)
                        if 'category' in json_data:
                            data['property_type'] = json_data['category']
                        
                        # Extract price from offers
                        if 'offers' in json_data and isinstance(json_data['offers'], list):
                            for offer in json_data['offers']:
                                if 'price' in offer and 'priceCurrency' in offer:
                                    price_val = offer['price']
                                    currency = offer['priceCurrency']
                                    # Format price
                                    try:
                                        price_num = float(price_val)
                                        data['price'] = f"${price_num:,.0f} {currency}"
                                    except:
                                        data['price'] = f"${price_val} {currency}"
                                    break
                        
                        # Extract URL
                        if 'url' in json_data:
                            data['url'] = json_data['url']
                        
                        break
                except:
                    continue
        
        # Extract bedrooms and bathrooms from meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            content = meta_desc['content']
            # Parse "4 bedrooms, 2 bathrooms"
            import re
            bed_match = re.search(r'(\d+)\s*bedroom', content, re.IGNORECASE)
            if bed_match:
                data['bedrooms'] = bed_match.group(1)
            
            bath_match = re.search(r'(\d+)\s*bathroom', content, re.IGNORECASE)
            if bath_match:
                data['bathrooms'] = bath_match.group(1)
        
        # Extract features from the page
        # Look for listing details sections
        feature_elements = soup.select('.listingDetailsRoomDetails_Room, .listingFeature, [class*="feature"]')
        features = []
        for elem in feature_elements[:20]:  # Limit to 20 features
            text = elem.get_text(strip=True)
            if text and len(text) > 2 and text not in features:
                features.append(text)
        
        if features:
            data['features'] = features
        
        # If still missing data, try H1 for title
        if data['title'] == 'Property Listing':
            h1 = soup.find('h1')
            if h1:
                data['title'] = h1.get_text(strip=True)
                data['address'] = h1.get_text(strip=True)
        
        return data
    
    def _extract_photo_urls(self, soup: BeautifulSoup, page) -> List[str]:
        """Extract all photo URLs from the listing."""
        photo_urls = []
        
        print("\n  调试: 开始提取照片URL...")
        
        # Get all images
        all_imgs = soup.find_all('img')
        print(f"  调试: 找到 {len(all_imgs)} 个img标签")
        
        # Extract URLs from img elements
        for i, img in enumerate(all_imgs):
            # Try different attribute names
            for attr in ['src', 'data-src', 'data-original', 'data-lazy-src', 'srcset', 'data-srcset']:
                url = img.get(attr)
                if url:
                    # Handle srcset (take the highest resolution)
                    if 'srcset' in attr:
                        # Parse srcset format: "url1 1x, url2 2x" or "url1 100w, url2 200w"
                        urls = []
                        for part in url.split(','):
                            part = part.strip()
                            if part:
                                url_part = part.split()[0]
                                urls.append(url_part)
                        url = urls[-1] if urls else None
                    
                    if url:
                        # Make sure it's a full URL
                        if url.startswith('//'):
                            url = 'https:' + url
                        elif url.startswith('/'):
                            url = 'https://www.realtor.ca' + url
                        
                        if url.startswith('http'):
                            # Filter out small icons, logos, and UI elements
                            if not any(x in url.lower() for x in ['logo', 'icon', 'avatar', 'favicon', 'arrow', 'svg']):
                                # Check if it looks like a property photo
                                if any(indicator in url.lower() for indicator in ['photo', 'image', 'img', 'listing', 'property', 'realtor.ca']):
                                    photo_urls.append(url)
                                    print(f"  调试: 找到照片 {len(photo_urls)}: {url[:80]}...")
                                    break
                                # If URL contains size indicators, it's likely a photo
                                elif any(size in url for size in ['1200', '1024', '800', '640', 'large', 'medium']):
                                    photo_urls.append(url)
                                    print(f"  调试: 找到照片 {len(photo_urls)}: {url[:80]}...")
                                    break
        
        # If no photos found, try alternative method: look for picture elements
        if not photo_urls:
            print("  调试: 尝试从<picture>标签提取...")
            pictures = soup.find_all('picture')
            for pic in pictures:
                sources = pic.find_all('source')
                for source in sources:
                    srcset = source.get('srcset')
                    if srcset:
                        urls = [u.strip().split()[0] for u in srcset.split(',')]
                        if urls:
                            url = urls[-1]
                            if url.startswith('//'):
                                url = 'https:' + url
                            photo_urls.append(url)
                            print(f"  调试: 从picture找到照片: {url[:80]}...")
        
        # Remove duplicates while preserving order
        seen = set()
        unique_urls = []
        for url in photo_urls:
            if url not in seen:
                seen.add(url)
                unique_urls.append(url)
        
        print(f"  调试: 去重后共 {len(unique_urls)} 张照片")
        return unique_urls
    
    def _download_photos_playwright(self, photo_urls: List[str], page) -> List[str]:
        """Download photos using Playwright's page context and return local file paths."""
        downloaded_paths = []
        
        for i, url in enumerate(photo_urls, 1):
            try:
                print(f"  下载照片 {i}/{len(photo_urls)}...", end=' ')
                
                # Use Playwright to download the image
                response = page.request.get(url)
                
                if response.status != 200:
                    print(f"✗ HTTP {response.status}")
                    continue
                
                # Get image data
                image_data = response.body()
                
                # Determine file extension from content type
                content_type = response.headers.get('content-type', '')
                if 'jpeg' in content_type or 'jpg' in content_type:
                    ext = '.jpg'
                elif 'png' in content_type:
                    ext = '.png'
                elif 'webp' in content_type:
                    ext = '.webp'
                else:
                    ext = '.jpg'  # Default
                
                # Save photo
                filename = f"photo_{i:03d}{ext}"
                filepath = self.output_dir / filename
                
                with open(filepath, 'wb') as f:
                    f.write(image_data)
                
                downloaded_paths.append(str(filepath))
                print(f"✓ {filename}")
                
                # Be polite - add small delay between downloads
                time.sleep(0.3)
                
            except Exception as e:
                print(f"✗ 失败: {e}")
                continue
        
        print(f"\n✓ 成功下载 {len(downloaded_paths)} 张照片")
        return downloaded_paths


if __name__ == "__main__":
    # Test the scraper
    scraper = RealtorScraper()
    url = "https://www.realtor.ca/real-estate/29106905/4583-rue-roger-montreal-pierrefonds-roxboro-pierrefondswest"
    
    try:
        data = scraper.scrape_property(url)
        print("\n" + "="*50)
        print("抓取完成!")
        print(f"照片保存在: {scraper.output_dir}")
    except Exception as e:
        print(f"\n抓取失败: {e}")
