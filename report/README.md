# Hướng dẫn báo cáo (LaTeX)

Mô tả nhanh cách build PDF và quy ước nhánh cho báo cáo.

Build local (yêu cầu `xelatex` hoặc `latexmk`):
```bash
latexmk -xelatex -interaction=nonstopmode -file-line-error report/main.tex
# hoặc
pdflatex report/main.tex
bibtex report/main
latexmk -xelatex report/main.tex
```

Quy ước file:
- `main.tex`: entry file (chứa preamble).
- `chapters/`: mỗi chương một file, mỗi người làm trên file riêng.
- `bib/`: thư mục `references.bib`.

Branching:
- Đẩy source `.tex` lên nhánh `report` hoặc `feature/*` rồi tạo PR vào `report`.
