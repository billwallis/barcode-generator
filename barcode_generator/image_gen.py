"""
Image generator.
"""

import struct
import zlib

HEIGHT = 30
PADDING = 4

TRUE_GRAY = 0  # true gray image (no palette)
ONE_BYTE_PER_PIXEL = 8  # one byte per pixel (0..255)
ZLIB = 0
ADAPTIVE = 0  # each scanline separate
NO_INTERLACE = 0  # no

EAN8_BIT_LENGTH = (7 * 8) + 11
EAN13_BIT_LENGTH = (7 * 13) + 11


def _i1(value):
    return struct.pack("!B", value & (2**8 - 1))


def _i4(value):
    return struct.pack("!I", value & (2**32 - 1))


def _png_header(  # noqa: PLR0913
    width: int,
    height: int,
    color_type: int = TRUE_GRAY,
    bit_depth: int = ONE_BYTE_PER_PIXEL,
    compression: int = ZLIB,
    filter_type: int = ADAPTIVE,
    interlaced: int = NO_INTERLACE,
) -> bytes:
    header = (
        _i4(width)
        + _i4(height)
        + _i1(bit_depth)
        + _i1(color_type)
        + _i1(compression)
        + _i1(filter_type)
        + _i1(interlaced)
    )
    block = "IHDR".encode("ascii") + header

    return _i4(len(header)) + block + _i4(zlib.crc32(block))


def _png_footer() -> bytes:
    block = "IEND".encode("ascii")

    return _i4(0) + block + _i4(zlib.crc32(block))


def _png_data(data: list[bool], width: int, height: int) -> bytes:
    raw = b""
    for _ in range(height):
        raw += b"\0"  # no filter for this scanline
        for digit in data:
            raw += b"\0" if digit else b"\255"

    compressor = zlib.compressobj()
    compressed = compressor.compress(raw) + compressor.flush()
    block = "IDAT".encode("ascii") + compressed

    return _i4(len(compressed)) + block + _i4(zlib.crc32(block))


def make_png(encoded_barcode: list[bool]):
    if len(encoded_barcode) not in [EAN8_BIT_LENGTH, EAN13_BIT_LENGTH]:
        raise ValueError("Data length does not match.")

    height = HEIGHT
    width = len(encoded_barcode)  # + PADDING

    return (
        b"\x89"
        + "PNG\r\n\x1a\n".encode("ascii")
        + _png_header(width, height)
        + _png_data(encoded_barcode, width, height)
        + _png_footer()
    )
