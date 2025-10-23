# 🇨🇦 Canada Immigration Processing Times Scraper

> 自动化获取加拿大移民局申请处理时间的工具

这个项目提供了完整的解决方案，用于自动化获取加拿大移民局网站上的各类申请处理时间数据。

## 🌐 目标网站

https://www.canada.ca/en/immigration-refugees-citizenship/services/application/check-processing-times.html

## 📚 文档导航

- **📑 [完整索引](INDEX.md)** ⭐⭐⭐ 项目全览 - 所有文档和代码导航
- **🚀 [快速参考](QUICK_REFERENCE.md)** ⭐⭐ 最常用 - 5分钟快速上手
- **📱 [网页查询器指南](VIEWER_GUIDE.md)** ⭐⭐ 图形界面使用说明
- **📖 [详细使用指南](USAGE.md)** - 完整的使用说明和示例
- **📊 [项目总结](SUMMARY.md)** - 完整的技术分析和项目成果

## 🌐 网页界面

- **[viewer.html](viewer.html)** ⭐ 演示版 - 本地打开即可查看界面效果
- **[viewer_integrated.html](viewer_integrated.html)** - 集成版 - 在目标网站运行的完整版本

## 💻 代码文件

- **[example_complete.js](example_complete.js)** ⭐ 核心脚本 - 可直接在控制台运行
- **[scraper_with_mcp.js](scraper_with_mcp.js)** - JavaScript工具函数库
- **[canada_processing_times.py](canada_processing_times.py)** - Python数据结构定义

## ⚡ 快速开始

1. 打开目标网页
2. 打开浏览器控制台（F12）
3. 复制 [`example_complete.js`](example_complete.js) 到控制台
4. 执行查询：

```javascript
const result = await getCanadaProcessingTime(
  "Temporary residence (visiting, studying, working)",
  "Visitor visa (from outside Canada)",
  "China (People's Republic of)"
);
console.log(result);
```

## How the Form Works

The website uses a multi-step cascading form:

1. **Step 1**: Select application category
   - Temporary residence (visiting, studying, working)
   - Economic immigration
   - Family sponsorship
   - Refugees
   - Humanitarian and compassionate cases
   - Passport
   - Citizenship
   - Permanent resident cards
   - Replacing or amending documents, verifying status

2. **Step 2**: Select specific application type (dynamically loaded based on Step 1)
   - For "Temporary residence", options include:
     - Visitor visa (from outside Canada)
     - Study permit (from outside Canada)
     - Work permit (from outside Canada)
     - etc.

3. **Step 3**: Select country of application (dynamically loaded)
   - 200+ countries available

4. **Step 4**: Click "Get processing time" button

5. **Result**: The page displays the processing time for that specific combination

## Page Structure Analysis

### Select Elements

The form contains multiple `<select>` elements with dynamic IDs:

- First select (id starts with `wb-auto-`): Application category
- Second select (id starts with `wb-auto-`): Application type (appears after category selection)
- Third select (id starts with `wb-auto-`): Country (appears after type selection)

### Button

- Text: "Get processing time"
- Triggers form submission and displays results

## Automation Challenges

1. **Dynamic IDs**: The select element IDs change on each page load
2. **Cascading Form**: Each selection triggers the next dropdown to appear
3. **Timing**: Need to wait for DOM updates between selections
4. **Result Extraction**: Processing time results appear in dynamically generated HTML

## Solution Approach

### Using Chrome DevTools MCP

The Chrome DevTools MCP provides tools to:

1. **Navigate**: `navigate_page` to load the URL
2. **Interact**: `fill` or `evaluate_script` to select dropdown options
3. **Wait**: Built-in waiting for page updates
4. **Extract**: `evaluate_script` to extract results from the page

### Example Workflow

```javascript
// 1. Get all select elements
const selects = document.querySelectorAll('select');

// 2. Select category (first select, exclude month selector at bottom)
const categorySelect = selects[0];
categorySelect.value = "Temporary residence (visiting, studying, working)";
categorySelect.dispatchEvent(new Event('change', { bubbles: true }));

// 3. Wait for second dropdown
await new Promise(resolve => setTimeout(resolve, 1000));

// 4. Select application type
const typeSelect = document.querySelectorAll('select')[1];
typeSelect.value = "Visitor visa (from outside Canada)";
typeSelect.dispatchEvent(new Event('change', { bubbles: true }));

// 5. Wait for third dropdown
await new Promise(resolve => setTimeout(resolve, 1000));

// 6. Select country
const countrySelect = document.querySelectorAll('select')[2];
countrySelect.value = "China (People's Republic of)";
countrySelect.dispatchEvent(new Event('change', { bubbles: true }));

// 7. Click submit button
const button = Array.from(document.querySelectorAll('button')).find(b =>
  b.textContent.includes('Get processing time')
);
button.click();

// 8. Wait for and extract results
await new Promise(resolve => setTimeout(resolve, 2000));
// Extract processing time from the result page
```

## Files

- `canada_processing_times.py`: Python structure and data models
- `scraper_with_mcp.js`: JavaScript helper functions for browser automation
- `README.md`: This documentation file

## Usage with Chrome DevTools MCP

The scripts can be used with Chrome DevTools MCP by:

1. Opening the Chrome DevTools MCP connection
2. Navigating to the target URL
3. Running the JavaScript functions via `evaluate_script`
4. Extracting and saving the results

## Data Export Formats

The scraper supports exporting to:

- **JSON**: Structured data with all fields
- **CSV**: Tabular format for spreadsheets
- **Database**: Can be extended to save to SQLite, PostgreSQL, etc.

## Example Output

```json
{
  "category": "Temporary residence (visiting, studying, working)",
  "type": "Visitor visa (from outside Canada)",
  "country": "China (People's Republic of)",
  "processing_time": "XX days/weeks/months",
  "timestamp": "2025-10-19T..."
}
```

## Next Steps

To make this fully functional:

1. Implement the result extraction logic after form submission
2. Add error handling and retries
3. Implement batch processing for multiple queries
4. Add rate limiting to avoid overwhelming the server
5. Create a CLI interface for easy usage
