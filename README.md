# csv-rescue-cn

**一键修复中文乱码 CSV** — 自动识别 GBK / GB18030 / Big5 / UTF-8 编码，统一转成干净的 UTF-8，
顺手去掉单元格首尾空格、重复行和空行。零第三方依赖，只用 Python 标准库。

Fix garbled (mojibake) CSV files exported from legacy Chinese systems — auto-detects
GBK / GB18030 / Big5 / UTF-8, rewrites as clean UTF-8, trims cells and drops duplicate
rows. Zero dependencies.

## 为什么需要它？

从老系统、旧版 Excel、政务/银行导出的数据经常是 GBK 编码：

- 用 Python / pandas 按 UTF-8 打开 → `UnicodeDecodeError` 或满屏乱码
- 通用转码工具针对 `.txt`，不懂 CSV 的分隔符、引号和重复行
- 手工在 Excel 里另存为，既慢又容易把长数字、日期改坏

`csv-rescue` 只做一件事，并把它做对：**无损地把 CSV 救回 UTF-8**。它永不覆盖原文件。

## 安装

```bash
pip install csv-rescue-cn
```

或从源码运行（无需安装）：

```bash
git clone https://github.com/sgl022320-alt/csv-rescue-cn
cd csv-rescue-cn && PYTHONPATH=src python -m csv_rescue_cn.cli --help
```

## 用法

```bash
# 只看编码，不改文件
csv-rescue data.csv --dry-run

# 转换 + 去重，结果写到 data.utf8.csv（原文件不动）
csv-rescue data.csv --dedupe

# 指定输出，并加 BOM 让 Windows 版 Excel 直接打开不乱码
csv-rescue data.csv -o clean.csv --dedupe --excel-bom
```

示例输出：

```
input encoding : gb18030 (delimiter ',')
rows           : 518 -> 468 (duplicates removed: 49, empty removed: 1)
written        : clean.csv
```

## 作为库使用

```python
from csv_rescue_cn import convert_file, detect_encoding

print(detect_encoding(open("data.csv", "rb").read()))  # -> "gb18030"
stats = convert_file("data.csv", "clean.csv", dedupe=True)
print(stats.rows_in, stats.rows_out)
```

## 路线图

见 [ROADMAP.md](ROADMAP.md)。欢迎提 Issue：请附上一个能复现乱码的小样本文件
（注意先脱敏）。

## License

MIT — 见 [LICENSE](LICENSE)
