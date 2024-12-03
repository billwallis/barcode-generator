"""
Unit tests for the ``barcode_generator.ean`` module.
"""

import pytest

from barcode_generator import encode_ean
from barcode_generator.ean import _calculate_checksum


@pytest.mark.parametrize(
    "code, checksum",
    [
        ("123", "6"),
        ("654321", "1"),
        ("1425534", "2"),
        ("1234567", "0"),
        ("4456456457", "8"),
        ("9876543210", "5"),
        ("0", "0"),
        ("00000000", "0"),
        ("123456789012", "8"),
    ],
)
def test__calculate_checksum(code: str, checksum: str):
    """
    Checksums can be calculated.
    """
    assert _calculate_checksum(code) == checksum


# def test__encoded_ean_is_a_bit_array():
#     """
#     Test the ``main`` function.
#     """
#     code = "1234567"
#     expected = []
#     assert encode_ean(code) == expected


@pytest.mark.parametrize(
    "code, expected",
    [
        (
            "5901234123457",
            "10100010110100111011001100100110111101001110101010110011011011001000010101110010011101000100101",
        ),
        (
            "55123457",
            "1010110001011000100110010010011010101000010101110010011101000100101",
        ),
        (
            "5512345",
            "1010110001011000100110010010011010101000010101110010011101000100101",
        ),
    ],
)
def test__ean_can_be_encoded(code: str, expected: str):
    """
    EANs can be encoded.
    """
    assert str(encode_ean(code)) == expected
