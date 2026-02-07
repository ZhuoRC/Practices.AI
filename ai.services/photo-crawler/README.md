# Photo Crawler - Realtor.ca 房产信息爬虫

一个轻量级的Python应用程序，用于从realtor.ca抓取房产信息和照片，并生成专业的PDF报告。

## 功能特点

- ✅ **轻量级设计**: 使用httpx和BeautifulSoup，无需浏览器驱动
- ✅ **完整信息提取**: 自动提取标题、价格、地址、房型、描述等
- ✅ **照片下载**: 下载所有房产照片到本地
- ✅ **PDF报告**: 生成包含所有信息和照片的专业PDF文档
- ✅ **一键启动**: 使用start.bat自动设置环境并运行

## 系统要求

- Windows 10/11
- Python 3.8 或更高版本
- 网络连接

## 快速开始

### 方法1: 使用启动脚本（推荐）

1. 双击运行 `start.bat`
2. 脚本会自动：
   - 创建Python虚拟环境
   - 安装所有依赖
   - 运行爬虫程序
3. 等待完成，PDF将保存在 `output/` 目录

### 方法2: 手动运行

```bash
# 1. 创建虚拟环境
python -m venv venv

# 2. 激活虚拟环境
venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 运行程序（使用默认URL）
python main.py

# 或指定自定义URL
python main.py "https://www.realtor.ca/real-estate/YOUR-LISTING-ID"
```

## 项目结构

```
photo-crawler/
├── main.py              # 主程序入口
├── scraper.py           # 网页爬虫模块
├── pdf_generator.py     # PDF生成模块
├── requirements.txt     # Python依赖
├── start.bat           # Windows启动脚本
├── README.md           # 本文件
├── output/             # 输出目录
│   ├── photos/        # 下载的照片
│   └── *.pdf          # 生成的PDF报告
└── venv/              # Python虚拟环境（自动创建）
```

## 依赖说明

| 包名 | 版本 | 用途 | 大小 |
|------|------|------|------|
| httpx | >=0.26.0 | HTTP客户端，支持HTTP/2 | ~100KB |
| beautifulsoup4 | >=4.12.0 | HTML解析 | ~500KB |
| lxml | >=5.1.0 | XML/HTML解析器 | ~2MB |
| reportlab | >=4.0.7 | PDF生成 | ~2MB |
| Pillow | >=10.1.0 | 图像处理 | ~3MB |

**总依赖大小**: ~5-8MB（vs Selenium方案的200MB+）

## 输出示例

运行成功后，您将获得：

1. **PDF报告** (`output/property_report_YYYYMMDD_HHMMSS.pdf`)
   - 房产基本信息表格
   - 详细描述
   - 房产特征列表
   - 所有照片（带编号）

2. **照片文件夹** (`output/photos/`)
   - photo_001.jpg
   - photo_002.jpg
   - ...

## 常见问题

### Q: 遇到403错误怎么办？
A: 本程序使用浏览器headers模拟真实访问，通常可以绕过基本的反爬机制。如果仍然失败，可能是网站加强了反爬措施。

### Q: 某些信息没有提取到？
A: realtor.ca的页面结构可能会变化。如果发现信息缺失，可能需要更新`scraper.py`中的CSS选择器。

### Q: 可以批量处理多个URL吗？
A: 当前版本一次处理一个URL。如需批量处理，可以创建一个包含URL的文本文件，然后修改`main.py`循环处理。

### Q: PDF中文显示有问题？
A: ReportLab默认支持中文。如果遇到问题，可能需要安装中文字体。

## 技术说明

### 为什么选择httpx而不是requests？

- ✅ 支持HTTP/2协议，更接近真实浏览器
- ✅ 更现代的API设计
- ✅ 更好的性能
- ✅ 异步支持（虽然本项目未使用）

### 爬虫策略

1. **Headers模拟**: 使用完整的浏览器headers
2. **礼貌爬取**: 照片下载间隔0.5秒
3. **容错处理**: 单张照片失败不影响整体流程
4. **多选择器**: 使用多个CSS选择器提高成功率

## 许可证

本项目仅供学习和个人使用。请遵守realtor.ca的使用条款和robots.txt规则。

## 更新日志

### v1.0.0 (2026-01-30)
- ✅ 初始版本
- ✅ 支持realtor.ca房产信息抓取
- ✅ PDF报告生成
- ✅ 照片下载功能
