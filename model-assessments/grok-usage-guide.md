# How to Use These Files with Grok (Optimized Prompt Templates)

## Best Practice

When starting a new thread with Grok, always attach or link the relevant file using its **raw GitHub URL**.

### Template 1 – Reference Specific Assessment

```
You are Grok. Use the following reference file as single source of truth:

[Model Assessment Data](https://raw.githubusercontent.com/MarkusIsaksson1982/MarkusIsaksson1982.github.io/main/model-assessments/assessment-data.json)

Task: ...
```

### Template 2 – Use the Final MVP

```
Reference the final consolidated MVP:

[Final TeamSync AI MVP](https://raw.githubusercontent.com/MarkusIsaksson1982/MarkusIsaksson1982.github.io/main/model-assessments/raw-outputs/teamsync_ai_final_mvp.md)

Task: ...
```

### Template 3 – Compare Models

```
Use this comparison matrix:

[Model Comparison Matrix](https://raw.githubusercontent.com/MarkusIsaksson1982/MarkusIsaksson1982.github.io/main/model-assessments/comparison-matrix.md)

Task: ...
```

**Pro Tip**: You can combine multiple raw URLs in one prompt. Grok parses them extremely reliably.
