import csv, io
from typing import List, Dict

DIFF_LEVELS = ("easy","medium","hard")

def _norm_diff(v: str) -> str:
    v = (v or "").strip().lower()
    if v in ("e","1","easy","dễ","de"): return "easy"
    if v in ("h","3","hard","khó","kho"): return "hard"
    return "medium"

def sniff_and_read(file_bytes: bytes) -> List[Dict[str,str]]:
    text = None
    for enc in ("utf-8-sig","utf-8"):
        try:
            text = file_bytes.decode(enc); break
        except UnicodeDecodeError: pass
    if text is None:
        text = file_bytes.decode("cp1258", errors="replace")

    try:
        dialect = csv.Sniffer().sniff(text[:4096], delimiters=[",",";","\t","|"])
        delim = dialect.delimiter
    except Exception:
        delim = ","

    f = io.StringIO(text)
    rdr = csv.DictReader(f, delimiter=delim)
    req = ["id","question","options","answer","points","topic"]
    missing = [c for c in req if c not in (rdr.fieldnames or [])]
    if missing:
        raise ValueError(f"Thiếu cột: {missing}. Header: {rdr.fieldnames}")

    rows = []
    for i, r in enumerate(rdr, start=2):
        row = { c: (r.get(c) or "").strip() for c in req }
        if not row["id"] or not row["question"]:
            raise ValueError(f"Dòng {i}: thiếu id/question")
        row["difficulty"] = _norm_diff(r.get("difficulty",""))
        rows.append(row)
    return rows
