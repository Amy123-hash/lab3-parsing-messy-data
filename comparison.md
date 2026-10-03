# Lab 3 Comparison Write-Up: Regex vs. AI-Assisted Cleaning of `messy_samples.csv`

## Agreement / disagreement

The two agree on the large majority of the 60 records:
sample ID normalization, site normalization, and all dates this is including
the six ambiguous 2-digit-year dates (e.g. `11.24.53`) matched
exactly. I expected the AI pass to missread those short years as future
dates, but when actually asked to reason through each one, it checked for
a birthdate after today doesn't make sense and it had landed on the same
year as the regex script every time.The AI had gotten confused by 2-digit
years.

Where they genuinely disagree:

**1. Sex coding collapses two distinct situations into one.** 9 records
have a truly blank `sex` cell; 14 others spell it out as `unknown` or
`U`. The regex script preserves that distinction (blank stays blank;
explicit unknown becomes `U`). The AI-assisted prompt defined only
three output categories (M/F/Unknown), with no category for "not
recorded at all" so both blank and explicit unknown had collapsed into a
single `Unknown` value. This is a consequence of how I worded
the prompt, and not reasoning failure: an AI tool follows whats its
given, and not specified schema erases a real distinction in the
source data.

**2. The asterisk flag on S0039 and S0042 survives differently.** The
regex script captures `*` as a dedicated `flagged` boolean column. The
AI pass noticed the same `*` and the same likely meaning (a lab-flagged
reading) but, since no flag column was requested, put that observation
into free-text `notes` instead. The information isn't lost, but it's no
longer machine-readable the same way — you'd need to parse the notes
text to find flagged rows instead of filtering a boolean column.

## Which caught more edge cases?

Regex caught the asterisk and the sex-blank/unknown distinction because 
the script was explicitly written to check for them those checks don't happen by
accident. The AI pass caught the site-name variants and the ambiguous
year dates just as well with far less upfront effort, and did so
through genuine reasoning (plausibility-checking the result) rather
than a hard-coded rule. Therefore, it's not that one tool is smarter
it's that both approaches only catch what you or the AI actually
think to check for, and a schema or rule that's underspecified will
silently drop information no matter which method applies it.

## Time/effort comparison

Writing and debugging the four regex date patterns took 
longer than writing the one-paragraph AI prompt. Most of that time went
into inspecting every unique date format in the file by hand before
writing the pattern, not the regex syntax itself. The AI prompt
produced a usable table almost immediately, but matching its output
fields to the regex script's and deciding how to handle
the sex/blank distinction and the asterisk took a second proccess of
back-and-forth  once that's counted, total time was close
to even.

## Failure modes (specific records)

**1. The `mmol/L` unit-conversion problem (shared by both methods).**
Every row labeled `mmol/L` (e.g. S0006: `159.9 mmol/L`, S0011: `165.0
mmol/L`) has a numeric value in the same 70–250 range as the
`mg/dL`-labeled rows. Normal blood glucose in mmol/L is roughly 4–8;
converting these values literally (×18.0182) produces readings of
roughly 1,850–4,350 mg/dL across 14 rows, incompatible with life. Both
the regex script and the AI pass apply the conversion the label asks
for, because both were told to "convert mmol/L to mg/dL" without a
plausibility check built in. It only becomes obvious once you compare
the converted values against a clinically plausible range — which
suggests the `mmol/L` label itself is the actual error in the source
file, not the arithmetic. **Why it failed:** neither method validates
its output against domain knowledge by default; both just followed the
instruction given.

**2. Sex field ambiguity, specifically S0012 and S0007.** S0012 has a
genuinely blank sex cell; S0007 has sex explicitly written as
"unknown." The regex script treats these differently (blank vs. `U`);
the AI pass, given a prompt that only allowed three output values,
treats them identically as `Unknown`. Neither answer is simply "wrong"
— it depends on whether "not asked" and "asked, don't know" should
count as the same thing for downstream analysis — but it's a concrete
case where the AI pass's output quietly discarded a distinction present
in the source data, purely because of how its instructions were
phrased. **Why it failed:** an underspecified output schema (three
categories) can't represent a four-category reality, and the gap gets
resolved silently rather than flagged.

## Which would I trust for a real dataset, and why

Neither one blindly. Regex is reliable, but only because it was tuned
after manually inspecting every date format and category value in this
file its correctness comes from that inspection, not from regex
itself. The AI pass was faster to get a first version and reasoned its
way correctly through the century ambiguity, but it silently followed
whatever schema I gave it rather than asking whether that schema could
represent the data. For a real dataset I'd want both methods plus a
mandatory plausibility pass on the output (value ranges, future dates,
unit sanity checks) that's the step that actually caught the
`mmol/L` problem, and neither method does it on its own.
