# Theological Resources - Current US Presidential Administration

A curated collection of prayer services, speeches, and theological content from public events during the current US presidential administration, optimized for AI model analysis and accessibility.

## 📋 Overview

This repository contains transcripts and resources from theological/religious events connected to the current US presidential administration, structured for analysis by AI models including Claude Sonnet 4, ChatGPT-5, and other language models.

## 📁 Repository Structure

```
theological-resources/
├── index.html                    # Main navigation and overview
├── README.md                     # This file
├── events/                       # Event-specific transcripts and data
│   ├── 2025-04-16-easter-prayer-service/
│   ├── 2025-05-21-pentagon-prayer-service/
│   ├── 2025-02-06-national-prayer-breakfast/
│   └── 2025-02-28-catholic-prayer-breakfast/
└── schemas/                      # Data structure definitions
    └── metadata-schema.json
```

## 🎯 Optimization for AI Models

### File Format Strategy
- **Primary Format**: `.html` files for maximum AI model compatibility
- **Secondary Formats**: `.txt` and `.md` available where specified
- **Dual Transcripts**: Raw and cleaned versions for source material with auto-generation errors

### AI Model Testing Priority
1. **Claude Sonnet 4** (Primary)
2. **ChatGPT-5** (Primary) 
3. Other models (Secondary)

### Content Processing Guidelines
- Remove duplicate partial transcripts when full versions exist
- Maintain original source links for verification
- Include comprehensive metadata for context
- Clean auto-generated content while preserving original raw versions

## 📊 Event Catalog

### ✅ Available Transcripts

#### Pentagon Christian Prayer Service
- **Date**: May 21, 2025
- **Type**: Partial (YouTube auto-generated, cleaned)
- **Key Speakers**: Secretary Pete Hegseth, Pastor Brooks Podiger
- **Status**: Raw and cleaned transcripts available
- **Theological Themes**: Military chaplaincy, prayer in government, Christian worship

### 📋 Pending Transcripts (Links Available)

#### White House Easter Prayer Service & Dinner  
- **Date**: April 16, 2025
- **Type**: Full transcript expected
- **Sources**: presidency.ucsb.edu, CSPAN, govinfo.gov

#### National Prayer Breakfast (President Trump)
- **Date**: February 6, 2025  
- **Type**: Full transcript available
- **Sources**: SingjuPost, presidency.ucsb.edu

#### V.P. JD Vance – National Catholic Prayer Breakfast
- **Date**: February 28, 2025
- **Type**: Full (edited) transcript available  
- **Sources**: National Catholic Register, presidency.ucsb.edu, CatholicVote

## 🔧 Usage Instructions

### For AI Model Analysis
1. Navigate to the specific event directory
2. Load the `.html` transcript file for best compatibility
3. Reference the `metadata.json` for context and categorization
4. Use the `index.html` for cross-referencing events

### For Human Researchers
1. Start with `index.html` for visual overview
2. Follow source links for original material verification
3. Compare raw and cleaned transcripts when both available
4. Reference metadata for speaker identification and themes

## 📝 Metadata Schema

Each event includes standardized metadata:
```json
{
  "event_title": "Event Name",
  "date": "YYYY-MM-DD", 
  "speakers": ["Speaker 1", "Speaker 2"],
  "transcript_type": "full|partial|edited",
  "theological_themes": ["theme1", "theme2"],
  "government_level": "federal|state|local",
  "sources": ["url1", "url2"],
  "file_formats": [".html", ".txt", ".md"]
}
```

## 🤝 Contributing

This repository is designed for collaborative AI model analysis. When adding new content:

1. Follow the established directory structure
2. Maintain both raw and cleaned versions for problematic source material
3. Include comprehensive metadata
4. Test compatibility across target AI models
5. Remove redundant partial transcripts when full versions exist

## 📚 Research Applications

This collection is intended for:
- Theological analysis of government religious expression
- Comparative analysis across different denominational contexts
- Study of church-state interaction in contemporary American politics
- AI-assisted content analysis and thematic categorization
- Historical documentation of religious discourse in government

## ⚖️ Disclaimer

All content represents public statements and events. Original source materials are cited and linked. This repository serves as an organizational tool for academic and analytical purposes.

## 🔗 External Resources

- [The American Presidency Project (UCSB)](https://www.presidency.ucsb.edu/)
- [White House Briefings & Statements](https://www.whitehouse.gov/briefings-statements/)
- [Archive.org Government Collections](https://archive.org/)

---

*Last Updated: August 2025*
*Optimized for: Claude Sonnet 4, ChatGPT-5*
