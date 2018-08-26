# coding = utf-8

from __future__ import print_function, unicode_literals
import os
import sys
import shutil


def convert_to_utf8(filename):
    # gather the encodings you think that the file may be
    # encoded inside a tuple
    encodings = ('windows-1253', 'iso-8859-7', 'utf-8')

    with open(filename, 'r') as f:
        for enc in encodings:
            try:
                data = f.read().decode(enc)
                break
            except UnicodeDecodeError:
                if enc == encodings[-1]:
                    print('Encoding doesn\'t belong to' + ' ,'.join(encodings))
                    sys.exit(1)
                continue

    # and at last convert it to utf-8
    with open(filename, 'w') as f:
        f.write(data.encode('utf-8'))
