import argparse
from pathlib import Path
import re
from shutil import copyfile
from threading import Thread
import logging


"""
python clean.py -s picture -o dist
"""

parser = argparse.ArgumentParser(description='App for sorting folder')
parser.add_argument('-s', '--source', help="Source folder", required=True)
parser.add_argument('-o', '--output', default='dist')
args = vars(parser.parse_args())
source = args.get('source')
output = args.get('output')

FOLDERS = []
base_folder = Path(source)
output_folder = Path(output)


CYRILLIC_SYMBOLS = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ'
TRANSLATION = ("a", "b", "v", "g", "d", "e", "e", "j", "z", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
               "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu", "u", "ja", "je", "ji", "g")

TRANS = {}
for c, l in zip(CYRILLIC_SYMBOLS, TRANSLATION):
    TRANS[ord(c)] = l
    TRANS[ord(c.upper())] = l.upper()

def normalize(name: str) -> str:
    first_part = name.split('.')[0]
    extension = name.split('.')[1]
    t_name = first_part.translate(TRANS)
    t_name = re.sub(r'\W', '_', t_name)
    final_name = f'{t_name}.{extension}'
    return final_name


def grabs_folder(path: Path):
    for el in path.iterdir():
        if el.is_dir():
            FOLDERS.append(el)
            grabs_folder(el)


def sort_file(path: Path):
    for el in path.iterdir():
        if el.is_file():
            ext = el.suffix
            new_path = output_folder / ext
            try:
                new_path.mkdir(exist_ok=True, parents=True)
                copyfile(el, new_path / normalize(el.name))
            except OSError as e:
                logging.error(e)


def main():
    logging.basicConfig(level=logging.DEBUG, format="%(threadName)s %(message)s")
    FOLDERS.append(base_folder)
    grabs_folder(base_folder)
    logging.debug(FOLDERS)
    threads = []
    for folder in FOLDERS:
        th = Thread(target=sort_file, args=(folder,))
        th.start()
        threads.append(th)
    [th.join() for th in threads]
    print('Finished. Source folder can be removed.')


if __name__ == '__main__':
    main()
