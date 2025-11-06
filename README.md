# PDF Toolkit

Python PDF 工具箱，提供命令列介面整合的合併、拆分、刪除、旋轉、水印、壓縮與資訊查詢等功能。

## 功能特性
- ✅ 合併多個 PDF 檔案
- ✅ 拆分 PDF（單頁或指定範圍）
- ✅ 刪除指定頁面（反向刪除避免索引錯位）
- ✅ 旋轉頁面並累加既有角度
- ✅ 為所有頁面添加自訂文字水印
- ✅ 使用 pikepdf 進行基礎壓縮，支援線性化
- ✅ 查詢 PDF 檔案資訊與中繼資料

## 安裝
```bash
python -m venv .venv
source .venv/bin/activate  # Windows 請使用 .venv\Scripts\activate
pip install -r requirements.txt
```

## 使用方法

所有指令皆透過 `python pdf_toolkit.py <子命令> [...]` 呼叫。可使用 `-h` 或 `--help` 檢視完整說明。

### 合併 PDF
```bash
python pdf_toolkit.py merge input1.pdf input2.pdf input3.pdf -o merged.pdf
```

### 拆分 PDF
```bash
# 拆分為單頁
python pdf_toolkit.py split input.pdf -d output_folder/

# 按範圍拆分
python pdf_toolkit.py split input.pdf -d output_folder/ -p "1-10,21-30"
```

### 刪除頁面
```bash
python pdf_toolkit.py delete input.pdf -p "1,3,5-8" -o trimmed.pdf
```

### 旋轉頁面
```bash
python pdf_toolkit.py rotate input.pdf -p "1-5" -a 90 -o rotated.pdf
```

### 添加文字水印
```bash
python pdf_toolkit.py watermark input.pdf -t "CONFIDENTIAL" -o watermarked.pdf
# 自訂參數
python pdf_toolkit.py watermark input.pdf -t "DRAFT" --size 48 --alpha 0.2 --angle 30 -o draft.pdf
```

### 壓縮優化
```bash
# 基礎壓縮（可選線性化）
python pdf_toolkit.py optimize input.pdf -o optimized.pdf --linearize

# 進階壓縮旗標（目前以基礎壓縮回退並顯示提醒）
python pdf_toolkit.py optimize input.pdf -o optimized_aggressive.pdf --aggressive --dpi 150
```

### 查詢 PDF 資訊
```bash
python pdf_toolkit.py info input.pdf
```

## 頁碼語法
- `1,3,5`：指定單頁
- `1-5`：連續範圍
- `10-`：從第 10 頁到最後
- `1-3,5-7,10-`：混合使用

所有頁碼均為 1-based；工具會自動去除重複並排序。

## 快速驗證（選用）
專案附帶 `quick_test.py`，可用於批次驗證各功能（需準備測試用 PDF）：
```bash
python quick_test.py
```

## 系統需求
- Python 3.8+
- PyMuPDF (fitz)
- pikepdf
- Pillow
- tqdm

## 授權
MIT License
