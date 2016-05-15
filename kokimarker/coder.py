"""Routines for encoding/decoding a marker number into the grid of
bits to be placed on a marker."""

import pprint

import CrcMoose
import hamming
import mapper


def add_crc(marker_num):
    "Add the CRC to the given marker number"

    CRC12 = CrcMoose.CrcAlgorithm(
        name         = "CRC-12",
        width        = 12,
        polynomial   = (12, 11, 3, 2, 1, 0),
        seed         = 0,
        lsbFirst     = True,
        xorMask      = 0)

    marker_chr = chr(int((marker_num+1) % 256))
    crc = CRC12.calcString(marker_chr)

    print("num: {0}, crc: {1}".format(marker_num, crc))

    code = (crc << 8) | marker_num

    print("{0:x}".format(code))

    return code

def code_to_lists(code):
    "Split the given code up into sections for hamming"
    output = []

    for i in range(5):
        l = []

        for j in range(4):
            mask = 0x1 << (i*4+j)
            tmp = code & mask
            bit = 1
            if (tmp == 0):
                bit = 0

            l.append(bit)

        output.append(l)

    return output

def print_lists_as_hex(l):
    for part in l:
        total = 0
        for i, val in enumerate(part):
            total |= val << i

        # At this point the value of 'total' should be equivalent to
        # the value of a single element of the 'codes' array of arrays
        # from the code_rotations function in code_grid.c
        print("{0} (0x{0:x})".format(total))

def encoded_lists(l):
    "Add hamming codes to all the items of the given list"

    #pprint.pprint(l)
    #print_lists_as_hex(l)

    return map(hamming.encode, l)

def code_grid(code):
    "Return the grid for the given (mapped) code"

    # code_to_lists returns a list of 5 groups of 4 bits
    # encoded_lists adds hamming, resulting in 5 groups of 7 bits
    blocks = encoded_lists(code_to_lists(code))

    pprint.pprint(blocks)
    print_lists_as_hex(blocks)
    #blocks = ['abcdefg', 'hijklmn', 'opqrstu', 'vwxyzAB', 'CDEFGHI']

    cell = 0

    grid = [[-1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1]]

    # arrange the 35 bits into a square, striping diagonally top right
    # to bottom left
    for i in range(7):
        for j in range(5):
            grid[cell / 6][cell % 6] = blocks[j][i]
            cell = cell + 1

    return grid

def user_code_grid( usercode ):
    "Return the grid for the given user-friendly code"

    marker_code = mapper.user_friendly_to_marker_code( usercode )
    c = add_crc( marker_code )
    grid = code_grid(c)

    return grid
