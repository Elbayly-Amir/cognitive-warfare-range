import pytest
from src.indicator_manager import IndicatorManager

def test_extract_domain_simple():
    """Vérifie qu'on extrait bien un domaine d'une URL"""
    manager = IndicatorManager()
    content = "Please click on http://malicious-site.com/login to verify account."
    
    indicators = manager.extract_indicators(content)
    
    assert len(indicators) == 1
    assert indicators[0]["type"] == "domain-name"
    assert indicators[0]["value"] == "malicious-site.com"

def test_extract_multiple_domains():
    """Vérifie qu'on gère plusieurs domaines sans doublons"""
    manager = IndicatorManager()
    content = "Check http://site1.com and https://site2.org now!"
    
    indicators = manager.extract_indicators(content)
    values = [i["value"] for i in indicators]
    
    assert len(indicators) == 2
    assert "site1.com" in values
    assert "site2.org" in values

def test_no_indicator():
    manager = IndicatorManager()
    content = "Hello world, nothing to see here."
    assert len(manager.extract_indicators(content)) == 0