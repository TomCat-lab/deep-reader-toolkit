import sys
import zipfile
import re
from pathlib import Path
from html.parser import HTMLParser

from bs4 import BeautifulSoup


class _EPubExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text: list[str] = []
        self.skip = False
        self.tag_stack: list[str] = []

    def handle_starttag(self, tag, attrs):
        self.tag_stack.append(tag)
        if tag in ("script", "style"):
            self.skip = True
        elif tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            level = int(tag[1])
            self.text.append("\n" + "#" * level + " ")
        elif tag == "p":
            self.text.append("\n\n")
        elif tag == "br":
            self.text.append("\n")
        elif tag == "li":
            self.text.append("\n- ")
        elif tag in ("strong", "b"):
            self.text.append("**")
        elif tag in ("em", "i"):
            self.text.append("*")

    def handle_endtag(self, tag):
        if self.tag_stack and self.tag_stack[-1] == tag:
            self.tag_stack.pop()
        if tag in ("script", "style"):
            self.skip = False
        elif tag in ("strong", "b"):
            self.text.append("**")
        elif tag in ("em", "i"):
            self.text.append("*")

    def handle_data(self, data):
        if not self.skip:
            self.text.append(data)


def epub_to_md_bs4(path: str) -> str:
    z = zipfile.ZipFile(path)
    files = sorted(n for n in z.namelist() if n.endswith((".html", ".xhtml", ".htm")))
    parts: list[str] = []
    for f in files:
        html = z.read(f).decode("utf-8", "ignore")
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup.find_all(["script", "style"]):
            tag.decompose()
        text = _html_to_md(soup)
        if len(text) < 10:
            continue
        parts.append(text)
    return "\n\n---\n\n".join(parts)


def _html_to_md(soup) -> str:
    result: list[str] = []
    for el in soup.children:
        if isinstance(el, str):
            result.append(el.strip())
            continue
        tag = el.name
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            level = int(tag[1])
            result.append(f"\n{'#' * level} {el.get_text(strip=True)}\n")
        elif tag == "p":
            result.append(f"\n\n{el.get_text(strip=True)}\n")
        elif tag == "li":
            result.append(f"\n- {el.get_text(strip=True)}")
        elif tag in ("strong", "b"):
            result.append(f"**{el.get_text(strip=True)}**")
        elif tag in ("em", "i"):
            result.append(f"*{el.get_text(strip=True)}*")
        else:
            result.append(_html_to_md(el))
    return re.sub(r"\n{3,}", "\n\n", "".join(result)).strip()


def pdf_to_md(path: str) -> str:
    import fitz

    doc = fitz.open(path)
    parts: list[str] = []
    for i, page in enumerate(doc):
        text = page.get_text()
        if text.strip():
            parts.append(text.strip())
    doc.close()
    return "\n\n---\n\n".join(parts)


def txt_to_md(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()
    lines = text.split("\n")
    result: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            result.append("")
        elif re.match(r"^第[一二三四五六七八九十百千\d]+[章节篇部回]", stripped):
            result.append(f"\n## {stripped}\n")
        elif re.match(r"^Chapter\s+\d+", stripped, re.IGNORECASE):
            result.append(f"\n## {stripped}\n")
        elif len(stripped) < 30 and stripped.endswith(("。", "：", ":", ".")):
            result.append(f"\n### {stripped}\n")
        else:
            result.append(stripped)
    return re.sub(r"\n{3,}", "\n\n", "\n".join(result)).strip()


def convert(path: str) -> str:
    p = Path(path)
    suffix = p.suffix.lower()
    if suffix == ".epub":
        return epub_to_md_bs4(path)
    elif suffix == ".pdf":
        return pdf_to_md(path)
    elif suffix in (".txt", ".text"):
        return txt_to_md(path)
    else:
        raise ValueError(f"不支持的格式: {suffix}，仅支持 .epub .pdf .txt")


def main():
    import click
    from rich.console import Console

    console = Console()
    if len(sys.argv) < 2:
        console.print("[bold red]用法:[/bold red] readbook <文件路径> [输出路径]")
        console.print("  支持 .epub .pdf .txt → .md")
        sys.exit(1)

    src = sys.argv[1]
    if not Path(src).exists():
        console.print(f"[red]文件不存在: {src}[/red]")
        sys.exit(1)

    dst = sys.argv[2] if len(sys.argv) > 2 else str(Path(src).with_suffix(".md"))

    console.print(f"[cyan]转换中:[/cyan] {src} → {dst}")
    try:
        md = convert(src)
    except Exception as e:
        console.print(f"[red]转换失败: {e}[/red]")
        sys.exit(1)

    Path(dst).parent.mkdir(parents=True, exist_ok=True)
    with open(dst, "w", encoding="utf-8") as f:
        f.write(md)

    chars = len(md)
    lines = md.count("\n") + 1
    console.print(f"[green]完成![/green] {chars:,} 字符, {lines:,} 行 → {dst}")


if __name__ == "__main__":
    main()