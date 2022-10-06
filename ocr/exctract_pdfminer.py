from pdfminer.layout import LAParams, LTTextBox
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import resolve1

import collections


from tqdm import tqdm
import argparse
from pathlib import Path

# import os
# os.chdir(os.path.dirname(__file__))


def get_parser():
    """Configuration de argparse pour les options de ligne de commandes"""
    parser = argparse.ArgumentParser(
        prog=f"python {Path(__file__).name}",
        description="Comparaison des performances entre deux requêtes SQL. Ajoute implicitement et automatiquement une commande EXPLAIN.",  # pylint: disable=line-too-long
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--page",
        "-p",
        action="store",
        default=0,
        type=int,
        help="indique la page que l'on veut transformer",
    )
    parser.add_argument(
        "--filename",
        "-f",
        action="store",
        default="output.csv",
        help="indique le nom du fichier de sortie",
    )
    parser.add_argument(
        "--aprox_X",
        "-ax",
        action="store",
        default=70,
        type=int,
        help="indique le nom du fichier de sortie",
    )
    parser.add_argument(
        "--aprox_Y",
        "-ay",
        action="store",
        default=10,
        type=int,
        help="indique le nom du fichier de sortie",
    )

    return parser


listCollumn = []


def reassembleText(tuppleListe):
    def t(x):
        return (round(x[1]), round(x[0]))

    tuppleListe.sort(key=t)
    res = ""
    for tupple in tuppleListe:
        
        res += tupple[2]
    return res


def transformDictToStr(dico, aprox):
    res = ""
    current = 0
    for x in dico:
        nb = listCollumn.index(aproximatif(listCollumn, x, aprox))
        if nb > current:
            for i in range(0, nb - current):
                res += ";"
                current += 1
        print(
            reassembleText(dico[x])
            .replace("\n", "")
            .replace("  ", " ")
            .replace(";", ")")
        )
        res += (
            reassembleText(dico[x])
            .replace("\n", "")
            .replace("  ", " ")
            .replace(";", ")")
            + ";"
        )
        current += 1
    return res[0 : len(res) - 1]


def dicoToCSV(dico, file, aprox):
    dico = collections.OrderedDict(sorted(dico.items(), reverse=True))
    for i in dico:
        dico[i] = collections.OrderedDict(sorted(dico[i].items()))
    for i in dico:
        if (
            len(dico[i]) > 1
            and aproximatif(listCollumn, list(dico[i])[0], aprox) == listCollumn[0]
        ):
            file.write(transformDictToStr(dico[i], aprox) + "\n")


def addList(val, approx):
    if not aproximatif(listCollumn, val, approx) in listCollumn:
        listCollumn.append(val)
        listCollumn.sort()


def aproximatif(collection, i, degresAprox=10):
    for key in collection:
        if i < key + degresAprox and i > key - degresAprox:
            return key
    return i


def pageToCSV(page, file, aprox_Y=10, aprox_X=50):
    global listCollumn
    listCollumn = []
    interpreter.process_page(page)
    layout = device.get_result()
    dico = {}
    for lobj in layout:
        if isinstance(lobj, LTTextBox):
            x, y, text = lobj.bbox[0], lobj.bbox[3], lobj.get_text()
            key_Y = aproximatif(dico, y, aprox_Y)
            addList(x, aprox_X)
            if not key_Y in dico:
                dico[key_Y] = {}
            key_X = aproximatif(dico[key_Y], x, aprox_X)
            if key_X in dico[key_Y]:
                dico[key_Y][key_X].append((x, y, text))
            else:
                dico[key_Y][key_X] = [(x, y, text)]
    dicoToCSV(dico, file, aprox_X)


if __name__ == "__main__":
    args = get_parser().parse_args()

    pdf_file = open("hienghene-Fr.pdf", "rb")
    rsrcmgr = PDFResourceManager()
    laparams = LAParams()
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    pages = PDFPage.get_pages(pdf_file)

    parser = PDFParser(pdf_file)
    document = PDFDocument(parser)
    # This will give you the count of pages
    nbPages = resolve1(document.catalog["Pages"])["Count"]
    start = 62
    end = 252
    i = 0

    numeroPage = args.page

    if numeroPage == 0:
        with tqdm(total=nbPages - 1 - (nbPages - end) - start) as pbar:
            f = open(args.filename, "w")
            for page in pages:
                if i > start and i < end:
                    pageToCSV(page, f, args.aprox_Y, args.aprox_X)
                    pbar.update()
                i += 1
            f.close()
    else:
        if numeroPage >= 0 and numeroPage < nbPages:
            f = open(args.filename, "w")
            for page in pages:
                if i == numeroPage:
                    pageToCSV(page, f, args.aprox_Y, args.aprox_X)
                i += 1
            f.close()
        else:
            print("Le numeros de page est en dehors du pdf")
    pdf_file.close()
