import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from csv_rescue_cn import convert_file, detect_encoding


class TestDetect(unittest.TestCase):
    def test_gbk_detected_as_gb18030_family(self):
        raw = "姓名,城市\n张三,城东\n".encode("gbk")
        self.assertIn(detect_encoding(raw), ("gb18030", "gbk"))

    def test_utf8_bom(self):
        self.assertEqual(detect_encoding(b"\xef\xbb\xbf" + "a,b\n".encode()), "utf-8-sig")

    def test_utf8(self):
        self.assertEqual(detect_encoding("你好,世界\n".encode("utf-8")), "utf-8")


class TestConvert(unittest.TestCase):
    def test_gbk_roundtrip_trim_and_dedupe(self):
        rows = "姓名, 城市 \n张三, 城东\n张三,城东\n\n李四,城西\n"
        with tempfile.TemporaryDirectory() as d:
            src, out = Path(d) / "in.csv", Path(d) / "out.csv"
            src.write_bytes(rows.encode("gbk"))
            stats = convert_file(src, out, trim=True, dedupe=True)
            text = out.read_text(encoding="utf-8")
        self.assertIn("张三,城东", text)
        self.assertEqual(stats.duplicates_removed, 1)
        self.assertEqual(stats.empty_rows_removed, 1)
        self.assertEqual(stats.rows_out, 3)  # header + 2 unique data rows

    def test_never_garbles_chinese(self):
        with tempfile.TemporaryDirectory() as d:
            src, out = Path(d) / "in.csv", Path(d) / "out.csv"
            src.write_bytes("名称\n中文测试\n".encode("gb18030"))
            convert_file(src, out)
            self.assertEqual(out.read_text(encoding="utf-8"), "名称\n中文测试\n")


if __name__ == "__main__":
    unittest.main()
