import json
import pytest
import os
from src.label_manager import LabelManager

@pytest.fixture
def sample_config_file(tmp_path):
    """Crée un fichier JSON temporaire valide pour le test"""
    config_data = [
        {
            "name": "TEST_URGENT", 
            "color": "#ff0000", 
            "keywords": ["urgent", "now"]
        }
    ]
    p = tmp_path / "labels_config.json"
    p.write_text(json.dumps(config_data), encoding="utf-8")
    return str(p)

def test_load_configuration(sample_config_file):
    manager = LabelManager(config_path=sample_config_file)
    assert len(manager.rules) == 1
    assert manager.rules[0]["name"] == "TEST_URGENT"

def test_detection_logic(sample_config_file):
    manager = LabelManager(config_path=sample_config_file)
    
    content = "This is extremely URGENT message"
    labels = manager.analyze_content(content)
    assert "TEST_URGENT" in labels
    assert "SIMULATION" in labels
    
    content_clean = "Just a calm message"
    labels_clean = manager.analyze_content(content_clean)
    assert "TEST_URGENT" not in labels_clean
    assert "SIMULATION" in labels_clean