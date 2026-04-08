from tools.calculator import calculator

def test_calculator_basic_operations():
    assert calculator("2 + 2") == "4"
    assert calculator("5 * 10") == "50"
    assert calculator("10 / 2") == "5"
    assert calculator("10 - 5") == "5"

def test_calculator_advanced_operations():
    assert calculator("sqrt(16)") == "4"
    assert calculator("2**3") == "8"
    assert calculator("abs(-5)") == "5"

def test_calculator_division_by_zero():
    assert "Error: division by zero" in calculator("10 / 0")

def test_calculator_invalid_input():
    assert "Error" in calculator("import os")
    assert "Error" in calculator("2 + ")
