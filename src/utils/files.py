# handle images
from PIL import Image

# handle application settings
import json

# use custom data formats
from . import data

def ReadJson(jsonPath: str) -> dict:
    """ Return application settings in json format. """
    # read json file
    with open(jsonPath, 'r') as file:
        jsonData = json.load(file)

    return jsonData

def WriteJson(jsonData: dict, jsonPath: str) -> None:
    """ Write application settings in json settings file. """
    # write to json
    with open(jsonPath, 'w') as file:
        json.dump(jsonData, file, indent=4)

def ExtractBytes(filepath: str) -> bytearray:
    """ Opens and extracts bytes from file. """
    
    # read file as binary
    with open(filepath, "rb") as file:
        # get each byte
        filebytes = file.read()

    return filebytes

def ExtractBinDataAsm(filepath: str) -> bytearray:
    """ Extracts binary data from 68k assembly source text. """
    # read text file
    with open(filepath, "r") as file:
        # split into lines
        asm = file.read().split("\n")
    
    binary = bytearray()

    # parse lines
    for line in asm:
        # remove comments/white space and lowercase the line
        line = line.split(";")[0].strip().lower()

        byteDefines = ["dc.b ", "dc.w ", "dc.l ", ".byte ", ".word ", ".long "] # list out every way to define bytes
        if any(item in line for item in byteDefines): # check for byte defines
            # remove the byte define
            for item in byteDefines:
                line = line.replace(item, "")
            line = line.replace(" ", "") # remove spaces

            # split for every group of bytes defined per line
            for item in line.split(","):
                # convert hex to int and add to bytearray
                if item.startswith("$") or item.startswith("0x"):
                    # get rid of hex specification sequence
                    item = item.replace("$", "").replace("0x", "")

                    # make sure there is actual data
                    if not item:
                        continue

                    # ensure length is multiple of two
                    if len(item) % 2 == 1:
                        item = "0" + item
                    
                    itembytes = [item[i:i+2] for i in range(0, len(item), 2)] # get the bytes for every item
                    try:
                        for i in itembytes: # append all the bytes
                            binary.append(int("0x" + i, 16))
                    except Exception as error: # couldn't convert to dec: hex in wrong format
                        raise ValueError(f"utils/files.py: ExtractBinDataAsm: Hexadecimal data not hexadecimal format.") from error
                
                # convert bin to int and add to bytearray
                elif item.startswith("%"):
                    # get rid of bin specification character
                    item = item.replace("%", "")

                    # make sure there is actual data
                    if not item:
                        continue

                    # ensure length is multiple of eight
                    if len(item) % 8 != 0:
                        item = (len(item) % 8 * "0") + item
                    
                    itembytes = [item[i:i+8] for i in range(0, len(item), 8)] # get the bytes for every item
                    try:
                        for i in itembytes: # append all the bytes
                            binary.append(int(i, 2))
                    except Exception as error: # couldn't convert to dec: binary in wrong format
                        raise ValueError(f"utils/files.py: ExtractBinDataAsm: Binary data not binary format.") from error
                
                # convert dec to hex and back to dec
                else:
                    # make sure there is actual data
                    if not item:
                        continue

                    # get the hexadecimal representation
                    try:
                        hexVal = hex(int(item)).replace("0x", "")
                    except Exception as error:
                        raise ValueError(f"utils/files.py: ExtractBinDataAsm: Decimal data not decimal format.") from error
                    
                    # ensure length is multiple of two
                    if len(hexVal) % 2 == 1:
                        hexVal = "0" + hexVal
                    
                    itembytes = [hexVal[i:i+2] for i in range(0, len(hexVal), 2)] # get the bytes for every item
                    for i in itembytes: # append all the bytes
                        binary.append(int("0x" + i, 16))
                    
    return binary

def ExtractPalettesBin(bin: bytearray) -> list[data.Palette]:
    """ Extract palette data from binary byte list. """
    # split into groups of 2 bytes, colors
    genesisColors = [bin[i:i+2] for i in range(0, len(bin), 2)]

    # split colors into RGB
    RGBColors = []
    for color in genesisColors:
        red = ((color[1] & 0xE) * 255) // 14 # NOTE: color channels are 3 bit (1110) so we use E (1110) not F (1111)
        green = (((color[1] >> 4) & 0xE) * 255) // 14
        blue = ((color[0] & 0xE) * 255) // 14
        RGBColors.append(data.Color(red, green, blue))
    
    # split into palettes and return
    return [data.Palette(RGBColors[color:color+16]) for color in range(0, len(RGBColors), 16)]

def ExtractTilesetBin(bin: bytearray) -> data.Tileset:
    """ Extract tileset data from binary byte list. """
    
    # split into tiles
    genesisTiles = [bin[i:i+32] for i in range(0, len(bin), 32)]

    # split tiles into 2d arrays
    #                                        get each row of a tile ----------------------- for every row ---- for every tile    
    return data.Tileset(len(genesisTiles), [[sum([tile[(y * 4) + x] for x in range(4)], []) for y in range(8)] for tile in genesisTiles])

def ExtractChunksetBin(bin: bytearray, chunkSize: int) -> data.Chunkset:
    """ Extract chunkset data from binary byte list. """
    # get the tiles/bytes per chunk
    tilesPerChunk = (chunkSize * chunkSize)
    
    # convert data in tiles
    tiles = []
    for i in range(0, len(bin), 2):
        # get all tile data
        tileData = bin[i:i+2]
        priority = bool((tileData >> 15) & 0b01)
        palette = (tileData >> 13) & 0b11
        hFlip = bool((tileData >> 12) & 0b01)
        vFlip = bool((tileData >> 11) & 0b01)
        id = tileData & 0b011111111111
        tiles.append(data.Tile(priority, palette, hFlip, vFlip, id))

    # seperate tiles into chunks
    chunks = [tiles[i:i+tilesPerChunk] for i in range(0, len(tiles), tilesPerChunk)]

    # convert into 2d arrays and return
    #                                              get row of chunk ----------------------------------- add each row to chunk ---- for every chunk
    return data.Chunkset(len(chunks), chunkSize, [[chunk[(y * chunkSize):((y * chunkSize) + chunkSize)] for y in range(chunkSize)] for chunk in chunks])

def ExtractTilemapBin(bin: bytearray, size: tuple[int, int]) -> data.Tilemap:
    """ Extract tilemap data from binary byte list. """
    # convert into chunks
    chunks = []
    for i in range(0, len(bin), 2):
        # get all chunk data
        chunkData = bin[i:i+2]
        hFlip = bool((chunkData >> 15) & 0b01)
        vFlip = bool((chunkData >> 15) & 0b01)
        id = chunkData & 0b0011111111111111
        chunks.append(data.Chunk(hFlip, vFlip, id))

    # break into 2d array and return
    #                          get row of tilemap ---------------------------- add each row to tilemap
    return data.Tilemap(size, [chunks[(y * size[0]):((y * size[0]) + size[0])] for y in range(size[0])])

def ExtractPaletteImg(imgpath: str) -> data.Palette:
    """ Extract palette data from bitmap image. """
    # open the image
    img = Image.open(imgpath)
    
    # get the palette
    palette = img.getpalette()
    paletteColor = [data.Color(palette[i], palette[i+1], palette[i+2]) for i in range(0, len(palette), 3)]
    
    return data.Palette(paletteColor)

def ExtractTilesetImg(imgpath: str) -> data.Tileset:
    """ Extract tileset data from bitmap image. """
    # open the image
    img = Image.open(imgpath)
    
    # read image data
    sizePixels = img.size
    sizeTiles = (sizePixels[0] // 8, sizePixels[0] // 8)
    numTiles = sizeTiles[0] * sizeTiles[1]
    pixels = img.getdata()

    # convert into list of 8x8 2d arrays - I'm so sorry
    #          get pixels of row of tile -------------------------------------------------------------------------------------------------------------------------- for each row and tile
    #                     (tile y * 8) + y = px y  | px y * width  |  tile x * 8 = px x   | do the same thing but add 8 to get full row                         v
    tiles = [[[pixels[((((tile//sizeTiles[0])*8)+y)*sizePixels[0])+((tile%sizeTiles[0])*8):((((tile//sizeTiles[0])*8)+y)*sizePixels[0])+((tile%sizeTiles[0])*8)+8]] for y in range(8)] for tile in range(numTiles)]

    return data.Tileset(numTiles, tiles)
