"""
EAN-8 and EAN-13 barcode generator.
"""

from __future__ import annotations

import dataclasses


@dataclasses.dataclass
class BitArray(list):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __str__(self) -> str:
        string = ""
        for i in self:
            string += str(int(i)) if isinstance(i, bool) else str(i)

        return string

    @classmethod
    def from_ints(cls, *ints: int) -> BitArray:
        return cls(bool(i) for i in ints)


@dataclasses.dataclass
class EncodedNumber:
    left_odd: BitArray
    left_even: BitArray
    right: BitArray
    checksum: BitArray


EAN8_MIDPOINT = 4
EAN13_MIDPOINT = 7

EDGE = BitArray.from_ints(1, 0, 1)
MIDDLE = BitArray.from_ints(0, 1, 0, 1, 0)
ENCODER_TABLE: dict[str, EncodedNumber] = {
    "0": EncodedNumber(
        BitArray.from_ints(0, 0, 0, 1, 1, 0, 1),
        BitArray.from_ints(0, 1, 0, 0, 1, 1, 1),
        BitArray.from_ints(1, 1, 1, 0, 0, 1, 0),
        BitArray.from_ints(0, 0, 0, 0, 0, 0),
    ),
    "1": EncodedNumber(
        BitArray.from_ints(0, 0, 1, 1, 0, 0, 1),
        BitArray.from_ints(0, 1, 1, 0, 0, 1, 1),
        BitArray.from_ints(1, 1, 0, 0, 1, 1, 0),
        BitArray.from_ints(0, 0, 1, 0, 1, 1),
    ),
    "2": EncodedNumber(
        BitArray.from_ints(0, 0, 1, 0, 0, 1, 1),
        BitArray.from_ints(0, 0, 1, 1, 0, 1, 1),
        BitArray.from_ints(1, 1, 0, 1, 1, 0, 0),
        BitArray.from_ints(0, 0, 1, 1, 0, 1),
    ),
    "3": EncodedNumber(
        BitArray.from_ints(0, 1, 1, 1, 1, 0, 1),
        BitArray.from_ints(0, 1, 0, 0, 0, 0, 1),
        BitArray.from_ints(1, 0, 0, 0, 0, 1, 0),
        BitArray.from_ints(0, 0, 1, 1, 1, 0),
    ),
    "4": EncodedNumber(
        BitArray.from_ints(0, 1, 0, 0, 0, 1, 1),
        BitArray.from_ints(0, 0, 1, 1, 1, 0, 1),
        BitArray.from_ints(1, 0, 1, 1, 1, 0, 0),
        BitArray.from_ints(0, 1, 0, 0, 1, 1),
    ),
    "5": EncodedNumber(
        BitArray.from_ints(0, 1, 1, 0, 0, 0, 1),
        BitArray.from_ints(0, 1, 1, 1, 0, 0, 1),
        BitArray.from_ints(1, 0, 0, 1, 1, 1, 0),
        BitArray.from_ints(0, 1, 1, 0, 0, 1),
    ),
    "6": EncodedNumber(
        BitArray.from_ints(0, 1, 0, 1, 1, 1, 1),
        BitArray.from_ints(0, 0, 0, 0, 1, 0, 1),
        BitArray.from_ints(1, 0, 1, 0, 0, 0, 0),
        BitArray.from_ints(0, 1, 1, 1, 0, 0),
    ),
    "7": EncodedNumber(
        BitArray.from_ints(0, 1, 1, 1, 0, 1, 1),
        BitArray.from_ints(0, 0, 1, 0, 0, 0, 1),
        BitArray.from_ints(1, 0, 0, 0, 1, 0, 0),
        BitArray.from_ints(0, 1, 0, 1, 0, 1),
    ),
    "8": EncodedNumber(
        BitArray.from_ints(0, 1, 1, 0, 1, 1, 1),
        BitArray.from_ints(0, 0, 0, 1, 0, 0, 1),
        BitArray.from_ints(1, 0, 0, 1, 0, 0, 0),
        BitArray.from_ints(0, 1, 0, 1, 1, 0),
    ),
    "9": EncodedNumber(
        BitArray.from_ints(0, 0, 0, 1, 0, 1, 1),
        BitArray.from_ints(0, 0, 1, 0, 1, 1, 1),
        BitArray.from_ints(1, 1, 1, 0, 1, 0, 0),
        BitArray.from_ints(0, 1, 1, 0, 1, 0),
    ),
}


def _calculate_checksum(code: str) -> str:
    """
    EAN uses a modulo 10 checksum scheme.
    """
    parity = len(code) % 2
    odd_sum = sum(int(rune) for i, rune in enumerate(code) if i % 2 == parity)
    even_sum = sum(int(rune) for i, rune in enumerate(code) if i % 2 != parity)
    total_sum = (even_sum * 3) + odd_sum

    return str((10 - (total_sum % 10)) % 10)


def _encode_ean8(code: str) -> BitArray:
    """
    Encode an EAN8 barcode.
    """
    result = BitArray()
    result.extend(EDGE)
    for i, digit in enumerate(code):
        if i == EAN8_MIDPOINT:
            result.extend(MIDDLE)

        bits = ENCODER_TABLE[digit]
        result.extend(bits.left_odd if i < EAN8_MIDPOINT else bits.right)

    result.extend(EDGE)
    return result


def _encode_ean13(code: str) -> BitArray:
    """
    Encode an EAN13 barcode.
    """
    result = BitArray()
    result.extend(EDGE)
    first_num = []
    for i, digit in enumerate(code):
        if i == EAN13_MIDPOINT:
            result.extend(MIDDLE)

        num = ENCODER_TABLE[digit]
        if i == 0:
            first_num = num.checksum
            continue
        if i < EAN13_MIDPOINT:
            data = num.left_even if first_num[i - 1] else num.left_odd
        else:
            data = num.right
        result.extend(data)

    result.extend(EDGE)
    return result


def encode_ean(code: str) -> BitArray:
    """
    Encode an EAN8 or EAN13 barcode.
    """
    if len(code) in [7, 12]:
        barcode = code + _calculate_checksum(code)
    elif len(code) in [8, 13]:
        if _calculate_checksum(code[:-1]) != code[-1]:
            raise ValueError("checksum missmatch")
        barcode = code
    else:
        raise ValueError("code is not EAN8 or EAN13")

    encoders = {
        8: _encode_ean8,
        13: _encode_ean13,
    }
    return encoders[len(barcode)](barcode)
