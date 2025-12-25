import pytest
from unittest.mock import patch, MagicMock
from src.connector import OpenCTIConnector

@patch("src.connector.OpenCTIConnector.__init__", return_value=None)
def test_disinformation_detection_logic(mock_init):
    """
    Vérifie que notre 'IA' détecte bien les mots-clés de désinformation.
    """
    connector = OpenCTIConnector()
    content_fake = "This is a massive fake news conspiracy about the government."
    content_clean = "Just a normal post about cats."
    tags_fake = connector._analyze_content(content_fake)
    tags_clean = connector._analyze_content(content_clean)

    assert "DISINFORMATION" in tags_fake
    assert "SIMULATION" in tags_fake
    assert "DISINFORMATION" not in tags_clean
    assert "SIMULATION" in tags_clean

@patch("src.connector.OpenCTIConnector.__init__", return_value=None)
def test_security_incident_detection(mock_init):
    """
    Vérifie la détection d'incidents de sécurité (hacked, leak...)
    """
    connector = OpenCTIConnector()
    
    content_hacked = "URGENT: My password was hacked and leaked online!"
    tags = connector._analyze_content(content_hacked)
    
    assert "SECURITY_INCIDENT" in tags
    assert "SIMULATION" in tags