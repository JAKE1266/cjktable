# 更新日志

本项目遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/) 格式,
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [0.1.0] - 2026-11-21

### 新增
- `char_width` / `width`:CJK 感知的终端显示宽度(组合符号、零宽字符、控制字符为 0;
  全角与宽字符为 2;常见 emoji 为 2;EAW 模糊宽度按 1 列,与 wcwidth 默认一致)
- `pad`:按显示宽度补齐(left / right / center)
- `truncate`:预留省略号的显示宽度截断,保证结果永不超预算
- `table`:CJK 对齐表格(数值列自动右对齐、超宽截断、None 占位)
- `bars`:横向条形图
- 42 个单元测试覆盖全部边界用例;GitHub Actions 三系统 × 三 Python 版本 CI
