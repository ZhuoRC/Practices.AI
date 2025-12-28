# PowerShell脚本：将scripts.txt拆分成45个字符的小文件
# 编号从0001开始

# 设置输入和输出路径
$inputFile = "ai.generator\input\scripts.txt"
$outputDir = "ai.generator\output\split_files"

# 检查输入文件是否存在
if (-not (Test-Path $inputFile)) {
    Write-Host "错误：找不到输入文件 $inputFile" -ForegroundColor Red
    exit 1
}

# 创建输出目录（如果不存在）
if (-not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
    Write-Host "已创建输出目录：$outputDir" -ForegroundColor Green
}

# 读取文件内容
$content = Get-Content -Path $inputFile -Raw -Encoding UTF8

# 移除换行符，将所有内容连成一行
$content = $content -replace "`r`n", "" -replace "`n", "" -replace "`r", ""

Write-Host "原始文件总字符数：$($content.Length)" -ForegroundColor Cyan

# 计算需要的文件数量
$chunkSize = 45
$totalChunks = [Math]::Ceiling($content.Length / $chunkSize)

Write-Host "将拆分成 $totalChunks 个文件，每个文件 $chunkSize 个字符" -ForegroundColor Cyan

# 拆分文件
$fileCounter = 1
for ($i = 0; $i -lt $content.Length; $i += $chunkSize) {
    # 计算当前块的内容
    $endIndex = [Math]::Min($i + $chunkSize, $content.Length)
    $chunk = $content.Substring($i, $endIndex - $i)
    
    # 生成文件名（4位数字，前面补零）
    $fileName = "{0:D4}" -f $fileCounter + ".txt"
    $filePath = Join-Path $outputDir $fileName
    
    # 写入文件
    $chunk | Out-File -FilePath $filePath -Encoding UTF8 -NoNewline
    
    Write-Host "已生成文件：$fileName (字符位置: $i-$($endIndex-1))" -ForegroundColor Gray
    
    $fileCounter++
}

Write-Host "`n拆分完成！共生成 $($fileCounter-1) 个文件" -ForegroundColor Green
Write-Host "文件保存在：$outputDir" -ForegroundColor Green

# 显示生成的文件列表
Write-Host "`n生成的文件列表：" -ForegroundColor Yellow
Get-ChildItem -Path $outputDir -Filter "*.txt" | Sort-Object Name | ForEach-Object {
    $fileContent = Get-Content -Path $_.FullName -Raw -Encoding UTF8
    Write-Host "$($_.Name) : $($fileContent.Length) 字符 - '$fileContent'"
}
