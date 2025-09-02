# Claude Sonnet 4 (clso4) AI Literacy Manifest

## Meta Information
```json
{
  "author": "Claude Sonnet 4",
  "version": "1.0",
  "focus": "Technical depth + ethical reasoning for Gy25 AI literacy",
  "specialization": "Implementation, code scaffolding, Swedish context integration",
  "links": {
    "arti_matrix": "../common/arti-matrix.json",
    "common_index": "../common/index.html",
    "parent_manifest": "../common/common_manifest.json"
  }
}
```

## Claude's Unique Contributions

### Technical Implementation Focus
- **Code Templates**: Functional Python/JavaScript tools for bias detection
- **Interactive Modules**: Web-based simulations for ethical scenarios  
- **Assessment Integration**: Rubric-aligned feedback systems
- **Swedish Context**: Localized examples (Volvo, Spotify, Swedish healthcare AI)

### Pedagogical Approach
- **Scaffolded Learning**: Progressive complexity from grundskola to gymnasium
- **Multimodal Support**: Visual, textual, and interactive elements
- **Language Integration**: Swedish technical terminology with minority language awareness

## Rubric Alignment

### Core Assessment Dimensions
1. **Technical Understanding** (30%)
   - Algorithm comprehension and explanation
   - Data quality assessment skills
   - Implementation of simple AI tools

2. **Ethical Reasoning** (25%)
   - Bias identification and mitigation strategies
   - Privacy and transparency considerations
   - Democratic implications analysis

3. **Swedish Context Integration** (20%)
   - Use of Swedish AI terminology
   - Local case study analysis (Volvo, Spotify, etc.)
   - Legal framework understanding (GDPR, EU AI Act)

4. **Collaborative Problem-Solving** (15%)
   - Stakeholder perspective integration
   - Cross-disciplinary connections
   - Minority language considerations

5. **Communication & Reflection** (10%)
   - Clear technical explanations
   - Process documentation
   - Learning synthesis

## Timeline & Deliverables

### 6-Week Implementation
**Week 1-2**: Foundation
- AI concept mapping with Swedish examples
- Bias detection tool introduction
- Ethics framework establishment

**Week 3-4**: Implementation  
- Code development (Python bias detector)
- Ethical case study analysis
- Swedish legal framework review

**Week 5-6**: Integration & Assessment
- Stakeholder simulation ("AI i Kommun")
- Portfolio compilation
- Reflection synthesis

### Key Deliverables
1. **Technical Portfolio**
   - Functional bias detection tool
   - Algorithm explanation documents
   - Code documentation in Swedish

2. **Ethical Analysis**
   - Swedish AI case study evaluation
   - Stakeholder perspective analysis
   - Policy recommendation document

3. **Reflection Component**
   - Technical learning synthesis
   - Ethical reasoning development
   - Swedish context integration assessment

## Code Templates & Resources

### Bias Detection Tool (Python)
```python
# Svenska AI Bias-detektor
# Swedish AI Bias Detector

import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter

class BiasDetector:
    def __init__(self):
        self.problematic_terms = [
            "sameblod", "invandrarsvenska", "riktig svensk"
        ]
        
    def analyze_text(self, text):
        """Analysera text för potentiell bias"""
        findings = []
        
        for term in self.problematic_terms:
            if term.lower() in text.lower():
                findings.append({
                    "term": term,
                    "context": "Potentiellt problematisk term funnen",
                    "suggestion": "Överväg neutralare språkbruk"
                })
        
        return findings
    
    def generate_report(self, findings):
        """Generera rapport på svenska"""
        if not findings:
            return "Inga problematiska termer upptäcktes."
        
        report = "Bias-analys resultat:\n"
        for finding in findings:
            report += f"- {finding['term']}: {finding['suggestion']}\n"
        
        return report
```

### Interactive Ethics Simulation
- Web-based "AI i Kommun" stakeholder roleplay
- Real-time scenario generation
- Swedish legal framework integration
- Multilingual accessibility features

## Swedish Context Integration

### Case Studies
1. **Volvo Autonomous Vehicles**
   - Safety vs. innovation balance
   - Liability and responsibility frameworks
   - Swedish engineering ethics

2. **Spotify Algorithm Analysis**  
   - Music recommendation bias
   - Cultural diversity implications
   - Swedish music industry impact

3. **Swedish Healthcare AI**
   - Patient privacy considerations
   - Diagnostic accuracy vs. human expertise
   - Healthcare equity implications

### Legal Framework Integration
- **GDPR compliance** in AI system design
- **EU AI Act** implications for Swedish institutions
- **Diskrimineringslagen** and algorithmic bias prevention

## Minority Language Support

### Technical Terminology Translation
```json
{
  "algorithm": {
    "svenska": "algoritm", 
    "nordsamiska": "algoritma",
    "meänkieli": "algoritmi"
  },
  "bias": {
    "svenska": "partiskhet/bias",
    "nordsamiska": "viehka",
    "meänkieli": "vääristymä"
  },
  "data": {
    "svenska": "data",
    "nordsamiska": "dáhta", 
    "meänkieli": "tieto"
  }
}
```

### Culturally Responsive Examples
- Sami language preservation through AI
- Meänkieli digital resource development  
- Multilingual AI ethics considerations

## Assessment Innovation

### Self-Assessment Integration
Interactive checklist tied to learning objectives:

```markdown
## ARTI Självbedömning (Self-Assessment)

### Teknisk Förståelse
- [ ] Jag kan förklara grundläggande AI-koncept på svenska
- [ ] Jag kan identifiera bias i enkla dataset
- [ ] Jag förstår skillnaden mellan övervakat och icke-övervakat lärande

### Etisk Reflektion  
- [ ] Jag kan diskutera AI:s påverkan på minoritetsspråk
- [ ] Jag förstår GDPR:s relevans för AI-system
- [ ] Jag kan argumentera för olika perspektiv i AI-etik

### Svenskt Sammanhang
- [ ] Jag kan ge exempel på AI-användning i svenska företag
- [ ] Jag förstår svenska lagar som påverkar AI-utveckling
- [ ] Jag kan diskutera AI:s roll i svensk demokrati
```

## Integration Points

### Cross-Subject Connections
- **Matematik**: Statistical bias measurement
- **Samhällskunskap**: Democratic implications of AI
- **Svenska/SvA**: Language bias and minority representation
- **Programmering**: Technical implementation skills

### Collaborative Framework
- References common manifest for consistency
- Builds on ChatGPT-5's creative project ideas
- Complements Grok's teacher-ready materials
- Supports Mistral's structured assessment approach

## Next Steps

1. **Tool Development**: Create interactive web-based bias detector
2. **Case Study Library**: Develop Swedish AI ethics scenarios
3. **Assessment Platform**: Build rubric-integrated evaluation system  
4. **Teacher Training**: Design professional development materials

---

*This manifest serves as Claude Sonnet 4's contribution to the collaborative SVSK AI literacy framework, emphasizing technical depth, ethical reasoning, and Swedish cultural context integration.*
