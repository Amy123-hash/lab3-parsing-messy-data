# AI_USAGE.md

## Task 2: AI-assisted extraction

**Tool used:** Claude (claude.ai), in a conversation where the raw
`messy_samples.csv` content was already visible to the assistant.

**Prompt used:**
> Here is a messy clinical CSV with columns sample_id, patient_name,
> dob, sex, enrollment_site, glucose_value, glucose_unit, notes.
> Extract it into a clean table with: sample_id (format SNNNN), dob
> (YYYY-MM-DD), sex (M/F/Unknown), enrollment_site (Site A/B/C), and
> glucose_value_mgdl (convert mmol/L to mg/dL).

No further instructions were given about 2-digit-year handling, how to
treat a blank sex field versus an explicitly-written "unknown," or the
`*` suffix on two glucose values — deliberately, to see what the tool
does with real judgment calls it wasn't told the answer to.

**Output:** `clean_samples_ai.csv` (60 rows), produced by the assistant
reasoning through each record directly rather than running a script.

**What actually happened, including a correction of an earlier guess:**
I initially assumed an AI tool would mis-handle the 2-digit-year dates
(e.g. reading `53` as `2053` instead of `1953`) the way a generic
date-parsing library does by default. When the assistant was actually
asked to do the extraction and reasoned through each date individually
instead of applying a library default, it checked the result for
plausibility (a birthdate in the future doesn't make sense) and got all
six of those dates right -- matching the regex script exactly. So that
specific "AI gets confused by short years" story doesn't hold up for a
careful live pass; it was really a property of a naive default parser,
not of AI-assisted extraction in general. The real divergences turned
out to be:

1. **Sex coding collapses blank and "unknown" together.** My prompt only
   defined three output categories (M/F/Unknown), with no fourth bucket
   for "not recorded at all." So both a genuinely blank cell and a cell
   that literally says "unknown"/"U" became `Unknown` in the AI output,
   while the regex script kept them distinct. This is a direct
   consequence of how the prompt was worded, not a parsing failure.
2. **The two asterisked glucose values (S0039, S0042) lost their flag
   as structured data.** The assistant noticed the `*` and treated it
   as a lab-flagged result, and said so in a sentence -- but since the
   prompt didn't ask for a flag column, that information ended up in
   free-text `notes`, not in a reusable column the way the regex
   script's `flagged` boolean is.
3. **Both approaches convert `mmol/L` literally, which is likely wrong.**
   See `comparison.md` -- this isn't a disagreement between the two
   methods, it's a shared failure mode worth separate discussion.

## General AI assistance this lab
Used an AI assistant to help design and debug the regex date patterns
against all four observed date formats before finalizing
`clean_samples_regex.py`, and to catch that the `mmol/L`-labeled
glucose values convert to physiologically implausible numbers (see
comparison.md) -- something neither script caught automatically, only
a manual plausibility check on the output did.
