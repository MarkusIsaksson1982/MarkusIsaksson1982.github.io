import pytest
import json
from curriculum_parser import CurriculumParser

def test_manifest_parsing():
    parser = CurriculumParser()
    data = parser.parse_file("manifest.json", validate=False)
    assert data["format"] == "manifest"
    assert "name" in data["data"]

def test_gy25_manifest_parsing():
    parser = CurriculumParser()
    data = parser.parse_file("gy25_manifest.json", validate=False)
    assert data["format"] == "gy25_curriculum"
    assert "programs" in data["data"]

def test_invalid_file(tmp_path):
    d = tmp_path / "sub"
    d.mkdir()
    p = d / "bad.json"
    p.write_text("{bad json")
    parser = CurriculumParser()
    with pytest.raises(Exception):
        parser.parse_file(str(p), validate=False)
