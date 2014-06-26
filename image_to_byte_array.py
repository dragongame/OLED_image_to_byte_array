#!/usr/bin/python2.7
"""Convert an image to a byte array ascii representation sutiable for OLEDs"""
from PIL import Image

__author__ = "Arne Kreutzmann"
__copyright__ = "Copyright 2014, DragonGame (Arne Kreutzmann)"
__credits__ = ["Arne Kreutzmann" ]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Arne Kreutzmann"
__email__ = "mail@arne-kreutzmann.de"
__status__ = "Prototype"

def set( image, x, y, on ):
    """Set the given pixel to either on or off.
    Image is a continous array."""

    # calculate the vertical byte
    y2 = y / 8
    # calculate the bit
    b  = y % 8
    # calculate the absolute byte index
    idx = y2*128 + x

    if on:
        image[idx] |= (1 << b)  # set the bit
    else:
        image[idx] &= ~(1 << b) # unset the bit


def convert( image,  fixed_size=(128,64) ):
    """Convert an image to the specific OLED encoding.

    First the image is converted to a binary black and white image using 127 as threshold.
    The OLED is turned on for black pixels and off for white pixels.
    A single pixel is represented by a single bit, packed in chunks of 8 into a byte.

    PNG
    11 12 13 14 15 16 17 18 19 1A 1B 1C ...
    21 22 23 24 25 26 27 28 29 2A 2B 2C ...
    31 32 33 34 35 36 37 38 39 3A 3B 3C ...
    41 42 43 44 45 46 47 48 49 4A 4B 4C ...
    51 52 53 54 55 56 57 58 59 5A 5B 5C ...
    61 62 63 64 65 66 67 68 69 6A 6B 6C ...
    71 72 73 74 75 76 77 78 79 7A 7B 7C ...
    81 82 83 84 85 86 87 88 89 8A 8B 8C ...
    91 92 93 94 95 96 97 98 99 9A 9B 9C ...

    OLED Binary
    | -------  1 byte ------- | -------  2 byte ------- | -------  3 byte ------- | ...
    | 11 21 31 41 51 61 71 81 | 12 22 32 42 52 62 72 82 | 13 23 33 43 53 63 73 83 | ...
    """

    img = image.convert("1")
    # load image and convert to binary
    if fixed_size:
        assert img.size == fixed_size

    data = [ 0 for _ in range( img.size[0]*img.size[1] ) ]

    for i, value in enumerate(img.getdata()):
        y = i / 128
        x = i % 128

        # turn off for white pixels and on for black pixels
        set( data, x, y, not value )


    return data

def join_with_linebreak( data, join_string, per_line=80 ):
    """Join a string and add newlines after no more than per_line characters are printed"""
    # a data element uses 3 characters
    num_per_line = per_line / (3 + len(join_string))
    result = ""

    for idx in range(0,len(data),num_per_line):
        end = min( idx+num_per_line, len(data) )
        result += join_string.join( data[ idx:end ] )
        if end != len(data):
            result += join_string + '\n'

    return result

def save( data, orig_filename, filename=None,  name=None ):
    """Save an OLED encoded array to a file.
    If name is given, than the output will be a C array with this name
    otherwise just an ascii representation with spaces will be printed.
    If filename is None than the output is printed to stdout."""

    if name:
        join_string = ", "
    else:
        join_string = " "

    data_string = join_with_linebreak( ["0x%02X" % datum for datum in data], join_string )

    if name:
        output_string = """
        /*
         * Image converted from '%s'
         */

        prog_uchar %s[] PROGMEM = {
        """ % (orig_filename, name)
        output_string += data_string + '\n'
        output_string += "};\n"
    else:
        output_string = data_string

    if filename:
        with open( filename, 'w' ) as out:
            out.write( output_string )
    else:
        print( output_string )

if __name__ == "__main__":
    import sys, os

    if len(sys.argv) < 2:
        print( '' )
        print( "Usage:" )
        print( sys.argv[0] + " <png_filename> [output filename]" )
        print( '' )
        print( "If no output filename is given, than the result is printed to standard out" )
        print( '' )
        exit(-1)

    png_filename = sys.argv[1]
    try:
        out_filename = sys.argv[2]
    except IndexError:
        out_filename = None

    array_name = os.path.splitext( os.path.basename( png_filename ) )[0]
    array_name = array_name.replace(' ','_')

    img = Image.open( png_filename )
    bin_array = convert( img )
    save( bin_array, png_filename, out_filename, array_name )

