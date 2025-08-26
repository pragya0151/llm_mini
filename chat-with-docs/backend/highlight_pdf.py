
# backend/highlight_pdf.py
import fitz  # PyMuPDF
import textwrap
from typing import List

def _generate_snippets(text: str, max_snippets: int = 6, window: int = 300, step: int = 200) -> List[str]:
    """
    Create a few overlapping candidate snippets from the long text to search for in PDF.
    This improves the chance of matching PDF text (which may have newlines, truncated lines, etc).
    """
    if not text:
        return []
    text = " ".join(text.split())  # collapse whitespace
    snippets = []
    start = 0
    length = len(text)
    while len(snippets) < max_snippets and start < length:
        snippet = text[start:start + window]
        if snippet.strip():
            snippets.append(snippet)
        start += step
    # also include the very first 200 chars as a final bite if not already included
    if snippets and len(snippets) < max_snippets:
        first = text[:200]
        if first not in snippets:
            snippets.append(first)
    return snippets

def highlight_pdf(pdf_path: str, text_to_highlight: str, output_path: str) -> List[str]:
    """
    Attempt to highlight portions of `text_to_highlight` inside `pdf_path` and save to `output_path`.

    Returns:
        - list of snippet strings that were actually highlighted (may be empty).
    """
    if not text_to_highlight:
        return []

    try:
        doc = fitz.open(pdf_path)
    except Exception:
        return []

    matched_snippets: List[str] = []
    # Candidates to search for (multiple tries)
    candidates = _generate_snippets(text_to_highlight, max_snippets=8, window=400, step=240)

    try:
        for snippet in candidates:
            # search_for expects reasonably short substrings; try a few variants:
            ss = snippet.strip()
            if not ss:
                continue

            found_any = False
            # Search page-by-page
            for page in doc:
                try:
                    rects = page.search_for(ss)
                except Exception:
                    rects = []

                if rects:
                    # annotate first few rects found on that page
                    for r in rects[:6]:
                        try:
                            page.add_highlight_annot(r)
                        except Exception:
                            pass
                    found_any = True

                if found_any:
                    matched_snippets.append(ss)
                    # stop searching this snippet further; go to next snippet candidate
                    break

            # if we found enough snippets, stop early (prevents huge annotations)
            if len(matched_snippets) >= 6:
                break

        if matched_snippets:
            try:
                doc.save(output_path)
            except Exception:
                # fallback: try incremental save
                try:
                    doc.save(output_path, garbage=4, deflate=True)
                except Exception:
                    pass
    finally:
        try:
            doc.close()
        except Exception:
            pass

    return matched_snippets

