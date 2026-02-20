# Model Assessment Comparison Matrix (TeamSync AI MVP - February 2026)

**Last updated:** 20 February 2026  
**Repo raw URL:** https://raw.githubusercontent.com/MarkusIsaksson1982/MarkusIsaksson1982.github.io/main/model-assessments/comparison-matrix.md

This matrix is optimized for Grok parsing. Use the raw GitHub URLs below when referencing in new threads.

## Comparison Table

| Model                        | Interface          | Max Practical Files | Project Scale Handling                  | Best For                              | Harper Strength Note                  | Overall Strength (1-5) | Recommended Grok Pairing |
|-----------------------------|--------------------|---------------------|-----------------------------------------|---------------------------------------|---------------------------------------|------------------------|--------------------------|
| **Kimi K2.5 Thinking**      | Web-based          | ~10 files           | Good for structured docs, limited nested | Deep security, RBAC, audit, architecture | —                                     | 5.0                    | Lucas (Production)       |
| **Claude Sonnet 4.6 Extended** | Web-based       | ~10 files           | Good for detailed reasoning             | Complex thinking, clean structure     | —                                     | 4.7                    | Benjamin (Deep Planning) |
| **Qwen3.5-Plus**            | Web-based          | ~10 files           | Balanced one-shot documents             | Clean code, balanced output           | —                                     | 4.3                    | Lucas (Quick Iterations) |
| **MiniMax M2.5**            | CLI (OpenCode)     | 20+ files, nested   | Excellent for full projects & editing   | Architecture, efficient code          | —                                     | 4.8                    | Benjamin (Planning)      |
| **OpenAI Codex**            | CLI (OpenCode)     | 15+ files, nested   | Strong for frontend & component work    | Polished UI, full implementations     | —                                     | 4.6                    | Harper (Creative UX)     |
| **Trinity Large Preview**   | CLI (OpenCode)     | 15+ files, nested   | Excellent for creative & visual work    | Storytelling, emotional UX, concepts  | **Best for immersive storytelling, role-play, emotional UX, visual concepts** | 4.9 | Harper (Creative)        |
| **Gemini Code Assist**      | Web-based          | ~10 files           | Structured engineering patterns         | Reliable backend adapters             | —                                     | 4.4                    | Lucas (Engineering)      |

### Key Insights for Grok Users

- **Web-based models** (Qwen, Kimi, Gemini, Claude): Best for one-shot creations, iterations, and structured documents. Can attach up to ~10 files. Limited on large nested projects or direct file editing.
- **CLI-based models** (MiniMax, Codex, Trinity via OpenCode): Superior for parsing full project structures, nested folders, and direct editing. Can handle 15–20+ files and generate consolidated Markdown with embedded code files.

**Trinity Large Preview** stands out for **Harper-style creative work** (immersive storytelling, emotional UX, visual concepts) and is recommended when pairing with Grok for design/UX tasks.

---

## How to Reference These Files with Grok

Copy-paste the raw GitHub URL directly into your prompt:

```markdown
Use this comparison matrix as reference:

https://raw.githubusercontent.com/MarkusIsaksson1982/MarkusIsaksson1982.github.io/main/model-assessments/comparison-matrix.md

Task: ...
```

**Recommended single-source files**:
- **Final consolidated MVP**: https://raw.githubusercontent.com/MarkusIsaksson1982/MarkusIsaksson1982.github.io/main/model-assessments/raw-outputs/teamsync_ai_final_mvp.md
- **Structured data**: https://raw.githubusercontent.com/MarkusIsaksson1982/MarkusIsaksson1982.github.io/main/model-assessments/assessment-data.json
- **Portfolio data**: https://raw.githubusercontent.com/MarkusIsaksson1982/MarkusIsaksson1982.github.io/main/data/portfolio.json

This setup ensures Grok can parse everything accurately in future threads.
```
