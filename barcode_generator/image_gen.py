"""
Image generator.
"""
import zlib
import struct

from barcode_generator import encode_ean

HEIGHT = 30
PADDING = 4
MAKE_IHDR = True
MAKE_IDAT = True
MAKE_IEND = True

EAN8_BIT_LENGTH = (7 * 8) + 11
EAN13_BIT_LENGTH = (7 * 13) + 11


def _i1(value):
    return struct.pack("!B", value & (2**8-1))


def _i4(value):
    return struct.pack("!I", value & (2**32-1))


def make_png(encoded_barcode: list[bool]):
    if len(encoded_barcode) not in [EAN8_BIT_LENGTH, EAN13_BIT_LENGTH]:
        raise ValueError("Data length does not match.")

    height = HEIGHT
    width = len(encoded_barcode) # + PADDING
    png = b"\x89" + "PNG\r\n\x1A\n".encode("ascii")

    if MAKE_IHDR:
        colortype = 0 # true gray image (no palette)
        bitdepth = 8 # with one byte per pixel (0..255)
        compression = 0 # zlib (no choice here)
        filtertype = 0 # adaptive (each scanline seperately)
        interlaced = 0 # no
        IHDR = _i4(width) + _i4(height) + _i1(bitdepth)
        IHDR += _i1(colortype) + _i1(compression)
        IHDR += _i1(filtertype) + _i1(interlaced)
        block = "IHDR".encode("ascii") + IHDR
        png += _i4(len(IHDR)) + block + _i4(zlib.crc32(block))

    if MAKE_IDAT:
        raw = b""
        for _ in range(height):
            raw += b"\0"  # no filter for this scanline
            for digit in encoded_barcode:
                raw += b"\0" if digit else b"\255"

        compressor = zlib.compressobj()
        compressed = compressor.compress(raw)
        compressed += compressor.flush()
        block = "IDAT".encode("ascii") + compressed
        png += _i4(len(compressed)) + block + _i4(zlib.crc32(block))

    if MAKE_IEND:
        block = "IEND".encode("ascii")
        png += _i4(0) + block + _i4(zlib.crc32(block))

    return png



def main() -> None:
    with open("fixtures/code.png", "wb") as f:
        png = make_png(encode_ean("12345670"))
        f.write(png)
        print(png)


if __name__ == "__main__":
    main()
