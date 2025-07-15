# Turbulence Documentation Home


## Table of Contents
- [What is Turbulence?](#what-is-turbulence)
- [What is a Palette on the Sega Genesis](#what-is-a-palette-on-the-sega-genesis)
- [What is a Tileset on the Sega Genesis](#what-is-a-tileset-on-the-sega-genesis)
- [What is a Chunkset on the Sega Genesis](#what-is-a-chunkset-on-the-sega-genesis)
- [What is a Tilemap on the Sega Genesis](#what-is-a-tilemap-on-the-sega-genesis)


## What is Turbulence?

Turbulence is an assets ediotr for Sega Genesis homebrew. It allows you to create, edit, and export: palettes, tilesets, chunksets, and tilemaps.

### What is a Palette on the Sega Genesis

A palette on the Sega Genesis is made up of 16 colors. Each color has a red, green, and blue value each made of 3 bits. The Genesis has 4 of these palettes.

### What is a Tileset on the Sega Genesis

A tileset is a list of tiles that are 8x8 pixels in size. Each pixel is an index in any of the palettes.

### What is a Chunkset on the Sega Genesis

A chunkset is a list of (any)x(any) tiles. Each tile can use 1 palette at a time and can store horizontal/vertical mirroring values.

### What is a Tilemap on the Sega Genesis

A tilemap is an (any)x(any) array of chunks. Each chunk can store horizontal/vertical mirroring values.
