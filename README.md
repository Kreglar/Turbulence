# Turbulence

Tileset/map editor for Sega Genesis homebrew


## Description/Overview

Turbulence allows you to create and edit various graphical asset files for use in Sega Genesis developement/homebrew including:
- Palettes -> 4, 16 color palettes with 3 bits per channel (Red, Green, and Blue)
- Tiles -> 8x8 array of pixels with indexed colors from a palette
- Tilesets -> a set of tiles
- Chunks -> custom size 2D array of indexed tiles from the tileset with certain attributes
- Chunksets -> set of chunks
- Tilemaps -> custom size 2D array of indexed chunks from the chunkset with certain attributes


## Usage

For detailed instructions on how to use Turbulence, visit the [Docs Home](docs/home.md).


## Compiling From Source

To compile from source, make sure you have all the dependencies installed: `pip install pyinstaller PyQt6 numpy`

Then run the build script: `pyinstaller --onefile --noconsole src/main.py`

Finally, copy the resources directory into the dist directory.


## Changelog

Latest version: 1.0.1

Highlights of version:
- Fixes exporting of chunksets and tilemaps
- Documentation and ReadMe updates

Refer to the [Changelog](CHANGELOG.md) for all new features, changes to old features, soon to be removed features, now removed features, and fixed bugs.


## Code of Conduct

Please visit the [Code of Conduct](CODE_OF_CONDUCT.md) for the code of conduct.


## License

This project is licensed under the GNU GPLv3 (GNU General Public License v3.0) for more information read the [License](LICENSE.txt).


## Support

For any questions, concerns, or comments feel free to email me at `kreglar@yahoo.com`

For any issues or bugs regarding the software, consider opening a new issue.


## Authors & Acknowledgements

kreglar - Turbulence lead, programming, art, documentation, everything else
