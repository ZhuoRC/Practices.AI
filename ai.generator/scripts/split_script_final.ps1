# PowerShell脚本：将scripts.txt拆分成45个字符的小文件
# 编号从0001开始

$inputFile = "ai.generator\input\scripts.txt"
$outputDir = "ai.generator\output\split_files"

# 检查输入文件
if (-not (Test-Path $inputFile)) {
    Write-Host "Error: Input file not found: $inputFile" -ForegroundColor Red
    exit 1
}

# 创建输出目录
if (-not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
    Write-Host "Created output directory: $outputDir" -ForegroundColor Green
}

# 读取文件内容
$content = [System.IO.File]::ReadAllText($inputFile, [System.Text.Encoding]::UTF8)
$content = $content -replace "`r`n", "" -replace "`n", "" -replace "`r", ""

Write-Host "Total characters: $($content.Length)" -ForegroundColor Cyan

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
    
    Write-Host "Generated: $fileName (position: $i-$($endIndex-1))" -ForegroundColor Gray
    $fileCounter++
}

Write-Host "`nSplit complete! Generated $($fileCounter-1) files" -ForegroundColor Green
Write-Host "Files saved to: $outputDir" -ForegroundColor Green

# 显示文件列表
Write-Host "`nGenerated files:" -ForegroundColor Yellow
Get-ChildItem -Path $outputDir -Filter "*.txt" | Sort-Object Name | ForEach-Object {
    $fileContent = [System.IO.File]::ReadAllText($_.FullName, [System.Text.Encoding]::UTF8)
    Write-Host "$($_.Name) : $($fileContent.Length) chars"
}
