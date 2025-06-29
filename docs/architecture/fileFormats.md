# File Fomats

## Turbulence Graphics Editor (*.tge)

Based on the json file format.

```
{
    "palettes": [
        [(red, green, blue) x16] x4
    ],

    "tileset": {
        "size": size of set,
        "set": [
            [
                [color index x8] x8
            ] x amount of tiles
        ]
    },

    "chunkset": {
        "size": size of set,
        "chunkSize": size of chunks,
        "set": [
            [
                [(palette, id, priority, hFlip, vFlip) x chunkSize] x chunkSize
            ] x amount of chunks
        ]
    },

    "tilemap": {
        "size": (length, width),
        "map": [
            [(id, hFlip, vFlip) x length] x width
        ]
    }
}
```
