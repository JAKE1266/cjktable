"""cjktable 全覆盖测试:宽度规则、排版原语、表格与条形图、边界用例。"""

import unittest

from cjktable import bars, char_width, pad, table, truncate, width
from cjktable.render import _COLUMN_GAP, _is_numeric_column


class CharWidthTest(unittest.TestCase):
    def test_ascii_and_cjk(self):
        self.assertEqual(char_width("a"), 1)
        self.assertEqual(char_width("中"), 2)
        self.assertEqual(char_width("Ａ"), 2)          # 全角字母 F
        self.assertEqual(char_width("！"), 2)          # 全角标点 F

    def test_wide_punctuation(self):
        self.assertEqual(char_width("，"), 2)          # 全角逗号 F
        self.assertEqual(char_width("、"), 2)          # 顿号 W

    def test_ambiguous_width_is_one(self):
        # EAW=A(模糊宽度)在现代终端按 1 列渲染,与 wcwidth 默认一致
        for ch in ("※", "·", "×", "±", "°"):
            self.assertEqual(char_width(ch), 1, f"U+{ord(ch):04X}")

    def test_combining_marks_are_zero(self):
        self.assertEqual(char_width("\u0301"), 0)      # 重音符号
        self.assertEqual(char_width("\u20e3"), 0)      # 键帽组合符号
        self.assertEqual(width("e\u0301"), 1)          # é 的分解形式占 1 列

    def test_zero_width_chars(self):
        for ch in ("\u200b", "\u200c", "\u200d", "\u2060", "\ufeff"):
            self.assertEqual(char_width(ch), 0, f"U+{ord(ch):04X}")
        self.assertEqual(width("a\u200bb"), 2)

    def test_control_chars_are_zero(self):
        self.assertEqual(char_width("\x07"), 0)        # BEL
        self.assertEqual(char_width("\t"), 0)          # 制表符按不可见处理

    def test_common_emoji_are_two(self):
        self.assertEqual(char_width("😀"), 2)
        self.assertEqual(char_width("🚀"), 2)
        self.assertEqual(char_width("🈶"), 2)          # 该符号本身是 W
        self.assertEqual(width("👍ok"), 4)

    def test_variation_selector_zero(self):
        self.assertEqual(char_width("\ufe0f"), 0)      # 变体选择符
        self.assertEqual(width("#\ufe0f\u20e3"), 1)    # 键帽序列整体 1 列

    def test_rejects_non_char(self):
        for bad in ("ab", "", 65, None):
            with self.assertRaises(ValueError):
                char_width(bad)


class WidthTest(unittest.TestCase):
    def test_mixed_text(self):
        self.assertEqual(width(""), 0)
        self.assertEqual(width("中文abc"), 7)
        self.assertEqual(width("中英混合 text"), 13)  # 4 个全角(8)+ 空格 + text(4)

    def test_type_check(self):
        with self.assertRaises(TypeError):
            width(123)

    def test_matches_manual_count(self):
        samples = ["你好,世界!", "x😀y", "\u200b中日\u2060英", "a" * 10]
        for sample in samples:
            self.assertEqual(width(sample), sum(char_width(c) for c in sample))


class PadTest(unittest.TestCase):
    def test_left_right_center(self):
        self.assertEqual(pad("ab", 5), "ab   ")
        self.assertEqual(pad("ab", 5, "right"), "   ab")
        self.assertEqual(pad("ab", 5, "center"), " ab  ")
        self.assertEqual(pad("ab", 6, "center"), "  ab  ")

    def test_cjk_padding_exact_terminal_width(self):
        padded = pad("中文", 8)
        self.assertEqual(padded, "中文" + " " * 4)
        self.assertEqual(width(padded), 8)

    def test_overflow_returned_unchanged(self):
        self.assertEqual(pad("中文超宽", 2), "中文超宽")

    def test_zero_width(self):
        self.assertEqual(pad("ab", 0), "ab")

    def test_invalid_align(self):
        with self.assertRaises(ValueError):
            pad("a", 2, "middle")

    def test_negative_width_clamped(self):
        self.assertEqual(pad("a", -3), "a")


class TruncateTest(unittest.TestCase):
    def test_fits_unchanged(self):
        self.assertEqual(truncate("abc", 5), "abc")
        self.assertEqual(truncate("中文", 4), "中文")

    def test_ascii_truncation(self):
        self.assertEqual(truncate("abcdef", 4), "abc…")   # abc(3)+省略号(1)=4
        self.assertEqual(truncate("abcdef", 3), "ab…")

    def test_cjk_cut_alignment(self):
        # 预算 5:中(2)+省略号(1)+文(2)= 5 → 只能放下 中+省略号
        self.assertEqual(truncate("中文测试", 5), "中文…")
        self.assertEqual(width(truncate("中文测试", 5)), 5)
        # 预算 4:省略号预留 1,可用 3 → 中(2)+省略号
        self.assertEqual(truncate("中文测试", 4), "中…")
        self.assertLessEqual(width(truncate("中文测试", 4)), 4)

    def test_tiny_budget(self):
        self.assertEqual(truncate("中文", 1), "…")
        self.assertEqual(truncate("中文", 0), "")
        self.assertEqual(truncate("中文", -1), "")

    def test_custom_ellipsis(self):
        self.assertEqual(truncate("abcdef", 5, ellipsis="..."), "ab...")
        self.assertEqual(truncate("abcdef", 2, ellipsis="..."), "")  # 省略号都放不下

    def test_no_overshoot_with_zero_width(self):
        result = truncate("a\u200b中文", 2)
        self.assertLessEqual(width(result), 2)

    def test_emoji_cut(self):
        result = truncate("😀😀😀", 3)
        self.assertEqual(result, "😀…")
        self.assertEqual(width(result), 3)

    def test_result_never_exceeds_budget(self):
        samples = ["混合 text 😀 中文", "a" * 20, "中日英英中日"]
        for sample in samples:
            for budget in range(0, 12):
                self.assertLessEqual(width(truncate(sample, budget)), max(0, budget))


class NumericColumnTest(unittest.TestCase):
    def test_numeric_detection(self):
        self.assertTrue(_is_numeric_column(["1", "2.5", "1e3"]))
        self.assertFalse(_is_numeric_column(["1", "a"]))
        self.assertFalse(_is_numeric_column([]))
        self.assertTrue(_is_numeric_column(["", "2.5"]))  # 空串(如 NULL)不干扰判断


class TableTest(unittest.TestCase):
    def test_basic_alignment(self):
        out = table(["Name", "Qty"], [["键盘", 99], ["mouse", 7]])
        lines = out.splitlines()
        self.assertEqual(len(lines), 4)  # 表头 + 分隔线 + 2 行
        header_cells = lines[0].split(_COLUMN_GAP)
        self.assertEqual(header_cells[0].strip(), "Name")
        self.assertEqual(header_cells[1].strip(), "Qty")

    def test_auto_numeric_right_align(self):
        out = table(["商品", "库存"], [["键盘", 99], ["鼠标垫超长名称", 7]])
        lines = out.splitlines()[2:]
        self.assertTrue(lines[0].rstrip().endswith("99"))
        self.assertTrue(lines[1].rstrip().endswith("7"))
        # 右对齐:两行的总显示宽度一致(数字贴齐同一右边界)
        self.assertEqual(width(lines[0]), width(lines[1]))

    def test_explicit_aligns(self):
        out = table(["AAA", "B"], [["x", 1]], aligns=["center", "left"])
        self.assertIn(" x ", out.splitlines()[2])

    def test_aligns_length_mismatch(self):
        with self.assertRaises(ValueError):
            table(["A", "B"], [["x", 1]], aligns=["left"])

    def test_max_col_width_truncates(self):
        out = table(["Col"], [["a" * 50]], max_col_width=10)
        self.assertIn("…", out)                 # 被截断
        self.assertNotIn("a" * 11, out)         # 且确实截短了

    def test_null_cells(self):
        out = table(["A", "B"], [["x", None]], null_text="∅")
        self.assertIn("∅", out)
        out2 = table(["A", "B"], [["x", None]])
        self.assertNotIn("None", out2)

    def test_short_rows_padded_with_empty(self):
        out = table(["A", "B", "C"], [["x", 1]])
        self.assertEqual(len(out.splitlines()[2].split(_COLUMN_GAP)), 3)

    def test_long_rows_truncated_to_ncols(self):
        out = table(["A"], [["x", "extra", "more"]])
        self.assertNotIn("extra", out)

    def test_empty_rows(self):
        out = table(["A", "B"], [])
        self.assertEqual(len(out.splitlines()), 2)

    def test_cjk_columns_line_up(self):
        out = table(["商品", "数量"], [["显示器超宽屏", 3], ["键盘", 100]])
        # 右对齐数值列:所有数据行总显示宽度一致
        data = out.splitlines()[2:]
        self.assertEqual(len({width(line) for line in data}), 1)


class BarsTest(unittest.TestCase):
    def test_scaling(self):
        out = bars([("A", 10), ("B", 5)])
        line_a = [l for l in out.splitlines() if "A " in l or l.strip().startswith("A")][0]
        line_b = [l for l in out.splitlines() if l.strip().startswith("B")][0]
        self.assertGreater(line_a.count("█"), line_b.count("█"))

    def test_zero_and_negative(self):
        out = bars([("A", 0), ("B", -5), ("C", 8)])
        b_line = [l for l in out.splitlines() if l.strip().startswith("B")][0]
        self.assertNotIn("█", b_line)          # 负值按 0 处理,无条形
        self.assertIn("0", b_line)

    def test_empty_items(self):
        self.assertEqual(bars([]), "(no data)")

    def test_int_float_notes(self):
        out = bars([("int", 5), ("float", 2.5)])
        self.assertIn("5", out)
        self.assertIn("2.5", out)


class IntegrationTest(unittest.TestCase):
    """真实场景:中文报表端到端。"""

    def test_report(self):
        out = table(
            ["商品", "销量", "销售额"],
            [["机械键盘", 120, 61718.4], ["无线鼠标", None, 4235.5], ["显示器", 13, 16887]],
            max_col_width=12,
        )
        # 不变式:所有行(含表头与分隔线)总显示宽度一致 → 列真正对齐
        lines = out.splitlines()
        self.assertEqual(len(lines), 5)
        self.assertEqual(len({width(line) for line in lines}), 1)


if __name__ == "__main__":
    unittest.main()
