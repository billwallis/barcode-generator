"""
Converts a list of list into gray-scale PNG image.
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
    x3 = len(code) == 7
    sum = 0
    for r in code:
        cur_num = int(r)
        if cur_num < 0 or cur_num > 9:
            return 'B'
        if x3:
            cur_num = cur_num * 3
        x3 = not x3
        sum += cur_num
    return str((10 - (sum % 10)) % 10)


def _encode_ean8(code: str) -> BitArray:
    result = BitArray()
    result.extend(EDGE)
    for i, digit in enumerate(code):
        num = ENCODER_TABLE[digit]
        data = num.left_odd if i < 4 else num.right
        if i == 4:
            result.extend(MIDDLE)
        result.extend(data)
    result.extend(EDGE)
    return result


def _encode_ean13(code: str) -> BitArray:
    result = BitArray()
    result.extend(EDGE)
    first_num = []
    for cpos, r in enumerate(code):
        num = ENCODER_TABLE[r]
        if cpos == 0:
            first_num = num.checksum
            continue
        if cpos < 7:
            data = num.left_even if first_num[cpos - 1] else num.left_odd
        else:
            data = num.right
        if cpos == 7:
            result.extend(MIDDLE)
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

    return _encode_ean8(barcode) if len(barcode) == 8 else _encode_ean13(barcode)
