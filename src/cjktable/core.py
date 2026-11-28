"""宽度计算与文本排版原语。

宽度规则(近似 ``wcwidth``,覆盖绝大多数日常场景):

- 组合符号(Mn/Me)、格式字符(Cf,含零宽空格/ZWJ/BOM)、控制字符(Cc)→ **0**
- East Asian Width 为 W(宽)或 F(全角)→ **2**
- 常见 emoji(符号类、码位 ≥ U+1F000)→ **2**
- 其余 → **1**

已知局限:ZWJ 组合 emoji(如家庭 emoji)按成员宽度简单累加,可能与个别终端
渲染有出入;需要像素级精确请使用 ``wcwidth``。
"""

from __future__ import annotations

import unicodedata

_ZEROWIDTH = frozenset("\u200b\u2060")

_ALIGN_CHOICES = ("left", "right", "center")


def char_width(ch: str) -> int:
    """单个字符的终端显示宽度(0 / 1 / 2)。"""
    if not isinstance(ch, str) or len(ch) != 1:
        raise ValueError(f"char_width 只接受单个字符,得到:{ch!r}")
    if ch in _ZEROWIDTH:
        return 0
    if unicodedata.category(ch) in ("Mn", "Me", "Cf", "Cc"):
        return 0
    if unicodedata.east_asian_width(ch) in ("W", "F"):
        return 2
    if unicodedata.category(ch) == "So" and ord(ch) >= 0x1F000:
        return 2  # 常见 emoji 在等宽终端按 2 列渲染
    return 1


def _display_width(text: str) -> int:
    """内部实现:字符串显示宽度(避免与 pad/truncate 的 width 参数重名)。"""
    return sum(char_width(ch) for ch in text)


def width(text: str) -> int:
    """字符串的终端显示宽度(逐字符累加)。"""
    if not isinstance(text, str):
        raise TypeError(f"text 必须是字符串,得到:{type(text).__name__}")
    return _display_width(text)


def pad(text: str, width: int, align: str = "left") -> str:
    """按显示宽度补空格。

    超宽的 ``text`` 原样返回(不截断);需要先截断请配合 :func:`truncate`。
    ``align`` 支持 ``left`` / ``right`` / ``center``。
    """
    if align not in _ALIGN_CHOICES:
        raise ValueError(f"align 只支持 {'/'.join(_ALIGN_CHOICES)},得到:{align!r}")
    if width < 0:
        width = 0
    gap = max(0, width - _display_width(text))
    if align == "left":
        return text + " " * gap
    if align == "right":
        return " " * gap + text
    left = gap // 2
    return " " * left + text + " " * (gap - left)


def truncate(text: str, width: int, ellipsis: str = "…") -> str:
    """按显示宽度截断,预留省略号空间。

    - 放得下时原样返回;
    - 放不下时在预算内逐字符取用,末尾加 ``ellipsis``;
    - 一个字符都放不下时返回省略号本身(若省略号也放不下则返回空串)。
    """
    if width <= 0:
        return ""
    if _display_width(text) <= width:
        return text
    ell_width = _display_width(ellipsis)
    avail = width - ell_width
    out, used = [], 0
    for ch in text:
        w = char_width(ch)
        if used + w > avail:
            break
        out.append(ch)
        used += w
    if not out:
        return ellipsis if ell_width <= width else ""
    return "".join(out) + ellipsis


def _char_units(text: str) -> list:
    """把文本拆成不可分割的单元:基字符 + 其后跟随的零宽/组合字符。"""
    units: list = []
    for ch in text:
        if char_width(ch) == 0 and units:
            units[-1] += ch  # 零宽/组合符号归属前一个基字符,永不拆开
        else:
            units.append(ch)
    return units


def _space_chunks(units: list) -> list:
    """把单元流切成 (是否空格, 块) 的连续段。"""
    chunks: list = []
    current = ""
    current_is_space = None
    for unit in units:
        is_space = unit == " "
        if current and is_space != current_is_space:
            chunks.append((current_is_space, current))
            current = ""
        current_is_space = is_space
        current += unit
    if current:
        chunks.append((current_is_space, current))
    return chunks


def _hard_cut(line: str, columns: int) -> str:
    """按显示宽度硬切一行,返回切掉的前段。"""
    out, used = "", 0
    for unit in _char_units(line):
        w = _display_width(unit)
        if used + w > columns:
            break
        out += unit
        used += w
    return out


def wrap(text: str, columns: int) -> list:
    """按显示宽度把文本换行,返回行列表(不含换行符)。

    规则:

    - 空白处优先断行,新行行首空格丢弃;
    - 无空格可断(如连续中文)时按列宽硬切;
    - 超宽单词硬切;
    - 显式 ``\\n`` 视为强制换行;
    - 组合/零宽字符跟随其基字符,永不拆开;
    - 空字符串输入返回 ``[""]``。
    """
    if not isinstance(text, str):
        raise TypeError(f"text 必须是字符串,得到:{type(text).__name__}")
    if columns < 1:
        raise ValueError(f"columns 至少为 1:{columns}")

    result: list = []
    for para in text.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        start = len(result)
        if para == "":
            result.append("")
            continue
        line = ""
        pending = _space_chunks(_char_units(para))
        index = 0
        while index < len(pending):
            is_space, chunk = pending[index]
            if is_space and not line:
                index += 1
                continue  # 新行行首空格丢弃
            if _display_width(line) + _display_width(chunk) <= columns or not line:
                line += chunk
                index += 1
            else:
                result.append(line.rstrip(" "))
                line = ""
            while _display_width(line) > columns:  # 单块超宽 → 硬切
                cut = _hard_cut(line, columns)
                if not cut:
                    # 首个单元就超出列宽:仍切出一个单元,保证循环推进
                    units = _char_units(line)
                    cut = units[0]
                result.append(cut)
                line = line[len(cut):]
        if line:
            result.append(line)
        if len(result) == start:  # 纯空白段落也产出一行
            result.append("")
    return result
