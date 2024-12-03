"""
Unit tests for the ``barcode_generator.ean`` module.
"""

import pytest

from barcode_generator import encode_ean


@pytest.mark.parametrize(
    "code, expected",
    [
        ("5901234123457","10100010110100111011001100100110111101001110101010110011011011001000010101110010011101000100101"),
        ("55123457", "1010110001011000100110010010011010101000010101110010011101000100101"),
        ("5512345", "1010110001011000100110010010011010101000010101110010011101000100101"),
    ],
)
def test__ean_can_be_encoded(code: str, expected: str):
    """
    Test the ``main`` function.
    """
    assert str(encode_ean(code)) == expected
