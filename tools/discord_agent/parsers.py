import re
from datetime import datetime
from typing import Optional


def extract_amount(text: str) -> Optional[float]:
    """Extract a plausible amount from OCR'd text. Returns the largest numeric value found
    that looks like a money amount (prefers two-decimal forms). Returns None if none found.
    """
    if not text:
        return None
    nums = []
    # Patterns: thousand separators with dot decimal, plain dot-decimal, comma-decimal
    patterns = [r"[0-9]{1,3}(?:,[0-9]{3})+\.[0-9]{2}", r"[0-9]+(?:\.[0-9]{2})", r"[0-9]+(?:,[0-9]{2})"]
    for p in patterns:
        for m in re.findall(p, text):
            s = m
            if "," in s and "." in s:
                # e.g. 1,234.56 -> remove thousand separators
                s = s.replace(",", "")
            elif "," in s and "." not in s:
                # e.g. 12,34 -> treat comma as decimal
                s = s.replace(",", ".")
            try:
                nums.append(float(s))
            except Exception:
                continue
    if nums:
        return max(nums)
    # Fallback: find integers
    ints = re.findall(r"\b([0-9]+)\b", text)
    ints = [int(x) for x in ints] if ints else []
    if ints:
        return float(max(ints))
    return None


def extract_date(text: str) -> Optional[str]:
    """Try to extract a date and return it as ISO YYYY-MM-DD if possible.
    Supports YYYY-MM-DD, MM/DD/YYYY, DD/MM/YYYY, and 'Mar 5, 2026' forms.
    """
    if not text:
        return None
    patterns = [r"(\d{4}-\d{2}-\d{2})", r"(\d{1,2}/\d{1,2}/\d{2,4})", r"([A-Za-z]{3,9}\s+\d{1,2},\s*\d{4})"]
    for p in patterns:
        m = re.search(p, text)
        if m:
            ds = m.group(1)
            for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%b %d, %Y", "%B %d, %Y", "%m/%d/%y"):
                try:
                    dt = datetime.strptime(ds, fmt)
                    return dt.date().isoformat()
                except Exception:
                    continue
            # Try a simple numeric split for ambiguous mm/dd/yy
            parts = re.split(r"[ /-]", ds)
            try:
                if len(parts) >= 3:
                    m1, m2, m3 = parts[0], parts[1], parts[2]
                    if len(m3) == 2:
                        m3 = "20" + m3
                    dt = datetime(int(m3), int(m1), int(m2))
                    return dt.date().isoformat()
            except Exception:
                pass
    return None


def extract_merchant(text: str) -> Optional[str]:
    """Heuristic: return the first non-empty line that doesn't look like a date, amount, or known label.
    """
    if not text:
        return None
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    for ln in lines[:6]:
        # Skip lines that look like dates or amounts or labels
        if re.search(r"\d{1,2}[/-]\d{1,2}[/-]\d{2,4}", ln):
            continue
        if re.search(r"\$|USD|AMOUNT|TOTAL|SUBTOTAL|TAX|INVOICE", ln, flags=re.I):
            continue
        # If the line is short and alphabetic-ish, assume merchant
        if len(ln) >= 2:
            return ln
    return lines[0] if lines else None
