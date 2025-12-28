# 简化版PowerShell脚本：将scripts.txt拆分成45个字符的小文件
# 编号从0001开始

# 设置输入和输出路径
$inputFile = "ai.generator\input\scripts.txt"
$outputDir = "ai.generator\output\split_files"

# 检查输入文件是否存在
if (-not (Test-Path $inputFile)) {
    Write-Host "错误：找不到输入文件 $inputFile" -ForegroundColor Red
    exit 1
}

# 创建输出目录
if (-not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
    Write-Host "已创建输出目录：$outputDir" -ForegroundColor Green
}

# 读取文件内容并移除换行符
$content = [System.IO.File]::ReadAllText($inputFile, [System.Text.Encoding]::UTF8)
$content = $content -replace "`r`n", "" -replace "`n", "" -replace "`r", ""

Write-Host "原始文件总字符数：$($content.Length)" -ForegroundColor Cyan

# 拆分参数
$chunkSize = 45
$fileCounter = 1

# 拆分文件
for ($i = 0; $i -lt $content.Length; $i += $chunkSize) {
    $endIndex = [Math]::Min($i + $chunkSize, $content.Length)
    $chunk = $content.Substring($i, $endIndex - $i)
    
    # 生成文件名
    $fileName = "{0:D4}.txt" -f $fileCounter
    $filePath = Join-Path $outputDir $fileName
    
    # 写入文件
    [System.IO.File]::WriteAllText($filePath, $chunk, [System.Text.Encoding]::UTF8)
    
    Write-Host "已生成文件：$fileName (位置: $i-$($endIndex-1))" -ForegroundColor Gray
    $fileCounter++
}

Write-Host "`n拆分完成！共生成 $($fileCounter-1) 个文件" -ForegroundColor Green
Write-Host "文件保存在：$outputDir" -ForegroundColor Green

# 显示前几个文件内容作为示例
Write-Host "`n前5个文件内容示例：" -ForegroundColor Yellow
Get-ChildItem -Path $outputDir -Filter "*.txt" | Sort-Object Name | Select-Object -First 5 | ForEach-Object {
    $fileContent = [System.IO.File]::ReadAllText($_.FullName, [System.Text.Encoding]::UTF8)
    Write-Host "$($_.Name) : $($fileContent.Length) 字符"
    Write-Host "内容: '$fileContent'"
    Write-Host ""
}
