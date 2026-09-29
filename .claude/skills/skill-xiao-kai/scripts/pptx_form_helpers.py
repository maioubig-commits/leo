"""
Reusable helpers for filling data into the 開發表單.pptx style table template.

Requires: python-pptx, pdfplumber (pip install python-pptx pdfplumber)
Works on plain python3 (no 3.10+ match-statement dependency), since the target
machine may not have a modern python or LibreOffice installed.
"""
import zipfile
import xml.dom.minidom as minidom


def dump_table(pptx_path, slide_index=0):
    """Print every VISIBLE cell (row, col, text) in the first table found on a slide.

    Only prints cells where is_spanned is False — cells that are covered by a
    merge from another cell are invisible in the rendered slide even if their
    raw XML still holds leftover text (a common artifact in hand-edited
    templates). Writing to a spanned cell has no visual effect; always target
    the reported (row, col) pairs instead.
    """
    from pptx import Presentation

    prs = Presentation(pptx_path)
    slide = prs.slides[slide_index]
    for shape in slide.shapes:
        if not shape.has_table:
            continue
        tbl = shape.table
        for r_idx, row in enumerate(tbl.rows):
            for c_idx, cell in enumerate(row.cells):
                if not cell.is_spanned:
                    print(f"[{r_idx},{c_idx}] spanned={cell.is_spanned} "
                          f"origin={cell.is_merge_origin} text={cell.text!r}")


def set_cell_text(cell, new_text):
    """Replace a table cell's text while preserving the first run's formatting.

    Assigning text_frame.text directly collapses all paragraphs into a single
    unstyled run and loses the template's font/color/size — always go through
    the existing runs instead.
    """
    tf = cell.text_frame
    p = tf.paragraphs[0]
    runs = p.runs
    if not runs:
        tf.text = new_text
        return
    runs[0].text = new_text
    for r in runs[1:]:
        r.text = ''
    for extra_p in tf.paragraphs[1:]:
        for r in extra_p.runs:
            r.text = ''


# Rough per-character width in "em" units (fraction of font size), used only
# to size-check a cell before committing to a font size — not a real text
# shaping engine. CJK full-width glyphs render close to 1em; ASCII digits and
# punctuation are narrower. Treat the result as a conservative estimate, not
# an exact fit.
def _char_width_em(ch):
    o = ord(ch)
    if o < 128:
        if ch == ' ':
            return 0.28
        if ch.isdigit():
            return 0.55
        return 0.5
    return 1.0


def estimate_text_width_pt(text, font_size_pt):
    return sum(_char_width_em(ch) for ch in text) * font_size_pt


def fit_font_size_pt(text, usable_width_pt, max_size_pt, min_size_pt=9):
    """Return the largest font size (<= max_size_pt) that fits `text` on one
    line within usable_width_pt, estimated via estimate_text_width_pt.

    If even min_size_pt overflows, returns min_size_pt anyway — at that point
    let the text wrap (table rows grow to fit; PowerPoint won't clip it) and
    consider shortening the text instead of shrinking further.
    """
    size = max_size_pt
    while size > min_size_pt:
        if estimate_text_width_pt(text, size) <= usable_width_pt:
            return size
        size -= 0.5
    return min_size_pt


def cell_usable_width_pt(table, col_start, col_span, margin_pt=14.4):
    """Sum the gridCol widths (EMU) a merged cell spans and convert to points,
    minus the default cell left/right margins (0.1in each = 7.2pt, 14.4pt
    total) unless the template overrides marL/marR explicitly.
    """
    cols = table._tbl.tblGrid.gridCol_lst
    total_emu = sum(int(cols[i].get('w')) for i in range(col_start, col_start + col_span))
    return total_emu / 12700 - margin_pt


def validate_pptx(pptx_path):
    """Zip integrity + XML well-formedness check that works on any python3 —
    the pptx skill's validate.py needs 3.10+ (match statement) and LibreOffice,
    neither of which may be available. This is a lighter but still useful
    sanity check to run before handing the file back to the user.
    """
    z = zipfile.ZipFile(pptx_path)
    bad = z.testzip()
    if bad:
        return False, f"corrupt member: {bad}"
    for name in z.namelist():
        if name.endswith('.xml') or name.endswith('.rels'):
            try:
                minidom.parseString(z.read(name))
            except Exception as e:
                return False, f"XML error in {name}: {e}"
    return True, "zip + XML OK"


def render_pdf_page_to_image(pdf_path, out_png, page_index=0, resolution=200):
    """Render a PDF page to PNG so a human (or Read tool) can visually confirm
    fields the text extractor may have silently dropped. This matters: on a
    real 建物謄本, pdfplumber's extract_text() missed the 所有權人 地址 line
    entirely (came back blank) even though the PDF clearly shows a highlighted
    address when rendered — always cross-check like this before treating a
    "blank" field as genuinely blank.
    """
    import pdfplumber

    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[page_index]
        im = page.to_image(resolution=resolution)
        im.save(out_png)
    return out_png
