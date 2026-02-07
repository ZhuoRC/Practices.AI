"""
Main script for the photo crawler application.
Orchestrates web scraping and PDF generation.
"""

import sys
from pathlib import Path
from scraper import RealtorScraper
from pdf_generator import PropertyPDFGenerator


def main():
    """Main entry point for the application."""
    
    # Default URL
    default_url = "https://www.realtor.ca/real-estate/29106905/4583-rue-roger-montreal-pierrefonds-roxboro-pierrefondswest"
    
    # Get URL from command line or use default
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = default_url
        print(f"使用默认URL: {url}\n")
    
    print("="*60)
    print("房产信息爬虫 - Realtor.ca")
    print("="*60)
    
    # Initialize scraper and PDF generator
    scraper = RealtorScraper(output_dir="output/photos")
    pdf_generator = PropertyPDFGenerator(output_dir="output")
    
    try:
        # Step 1: Scrape property data
        print("\n[步骤 1/2] 正在抓取房产信息...")
        print("-" * 60)
        property_data = scraper.scrape_property(url)
        
        # Step 2: Generate PDF
        print("\n[步骤 2/2] 正在生成PDF报告...")
        print("-" * 60)
        pdf_path = pdf_generator.generate_pdf(property_data)
        
        # Success!
        print("\n" + "="*60)
        print("✓ 任务完成!")
        print("="*60)
        print(f"\n报告信息:")
        print(f"  • PDF文件: {pdf_path}")
        print(f"  • 照片数量: {len(property_data['photos'])}")
        print(f"  • 照片目录: {scraper.output_dir}")
        print(f"\n您可以打开PDF查看完整的房产报告。")
        
        return 0
        
    except Exception as e:
        print("\n" + "="*60)
        print("✗ 错误!")
        print("="*60)
        print(f"\n发生错误: {e}")
        print("\n可能的原因:")
        print("  1. 网站结构已更改")
        print("  2. 网络连接问题")
        print("  3. URL无效或已过期")
        print("\n请检查URL是否正确，或稍后重试。")
        
        return 1


if __name__ == "__main__":
    sys.exit(main())
