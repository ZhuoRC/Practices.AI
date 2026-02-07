"""
PDF generator for property listings.
Creates a professional PDF report with property information and photos.
Supports Chinese characters using system fonts.
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image as PILImage
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import os


# Register Chinese fonts
def register_chinese_fonts():
    """Register Chinese fonts from Windows system."""
    try:
        # Try to use Microsoft YaHei (common on Windows)
        font_paths = [
            r'C:\Windows\Fonts\msyh.ttc',  # Microsoft YaHei
            r'C:\Windows\Fonts\simsun.ttc',  # SimSun
            r'C:\Windows\Fonts\simhei.ttf',  # SimHei
        ]
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    pdfmetrics.registerFont(TTFont('ChineseFont', font_path))
                    return 'ChineseFont'
                except:
                    continue
    except:
        pass
    
    # Fallback to Helvetica (won't display Chinese properly)
    return 'Helvetica'


CHINESE_FONT = register_chinese_fonts()


class PropertyPDFGenerator:
    """Generate PDF reports for property listings."""
    
    def __init__(self, output_dir: str = "output"):
        """
        Initialize the PDF generator.
        
        Args:
            output_dir: Directory to save the PDF
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_pdf(self, property_data: Dict, output_filename: str = None) -> str:
        """
        Generate a PDF report for a property listing.
        
        Args:
            property_data: Dictionary containing property information
            output_filename: Optional custom filename for the PDF
            
        Returns:
            Path to the generated PDF file
        """
        if output_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"property_report_{timestamp}.pdf"
        
        pdf_path = self.output_dir / output_filename
        
        # Create PDF document
        doc = SimpleDocTemplate(
            str(pdf_path),
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        
        # Build content
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles with Chinese font support
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName=CHINESE_FONT
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=10,
            spaceBefore=15,
            fontName=CHINESE_FONT
        )
        
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['BodyText'],
            fontSize=11,
            textColor=colors.HexColor('#333333'),
            spaceAfter=8,
            leading=14,
            fontName=CHINESE_FONT
        )
        
        # Title
        story.append(Paragraph("房产信息报告", title_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Property Title
        if property_data.get('title'):
            story.append(Paragraph(property_data['title'], heading_style))
        
        # Basic Information Table
        basic_info = [
            ['价格', property_data.get('price', '未知')],
            ['地址', property_data.get('address', '未知')],
            ['房型', property_data.get('property_type', '未知')],
            ['卧室', property_data.get('bedrooms', '未知')],
            ['浴室', property_data.get('bathrooms', '未知')],
        ]
        
        table = Table(basic_info, colWidths=[1.5*inch, 4.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2c3e50')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), CHINESE_FONT),
            ('FONTNAME', (1, 0), (1, -1), CHINESE_FONT),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 0.3*inch))
        
        # Description
        if property_data.get('description') and property_data['description'] != '暂无描述':
            story.append(Paragraph("房产描述", heading_style))
            story.append(Paragraph(property_data['description'], body_style))
            story.append(Spacer(1, 0.2*inch))
        
        # Features
        if property_data.get('features'):
            story.append(Paragraph("房产特征", heading_style))
            for feature in property_data['features'][:10]:  # Limit to 10 features
                story.append(Paragraph(f"• {feature}", body_style))
            story.append(Spacer(1, 0.2*inch))
        
        # URL
        if property_data.get('url'):
            story.append(Paragraph("链接", heading_style))
            story.append(Paragraph(f'<link href="{property_data["url"]}">{property_data["url"]}</link>', body_style))
            story.append(Spacer(1, 0.3*inch))
        
        # Photos
        if property_data.get('photos'):
            story.append(PageBreak())
            story.append(Paragraph("房产照片", heading_style))
            story.append(Spacer(1, 0.2*inch))
            
            for i, photo_path in enumerate(property_data['photos'], 1):
                try:
                    # Add photo with caption
                    img = self._resize_image(photo_path, max_width=6.5*inch, max_height=5*inch)
                    if img:
                        story.append(img)
                        caption = Paragraph(
                            f"<i>照片 {i}/{len(property_data['photos'])}</i>",
                            ParagraphStyle('Caption', parent=body_style, alignment=TA_CENTER, fontSize=9, textColor=colors.HexColor('#7f8c8d'))
                        )
                        story.append(caption)
                        story.append(Spacer(1, 0.3*inch))
                        
                        # Add page break after every 2 photos
                        if i % 2 == 0 and i < len(property_data['photos']):
                            story.append(PageBreak())
                            
                except Exception as e:
                    print(f"  警告: 无法添加照片 {photo_path}: {e}")
                    continue
        
        # Build PDF
        print(f"\n正在生成PDF: {pdf_path}")
        doc.build(story)
        print(f"✓ PDF生成成功!")
        
        return str(pdf_path)
    
    def _resize_image(self, image_path: str, max_width: float, max_height: float) -> Image:
        """
        Resize image to fit within max dimensions while maintaining aspect ratio.
        
        Args:
            image_path: Path to the image file
            max_width: Maximum width in points
            max_height: Maximum height in points
            
        Returns:
            ReportLab Image object
        """
        try:
            # Open image to get dimensions
            with PILImage.open(image_path) as img:
                img_width, img_height = img.size
            
            # Calculate scaling factor
            width_ratio = max_width / img_width
            height_ratio = max_height / img_height
            scale_factor = min(width_ratio, height_ratio)
            
            # Calculate new dimensions
            new_width = img_width * scale_factor
            new_height = img_height * scale_factor
            
            # Create ReportLab Image
            return Image(image_path, width=new_width, height=new_height)
            
        except Exception as e:
            print(f"  警告: 无法处理图片 {image_path}: {e}")
            return None


if __name__ == "__main__":
    # Test the PDF generator
    test_data = {
        'title': '测试房产',
        'price': '$500,000',
        'address': '123 Test Street, Montreal, QC',
        'property_type': '独立屋',
        'bedrooms': '3',
        'bathrooms': '2',
        'description': '这是一个测试描述。',
        'features': ['特征1', '特征2', '特征3'],
        'url': 'https://example.com',
        'photos': []
    }
    
    generator = PropertyPDFGenerator()
    pdf_path = generator.generate_pdf(test_data, "test_report.pdf")
    print(f"测试PDF已生成: {pdf_path}")
