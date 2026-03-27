import pytest
import importlib.util
import os

# Load parsers module directly from file to avoid package import issues during tests
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
MOD_PATH = os.path.join(ROOT, 'tools', 'discord_agent', 'parsers.py')
spec = importlib.util.spec_from_file_location('parsers', MOD_PATH)
parsers = importlib.util.module_from_spec(spec)
spec.loader.exec_module(parsers)


def test_extract_amount_dollar():
    assert parsers.extract_amount("$12.34") == pytest.approx(12.34)


def test_extract_amount_multiple():
    assert parsers.extract_amount("Subtotal 5.00\nTotal 12.34") == pytest.approx(12.34)


def test_extract_amount_comma_decimal():
    assert parsers.extract_amount("Total 12,34") == pytest.approx(12.34)


def test_extract_amount_thousand_sep():
    assert parsers.extract_amount("Amount: 1,234.56") == pytest.approx(1234.56)


def test_extract_date_iso():
    assert parsers.extract_date("Date: 2026-03-27") == "2026-03-27"


def test_extract_date_slash():
    assert parsers.extract_date("03/27/2026") == "2026-03-27"


def test_extract_merchant_simple():
    text = "STARBUCKS\n123 Main St\nTotal $5.00\n"
    assert parsers.extract_merchant(text) == "STARBUCKS"


def test_extract_merchant_fallback():
    text = "\nTotal 5.00"
    assert parsers.extract_merchant(text) == "Total 5.00"
