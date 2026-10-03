"""
Lab 3 - Task 1: Regex-based cleaning of messy_samples.csv

Standardizes:
  - sample_id       -> SNNNN (4-digit, zero-padded, uppercase S)
  - dob             -> YYYY-MM-DD (ISO 8601)
  - sex             -> "M", "F", or "U" (explicit unknown markers only;
                       truly blank cells are left blank and counted as
                       missing, NOT silently folded into "U" -- see README)
  - enrollment_site -> "Site A", "Site B", or "Site C"
  - glucose_value   -> numeric, mg/dL, asterisk stripped
  - flagged         -> True if the original value had a trailing "*"
  - glucose_unit    -> always "mg/dL" after conversion
  - notes           -> whitespace-trimmed, unchanged otherwise

Usage:
    python clean_samples_regex.py messy_samples.csv clean_samples_regex.csv
"""
import re
import sys
import csv
from datetime import date

MONTHS = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}

# mmol/L -> mg/dL for glucose (standard clinical conversion factor)
MMOL_TO_MGDL = 18.0182

# Below this 2-digit year, assume 20XX; at/above, assume 19XX.
# Chosen by inspecting the actual 2-digit years in this file (12, 15, 51,
# 53, 58, 61, 65, 80, 95, 96, 98, 99) -- there's a clean gap between the
# "recent" ones and the "mid-century" ones, so 30 cleanly separates them.
PIVOT_YEAR = 30

DATE_PATTERNS = [
    # MM/DD/YYYY
    (re.compile(r"^(\d{1,2})/(\d{1,2})/(\d{4})$"),
     lambda m: (int(m.group(3)), int(m.group(1)), int(m.group(2)))),
    # YYYY-MM-DD (already ISO)
    (re.compile(r"^(\d{4})-(\d{1,2})-(\d{1,2})$"),
     lambda m: (int(m.group(1)), int(m.group(2)), int(m.group(3)))),
    # MM.DD.YY (2-digit year)
    (re.compile(r"^(\d{1,2})\.(\d{1,2})\.(\d{2})$"),
     lambda m: (
        2000 + int(m.group(3)) if int(m.group(3)) < PIVOT_YEAR else 1900 + int(m.group(3)),
        int(m.group(1)), int(m.group(2)),
     )),
    # DD-Mon-YYYY
    (re.compile(r"^(\d{1,2})-([A-Za-z]{3})-(\d{4})$"),
     lambda m: (int(m.group(3)), MONTHS[m.group(2).lower()], int(m.group(1)))),
]


def clean_dob(raw):
    raw = raw.strip()
    for pattern, extractor in DATE_PATTERNS:
        match = pattern.match(raw)
        if match:
            year, month, day = extractor(match)
            try:
                return date(year, month, day).isoformat()
            except ValueError:
                return f"UNPARSEABLE:{raw}"
    return f"UNPARSEABLE:{raw}"


def clean_sample_id(raw):
    digits = re.search(r"(\d+)", raw)
    return f"S{int(digits.group(1)):04d}" if digits else raw


def clean_sex(raw):
    raw = raw.strip()
    if raw == "":
        return ""  # true missingness -- preserved, not guessed
    if re.fullmatch(r"(?i)f(emale)?", raw):
        return "F"
    if re.fullmatch(r"(?i)m(ale)?", raw):
        return "M"
    if re.fullmatch(r"(?i)u(nknown)?", raw):
        return "U"
    return f"UNRECOGNIZED:{raw}"


def clean_site(raw):
    match = re.search(r"(?i)site[\s_-]*([abc])\b", raw)
    return f"Site {match.group(1).upper()}" if match else f"UNRECOGNIZED:{raw}"


def clean_glucose(value_raw, unit_raw):
    flagged = value_raw.strip().endswith("*")
    num_match = re.search(r"[\d.]+", value_raw)
    value = float(num_match.group(0)) if num_match else None

    unit_norm = re.sub(r"\s+", "", unit_raw).lower()
    if unit_norm == "mmol/l" and value is not None:
        value = round(value * MMOL_TO_MGDL, 1)
    elif unit_norm == "mg/dl":
        value = round(value, 1) if value is not None else None
    else:
        return value, unit_raw, flagged  # unrecognized unit, leave as-is

    return value, "mg/dL", flagged


def main(in_path, out_path):
    with open(in_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows_out = []
        for row in reader:
            value, unit, flagged = clean_glucose(row["glucose_value"], row["glucose_unit"])
            rows_out.append({
                "sample_id": clean_sample_id(row["sample_id"]),
                "patient_name": row["patient_name"].strip(),
                "dob": clean_dob(row["dob"]),
                "sex": clean_sex(row["sex"]),
                "enrollment_site": clean_site(row["enrollment_site"]),
                "glucose_value_mgdl": value,
                "flagged": flagged,
                "notes": row["notes"].strip(),
            })

    fieldnames = ["sample_id", "patient_name", "dob", "sex", "enrollment_site",
                  "glucose_value_mgdl", "flagged", "notes"]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows_out)

    print(f"Wrote {len(rows_out)} cleaned rows to {out_path}")


if __name__ == "__main__":
    in_path = sys.argv[1] if len(sys.argv) > 1 else "messy_samples.csv"
    out_path = sys.argv[2] if len(sys.argv) > 2 else "clean_samples_regex.csv"
    main(in_path, out_path)
