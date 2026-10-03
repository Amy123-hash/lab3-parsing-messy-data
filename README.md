# Lab 3 — Parsing Messy Health Data

## Files
- `clean_samples_regex.py` — regex-based cleaning script (Task 1)
- `clean_samples_regex.csv` — its output
- `clean_samples_ai.csv` — AI-assisted extraction output (Task 2),
  produced directly by an AI assistant reasoning through the raw data
  per the prompt documented in `AI_USAGE.md` (no script -- this was a
  live extraction, not an automated pass)
- `comparison.md` — agreement/disagreement, edge cases, failure modes
  (Tasks 3–4)
- `AI_USAGE.md` — documented prompts

## Usage
Input: messy_samples.csv

```bash
python clean_samples_regex.py messy_samples.csv clean_samples_regex.csv
```

Takes the raw CSV path as the first argument and the output path as the
second; defaults to `messy_samples.csv` / `clean_samples_regex.csv` in
the current directory if no arguments are given.

`clean_samples_ai.csv` was produced by giving an AI assistant the raw
CSV plus the prompt in `AI_USAGE.md` directly -- there's no script to
run for this one, since Task 2 asks for AI-assisted extraction, not an
automated stand-in for it.

## Standardization rules applied
- `sample_id` → `SNNNN` (4-digit zero-padded, uppercase `S`)
- `dob` → ISO `YYYY-MM-DD`
- `sex` → `M` / `F` / `U` in the regex output (truly blank cells are
  kept blank rather than guessed); `M` / `F` / `Unknown` in the AI
  output, which collapses blank and explicit "unknown" together -- see
  comparison.md for why this differs
- `enrollment_site` → `Site A` / `Site B` / `Site C`
- `glucose_value_mgdl` → numeric, standardized to mg/dL (see
  comparison.md for a known issue with the `mmol/L`-labeled rows --
  both outputs likely need a second look here before calling this
  "clean")
- `flagged` (regex script only) → `True` if the original value had a
  trailing `*`; the AI output instead notes this in free-text `notes`
  for the two affected rows (S0039, S0042)
