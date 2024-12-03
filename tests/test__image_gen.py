"""
Unit tests for the ``barcode_generator.image_gen`` module.
"""

import pathlib

from barcode_generator import encode_ean, make_png

HERE = pathlib.Path(__file__).parent


def _read_png_fixture(name: str) -> bytes:
    with open(HERE / "fixtures" / name, "rb") as f:
        return f.read()


def test__barcodes_can_be_written_to_png():
    """
    Barcodes can be written to PNG.
    """
    barcode = "12345670"
    assert make_png(encode_ean(barcode)) == _read_png_fixture("12345670.png")
