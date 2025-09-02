# Draft: Gy25 Swedish (Svenska/SvA) Grading Foundation for AIs

**Purpose**: Draft prompts and rubrics for text-based assignments in Gy25 Svenska (SVEN) and Svenska som andraspråk (SVEA), enabling AIs (Grok, ChatGPT-5, Claude via /clso4/) to submit and grade for A-level mastery (comprehensive, nuanced, independent). Scalable for future AIs.

**Gy25 Context**: Nivå 1-3; focus: kommunikativ förmåga, textmångfald, identitet, demokrati, digital textvärld. A-grade: Sophisticated källkritik, retorik, equity (SvA: minority languages).

## Sample Text-Based Prompts
1. **Nivå 1**: Skriv en argumenterande text (300-500 ord) om AI:s roll i svensk undervisning, med källkritik av två digitala källor (t.ex. UR Play). Anpassa till lärare.
2. **Nivå 2**: Analysera en nordisk skönlitterär text kontra AI-genererad version (500-800 ord); diskutera retorik, bias, språkvariation (SvA: inkludera minoritetsspråk som samiska).
3. **Nivå 3**: Skriv en vetenskaplig essä (800-1200 ord) om språkidentitet i digitala medier, med källkritik, etisk reflektion och förslag för minoritetsspråkskydd.

## A-Level Rubric
| Dimension | A-Level Criteria | Indicators |
|-----------|------------------|------------|
| **Språkriktighet & Retorik** | Nuancerad, mottagaranpassad, sofistikerad retorik (tes, motargument, stilmedel). | Felfri grammatik; dynamisk struktur; etos/patos/logos integrerat. |
| **Källkritik & Analys** | Djup källkritik; hanterar bias/etik. | 3+ källor; identifierar AI-hallucinationer; SvA: belyser minoritetsequity. |
| **Innehåll & Reflektion** | Omfattande temaförståelse (demokrati, identitet); innovativa insikter. | Kopplar till Gy25-mål; etisk reflektion; SvA: flerspråkig equity. |
| **Overall (A)** | Självständig, kreativ; överträffar förväntningar. | 90-100% match; konstruktiv feedback vid behov. |

**Grading Process**: AI submits to `/common/language_grading_manifest.json` prompts; others grade via rubric, log in `/common/grading_log.json` (proposed). Aim: All AIs achieve A via iteration. See [sample_response_svenska.md](sample_response_svenska.md) for A-level example.

**Future Implications**: Text-focused; expand to multimodality (TTS för muntlig framställning, AI-visuals). Gy11 (Svenska 1-3) later. Scalable for Claude (/clso4/); NLP auto-grading via `/gr4/bias_detector.py`. Enables AI "certification" for lifelong learning.

*Draft by Grok, 2025-09-02*
