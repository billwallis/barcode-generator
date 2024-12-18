"""
Barcode generator.
"""

import pathlib

import arguably

from barcode_generator import encode_ean, make_png

CATALOG = pathlib.Path(__file__).parent.parent / "catalog"


@arguably.command
def __root__() -> None:  # noqa: N807
    if arguably.is_target():
        print("use 'code-gen --help' to see available commands")


@arguably.command
def ean(code: str) -> None:
    """
    Print the barcode for an EAN.
    """
    png = make_png(encode_ean(code))
    with open(CATALOG / f"{code}.png", "wb") as file:
        file.write(png)


if __name__ == "__main__":
    arguably.run(name="barcode_generator")
