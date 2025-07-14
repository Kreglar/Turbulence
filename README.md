# Turbulence

Tileset/map editor for Sega Genesis homebrew

## Table of Contents
- [License](#License)
- [Description/Overview](#descriptionoverview)
- [Installation](#installation)
- [Usage](#usage)
- [Compiling From Source](#compiling-from-source)
- [Changelog](#changelog)
- [Contributing](#contributing)
- [Code of Conduct](#code-of-conduct)
- [Support](#support)
- [Authors & Acknowledgements](#authors--acknowledgement)


## License

This project is licensed under the GNU GPLv3 (GNU General Public License v3.0) for more information read the [License](LICENSE.txt).


## Description/Overview

Turbulence allows you to create and edit various graphical asset files for use in Sega Genesis developement/homebrew including:
- Palettes -> 4, 16 color palettes with 3 bits per channel (Red, Green, and Blue)
- Tiles -> 8x8 array of pixels with indexed colors from a palette
- Tilesets -> a set of tiles
- Chunks -> custom size 2D array of indexed tiles from the tileset with certain attributes
- Chunksets -> set of chunks
- Tilemaps -> custom size 2D array of indexed chunks from the chunkset with certain attributes


## Installation


## Usage

For detailed instructions on how to use Turbulence, visit the [Guide Home](docs/guide/guideHome.md).


## Compiling From Source

To compile from source, make sure you have all the dependencies installed: `pip install pyinstaller PyQt6 numpy`

Then run the build script: `pyinstaller --onefile --noconsole src/main.py`

Finally, copy the recources directory into the dist directory.


## Changelog

Latest version: 1.0.0

Highlights of version:
- Initial release!

Refer to the [Changelog](CHANGELOG.md) for all new features, changes to old features, soon to be removed features, now removed features, and fixed bugs.


## Contributing

For a detailed explanation about the inner workings of Turbulence visit the [Architecture Home](docs/architecture/architectureHome.md)


## Code of Conduct

Please visit the [Code of Conduct](CODE_OF_CONDUCT.md) for the code of conduct.


## Support


## Authors & Acknowledgements

kreglar - Turbulence lead, programming, art, documentation, everything else
