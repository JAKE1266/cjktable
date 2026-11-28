# cjktable

> 让中文在等宽终端里**真正对齐**的排版微库。
> `len("中文")` 是 2,但终端占 4 列——这个库替你算清楚,并据此补空格、截断、画表格。

![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Dependencies](https://img.shields.io/badge/dependencies-0-brightgreen)
![Tests](https://img.shields.io/badge/tests-42%20passing-success)

## 为什么需要它?

用 `str.ljust()` / `f-string` 对齐含中文的表格,输出一定是歪的:

```python
print(f"{'商品':<8}{'数量':>6}")
print(f"{'键盘':<8}{99:>6}")
print(f"{'鼠标垫超长名称':<8}{7:>6}")
```

`cjktable` 按终端**显示宽度**计算(全角 2 列、ASCII 1 列、组合符号 0 列):

```python
from cjktable import table

print(table(["商品", "库存"], [["键盘", 99], ["鼠标垫超长名称", 7]]))
```

```
商品          库存
------  ------
键盘           99
鼠标垫超长名称    7
```

## ✨ API

| 函数 | 作用 |
|------|------|
| `char_width(ch)` | 单字符显示宽度(0 / 1 / 2) |
| `width(text)` | 字符串显示宽度 |
| `pad(text, width, align)` | 按显示宽度补齐(left / right / center),超宽不截断 |
| `truncate(text, width, ellipsis="…")` | 按显示宽度截断,预留省略号,结果永不超预算 |
| `table(headers, rows, *, aligns, max_col_width, null_text)` | CJK 对齐表格;数值列自动右对齐 |
| `bars(items, width)` | 横向条形图 `[(标签, 数值), ...]` |

## 📦 安装

```bash
pip install .        # 或克隆后把 src/ 加入 PYTHONPATH
```

零第三方依赖;`pip install cjktable` 上 PyPI 前请先确认名称占用情况。

## 🧠 宽度规则

| 字符类型 | 宽度 | 例子 |
|----------|:----:|------|
| 组合符号 Mn/Me(重音、键帽) | 0 | `e` + `◌́` → 1 列 |
| 格式字符 Cf(零宽空格、ZWJ、BOM) | 0 | `a\u200bb` → 2 列 |
| 控制字符 Cc | 0 | `\t`、`\x07` |
| East Asian Width = W / F | 2 | `中` `Ａ` `！` `、` |
| 常见 emoji(So,码位 ≥ U+1F000) | 2 | 😀 🚀 👍 |
| East Asian Width = A(模糊) | 1 | `※` `·` `×` `°`(与 wcwidth 默认一致) |
| 其余 | 1 | ASCII、西文 |

**已知局限**:ZWJ 组合 emoji(如 👨‍👩‍👧)按成员宽度简单累加;极端终端差异
请用 [`wcwidth`](https://github.com/jquast/wcwidth) 查表级实现。

## 🧪 测试

42 个用例覆盖全部边界:组合字符、零宽字符、变体选择符、emoji 截断、
模糊宽度、超宽截断、数值列自动右对齐、None 占位、行列补齐……

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

## 📁 项目结构

```
cjktable/
├── src/cjktable/
│   ├── core.py     # char_width / width / pad / truncate
│   └── render.py   # table / bars
├── tests/          # 42 个单元测试
└── pyproject.toml
```

## 🗺 路线图

- [ ] `wrap(text, columns)` 按显示宽度换行
- [ ] ZWJ emoji 序列的精准宽度表
- [x] 本库反哺项目集:CashBook / gitdash / csvq 已改用本库(2026-11-21)

## 📄 许可证

[MIT](LICENSE) —— 可自由使用、修改与分发。

---

*同系列项目:[PyToolBox](https://github.com/JAKE1266/py-toolbox) 多功能工具箱 · [CashBook](https://github.com/JAKE1266/cashbook) 命令行记账本 · [gitdash](https://github.com/JAKE1266/gitdash) Git 终端仪表盘 · [DevBox](https://github.com/JAKE1266/devbox) 前端开发工具箱 · [csvq](https://github.com/JAKE1266/csvq) SQL 查 CSV · [duviz](https://github.com/JAKE1266/duviz) 磁盘占用可视化 · [httpoke](https://github.com/JAKE1266/httpoke) HTTP 调试工具 · [mdown](https://github.com/JAKE1266/mdown) Markdown→HTML · [msite](https://github.com/JAKE1266/msite) 静态文档站 · [crony](https://github.com/JAKE1266/crony) cron 表达式解析 · [pomo](https://github.com/JAKE1266/pomo) 番茄钟 · [termplot](https://github.com/JAKE1266/termplot) 终端数据图表 · [filewatch](https://github.com/JAKE1266/filewatch) 目录变更监控 · [packpeek](https://github.com/JAKE1266/packpeek) 压缩包检查与安全解压 · [statline](https://github.com/JAKE1266/statline) 统计摘要 · [difftool](https://github.com/JAKE1266/difftool) 文本差异 · [wordfreq](https://github.com/JAKE1266/wordfreq) 词频统计 · [hexview](https://github.com/JAKE1266/hexview) 十六进制查看器*
