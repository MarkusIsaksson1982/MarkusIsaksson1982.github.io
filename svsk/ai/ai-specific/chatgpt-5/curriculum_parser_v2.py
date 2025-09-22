import json
import csv
from typing import Dict, Any, Optional
from jsonschema import validate, ValidationError

GY25_SCHEMA = {
    "type": "object",
    "properties": {
        "programs": {"type": "object"},
        "subjects": {"type": "array", "items": {"type": "string"}}
    },
    "required": ["programs", "subjects"]
}

MANIFEST_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "type": {"type": "string"},
        "children": {"type": "array"}
    },
    "required": ["name", "type"]
}

class CurriculumParserV2:
    """
    Extended parser supporting manifest.json and gy25_manifest.json.
    Adds schema validation and export helpers.
    """

    def _detect_format(self, data: Dict[Any, Any]) -> str:
        if "programs" in data and "subjects" in data:
            return "gy25_curriculum"
        elif "name" in data and "children" in data:
            return "manifest"
        else:
            raise ValueError("Unknown curriculum format")

    def _get_schema(self, format_type: str) -> Optional[Dict]:
        if format_type == "gy25_curriculum":
            return GY25_SCHEMA
        elif format_type == "manifest":
            return MANIFEST_SCHEMA
        return None

    def validate_schema(self, data: Dict[Any, Any], schema: Dict[Any, Any]) -> bool:
        try:
            validate(instance=data, schema=schema)
            return True
        except ValidationError as e:
            print(f"❌ Schema validation failed: {e.message}")
            return False

    def parse_file(self, file_path: str, validate: bool = True) -> Dict:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        format_type = self._detect_format(data)
        schema = self._get_schema(format_type)

        if validate and schema:
            self.validate_schema(data, schema)

        return {"format": format_type, "data": data}

    def export_to_markdown(self, data: Dict, file_path: str) -> None:
        """Export curriculum data to Markdown for easy review."""
        format_type = data["format"]
        payload = data["data"]

        lines = [f"# Curriculum Data ({format_type})", ""]

        if format_type == "gy25_curriculum":
            lines.append("## Programs")
            for category, items in payload["programs"].items():
                lines.append(f"### {category.capitalize()}")
                for program in items:
                    if isinstance(program, dict):
                        lines.append(f"- **{program['name']}**")
                        if "inriktningar" in program:
                            for track in program["inriktningar"]:
                                lines.append(f"  - {track}")
                    else:
                        lines.append(f"- {program}")

            lines.append("\n## Subjects")
            for subj in payload["subjects"]:
                lines.append(f"- {subj}")

        elif format_type == "manifest":
            lines.append("## Repository Structure")

            def walk(node, depth=0):
                prefix = "  " * depth + "- "
                lines.append(f"{prefix}{node['name']} ({node['type']})")
                for child in node.get("children", []):
                    walk(child, depth + 1)

            walk(payload)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    def export_subjects_to_csv(self, data: Dict, file_path: str) -> None:
        """Export subject list (gy25 only) to CSV."""
        if data["format"] != "gy25_curriculum":
            raise ValueError("CSV export only available for gy25 curriculum")

        subjects = data["data"]["subjects"]
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Subject"])
            for subj in subjects:
                writer.writerow([subj])
