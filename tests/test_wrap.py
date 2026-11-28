"""wrap() 按显示宽度换行测试。"""

import unittest

from cjktable import wrap
from cjktable.core import width


class WrapTest(unittest.TestCase):
    def test_english_word_wrap(self):
        self.assertEqual(wrap("hello world", 5), ["hello", "world"])

    def test_cjk_char_wrap(self):
        self.assertEqual(wrap("中文测试", 4), ["中文", "测试"])

    def test_cjk_wide_columns(self):
        self.assertEqual(wrap("一二三四五六", 4), ["一二", "三四", "五六"])

    def test_mixed_text(self):
        self.assertEqual(wrap("ab中文cd", 4), ["ab中", "文cd"])

    def test_hard_break_long_word(self):
        self.assertEqual(wrap("abcdefgh", 3), ["abc", "def", "gh"])

    def test_explicit_newline(self):
        self.assertEqual(wrap("a\nb", 10), ["a", "b"])

    def test_empty(self):
        self.assertEqual(wrap("", 5), [""])

    def test_columns_validation(self):
        with self.assertRaises(ValueError):
            wrap("x", 0)
        with self.assertRaises(TypeError):
            wrap(None, 5)

    def test_zero_width_stays_with_base(self):
        result = wrap("a\u200bb", 1)
        # 零宽字符跟随 a,不会产生独立的零宽行
        self.assertEqual(result, ["a\u200b", "b"])
        self.assertTrue(all(width(line) <= 1 for line in result))

    def test_newline_leading_spaces_dropped(self):
        self.assertEqual(wrap("ab   cd", 2), ["ab", "cd"])

    def test_whitespace_only_paragraph(self):
        self.assertEqual(wrap("   ", 5), [""])

    def test_every_line_within_budget(self):
        # 不变式:每行显示宽度 ≤ max(预算, 最宽单元)——单个宽字形无法再切
        from cjktable.core import _char_units
        samples = ["hello world foo bar", "中文测试混合 text 😀", "a" * 50]
        for sample in samples:
            widest = max(width(u) for u in _char_units(sample))
            for budget in range(1, 20):
                for line in wrap(sample, budget):
                    self.assertLessEqual(
                        width(line), max(budget, widest),
                        f"sample={sample!r} budget={budget} line={line!r}")


if __name__ == "__main__":
    unittest.main()
