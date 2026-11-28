from importlib.metadata import distribution
from pathlib import Path

import cjktable


dist = distribution("cjktable")
assert dist.version == cjktable.__version__ == "0.2.0"
assert dist.metadata["Requires-Python"] == ">=3.9"
assert not dist.requires
assert dist.read_text("top_level.txt").split() == ["cjktable"]
assert Path(cjktable.__file__).resolve() == Path(
    dist.locate_file("cjktable/__init__.py")).resolve()

assert cjktable.width("中文") == 4
assert cjktable.width("e\u0301") == 1
assert cjktable.pad("中", 4) == "中  "
assert cjktable.truncate("中文测试", 5) == "中文…"
assert cjktable.wrap("ab中文cd", 4) == ["ab中", "文cd"]
assert cjktable.wrap("a\u200bb", 1) == ["a\u200b", "b"]
rendered = cjktable.table(["商品", "库存"], [["键盘", 99], ["鼠标垫", 7]])
assert len({cjktable.width(line) for line in rendered.splitlines()}) == 1
assert cjktable.bars([]) == "(no data)"

print("cjktable 0.2.0 installed wheel smoke test passed")
