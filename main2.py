import argparse

from data_helpers import *

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='giphygrab - save a GIF today!')
    parser.add_argument('area', help='area name (e.g. "New York, NY", a zipcode, etc.)')
    parser.add_argument('-n', '--name', help='filename to save GIF as (default: giphygrab<time>.gif)',
                        default=f'')
    parser.add_argument('-o', '--output',
                        help='Path of the output directory (default is defined in config.json)')

    # argument types:
    #     load from file vs get new data
    #     for sale vs rent
    #     save to file flag
    #     file type to save as
    #     number of pages to retrieve (default all)
    #
    # TODO remove comments
    # args = parser.parse_args()
    # args = parser.parse_args(
    #     ['https://giphy.com/gifs/long-far-FbPsiH5HTH1Di', '-o', '.', '-n', 'test.gif'])
    args = parser.parse_args()