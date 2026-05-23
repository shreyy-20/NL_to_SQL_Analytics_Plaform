import pytest
from unittest.mock import MagicMock
from ai.sql_generator.generator import SQLGenerator

@pytest.fixture
def generator():
    gen = SQLGenerator(model_type="template")
    gen.validator = MagicMock()
    gen.validator.validate.return_value = {
        "is_valid": True,
        "errors": [],
        "warnings": [],
        "query_type": "SELECT",
        "tables_accessed": []
    }
    return gen

def test_clean_sql_removes_markdown(generator):
    raw_sql = "```sql\nSELECT * FROM farmers;\n```"
    cleaned = generator._clean_sql(raw_sql)
    assert cleaned == "SELECT * FROM farmers;"

def test_clean_sql_adds_semicolon(generator):
    raw_sql = "SELECT * FROM farmers"
    cleaned = generator._clean_sql(raw_sql)
    assert cleaned == "SELECT * FROM farmers;"

def test_clean_sql_extracts_select(generator):
    raw_sql = "Here is your query: SELECT * FROM soil_health; Have a nice day!"
    cleaned = generator._clean_sql(raw_sql)
    assert cleaned == "SELECT * FROM soil_health;"

def test_generate_with_template_payment(generator):
    result = generator.generate("Where is my money?", "PAYMENT", {}, farmer_id=123)
    assert result["validated"] is True
    assert "123" in result["sql_query"]
    assert "query_type" in result

def test_generate_fallback_sql(generator):
    sql = generator._get_fallback_sql("PRICE", None)
    assert "SELECT crop, market" in sql