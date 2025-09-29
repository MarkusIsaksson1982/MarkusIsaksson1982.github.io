# Grading Script Examples: Nivå 3 Responses for Gy25 Svenska/SvA and Engelska

**Purpose**: This document provides examples of outputs from `grading_script.py` when applied to Nivå 3 sample responses (`sample_response_svenska_niva3.md` and `sample_response_engelska_niva3.md`) for Gy25 Svenska/SvA and Engelska. The examples demonstrate automated scoring for A-level mastery, aligning with Gy25 criteria (advanced källkritik, etisk reflektion, cross-cultural/minority language focus). Results can be logged in `/common/grading_log.json` for cross-AI grading by Grok, ChatGPT-5, Claude (/clso4/), and future models.

**Gy25 Context**: Nivå 3 emphasizes sophisticated analysis, ethical reflection, and innovative solutions in digital textvärld. A-level requires nuanced language, deep source critique, and comprehensive thematic understanding, per `/gr4/swedish_grading_draft.md` and `/gr4/english_grading_draft.md`.

## Example 1: Svenska Nivå 3 Response

**Response File**: `sample_response_svenska_niva3.md`  
**Prompt**: Skriv en vetenskaplig essä (800-1200 ord) om språkidentitet i digitala medier, med källkritik, etisk reflektion och förslag för minoritetsspråkskydd.  
**Input Text**: [Full text of `sample_response_svenska_niva3.md`, 820 words, with citations, bias critique, and Sami focus.]

**Script Output**:
```json
{
  "scores": {
    "Språkriktighet & Retorik": 25,
    "Källkritik & Analys": 25,
    "Innehåll & Reflektion": 25,
    "Overall (A)": 25
  },
  "total": 100,
  "grade": "A",
  "notes": "Enhanced with stopword filtering, bias density, and Gy25 term depth. Log in ../common/grading_log.json."
}
