import os

import pytesseract
import fitz

import cv2
import numpy as np

import argparse

from pathlib import Path
import json

from tqdm import tqdm

DELIM = "#@#"

MODIF_RECU = [
    ("- ", ""),
    ("(7)", "(T)"),
    ("(11)", "(il)"),
    ("({)", "(Y)"),
    ("(})", "(Y)"),
    ("{", "("),
    ("}", ")"),
    ("(0)", "(O)"),
    ("fT)", "(T)"),
    (";", ","),
]

LANGUE_LIST = [
    "français",
    "pije",
    "fwâi",
    "nemi",
    "temala",
    "nemi",
    "côte est",
    "jawe",
    "pige",
    "fuät",
    "fuat",
    "nemt",
    "jave",
]


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
        "--output",
        "-o",
        action="store",
        default="output",
        help="indique le nom du fichier de sortie",
    )
    parser.add_argument(
        "--filename",
        "-f",
        action="store",
        default="hienghene-Fr.pdf",
        help="indique le nom du pdf d'entré",
    )
    parser.add_argument(
        "--aprox_x",
        "-ax",
        action="store",
        default=70,
        type=int,
        help="aproximation en largeur",
    )
    parser.add_argument(
        "--aprox_y",
        "-ay",
        action="store",
        default=10,
        type=int,
        help="aproximation en heauteur",
    )
    parser.add_argument("--show", action="store_true")

    return parser


def overlap(
    elem1, elem2, tolerence_top=0, tolerence_left=0
):  # pylint: disable=missing-function-docstring
    if (
        (elem1["top"] >= elem2["top"] + elem2["height"] + tolerence_top)
        or (elem1["top"] + elem1["height"] <= elem2["top"] - tolerence_top)
        or (elem1["left"] + elem1["width"] <= elem2["left"] - tolerence_left)
        or (elem1["left"] >= elem2["left"] + elem2["width"] + tolerence_left)
    ):
        return False
    return True


def compare(elem1, elem2, tolerence=1):  # pylint: disable=missing-function-docstring
    return (
        abs(elem1["top"] - elem2["top"]) < tolerence
        and abs(elem1["left"] - elem2["left"]) < tolerence
    )


def return_index_of_array(
    array, element
):  # pylint: disable=missing-function-docstring,redefined-outer-name
    for test in array:
        if compare(test, element):
            return array.index(test)
    return None


def concat(
    array, res, element1, element2
):  # pylint: disable=missing-function-docstring
    if (
        abs(element1["top"] - element2["top"]) > 20
        and element1["top"] < element2["top"]
    ):
        text = element1["text"] + " " + element2["text"]
    else:
        text = element2["text"] + " " + element1["text"]
    to_add = {
        "top": min(element1["top"], element2["top"]),
        "left": min(element2["left"], element1["left"]),
        "width": max(
            element1["left"] + element1["width"],
            element2["left"] + element2["width"],
        )
        - min(element1["left"], element2["left"]),
        "height": max(
            element1["top"] + element1["height"],
            element2["top"] + element2["height"],
        )
        - min(element1["top"], element2["top"]),
        "text": text,
    }
    # if "tr" in element1["text"] or "tr" in element2["text"]:
    #     print("1 : ", element1)
    #     print("2 : ", element2)
    array.append(to_add)
    res.append(to_add)

    try:
        del res[res.index(element2)]
    except:
        pass
    try:
        del res[return_index_of_array(res, element1)]
    except:
        pass


def not_column_begin(elem, approx=200):
    return abs(elem["left"] - COLLUMN_TO_LANGUE[get_closest_lang(elem)]) > approx


def global_compare(
    element1, element2, array, approx_top=15, approx_left=90
):  # pylint: disable=missing-function-docstring
    return (
        overlap(element1, element2, tolerence_left=100, tolerence_top=0)
        and not_column_begin(element1)
        and not_column_begin(element2)
        or (
            (
                abs(COLLUMN_TO_LANGUE["français"] - element1["left"]) < approx_left
                and abs(COLLUMN_TO_LANGUE["français"] - element2["left"]) < approx_left
            )
            and overlap(
                element1, element2, tolerence_left=approx_left, tolerence_top=approx_top
            )
        )
        or (overlap(element1, element2, tolerence_left=50, tolerence_top=0))
    )


def get_fr_column(array):  # pylint: disable=missing-function-docstring
    res = []
    for element in array:
        if abs(element["left"] - COLLUMN_TO_LANGUE["français"]) < 400:
            res.append(element)
    return res


def get_most_close_fr(array, element):  # pylint: disable=missing-function-docstring
    fr_array = get_fr_column(array)
    res = fr_array[0]
    for element_fr in fr_array:
        if abs(element_fr["top"] - element["top"]) < abs(res["top"] - element["top"]):
            res = element_fr
    return res


def fr_compare(element1, element2, array):  # pylint: disable=missing-function-docstring
    element1_close = get_most_close_fr(array, element1)
    element2_close = get_most_close_fr(array, element2)
    return (
        (not compare(element1, element1_close) or not compare(element2, element2_close))
        and abs(element2["left"] - element1["left"]) < 200
        and compare(element1_close, element2_close)
    )


def concat_box(array, func_compare):  # pylint: disable=missing-function-docstring

    change = True
    while change:
        change = False
        res = []
        for element1 in array:
            if (
                not any(overlap(element1, elem2) for elem2 in res)
                and element1["top"] > TITLE_TOP
            ):
                res.append(element1)

                for element2 in res:
                    if not overlap(element1, element2) and func_compare(
                        element1, element2, array
                    ):
                        change = True
                        concat(array, res, element1, element2)
            else:

                for element2 in res:
                    if overlap(element1, element2) and func_compare(
                        element1, element2, array
                    ):
                        change = True
                        concat(array, res, element1, element2)

        array = res

    return res


def get_the_min(array):  # pylint: disable=missing-function-docstring
    res = 10_000
    for element in array:  # pylint: disable=redefined-outer-name
        if element["top"] > TITLE_TOP:
            res = min(res, element["left"])
    return res


def get_the_smallest_overlap(array, elem_test):
    smallest = elem_test
    for elem in array:
        if (
            overlap(elem, elem_test)
            and elem["width"] * elem["height"] < smallest["width"] * smallest["height"]
        ):
            smallest = elem
    return smallest


def suppr_overlap(array):
    res = []
    change = True
    while change:
        change = False
        for element1 in array:
            if element1["top"] > TITLE_TOP:
                smallest_overlap = get_the_smallest_overlap(array, element1)
                if not any(overlap(smallest_overlap, element2) for element2 in res):
                    change = True
                    res.append(element1)
                elif not compare(smallest_overlap, element1):
                    for elem_res in res:
                        if (
                            overlap(elem_res, smallest_overlap)
                            and len(
                                list(
                                    set(
                                        smallest_overlap["text"].lower().split()
                                    ).intersection(elem_res["text"].lower().split())
                                )
                            )
                            == 0
                        ):
                            res.append(smallest_overlap)

    return res


def particionner(tab, deb, fin, func):
    if deb < fin:
        curent = deb
        for i in range(deb + 1, fin):
            if func(tab[curent], tab[i]) and curent < i:
                tmp = tab[curent]
                tab[curent] = tab[i]
                tab[i] = tab[curent + 1]
                tab[curent + 1] = tmp
                curent += 1
        particionner(tab, deb, curent, func)
        particionner(tab, curent + 1, fin, func)


def triRapide(tab, func):
    particionner(tab, 0, len(tab), func)


def compare_sort(elem1, elem2):
    if elem1["top"] + elem1["height"] < elem2["top"]:
        return 0
    if elem2["top"] + elem2["height"] < elem1["top"]:
        return 1
    if elem1["left"] < elem2["left"]:
        return 0
    return 1


def overlap_from_two_array(
    array_base, array_clean
):  # pylint: disable=missing-function-docstring
    res = []
    for element_clean in array_clean:
        tmp = []
        for element_base in array_base:
            if overlap(element_clean, element_base):
                tmp.append(element_base)
        triRapide(tmp, compare_sort)
        # print(tmp)
        tmp_text = ""
        for text in tmp:
            tmp_text += " " + text["text"]
        for rule in MODIF_RECU:
            tmp_text = tmp_text.replace(rule[0], rule[1])
        res.append(
            {
                "top": element_clean["top"],
                "left": element_clean["left"],
                "width": element_clean["width"],
                "height": element_clean["height"],
                "text": tmp_text,
            }
        )
    return res


def from_array_to_line(array):
    fr_col = get_fr_column(array)
    res = {}
    for fr_elem in fr_col:
        res[fr_elem["top"]] = []
    for elem in array:
        fr_ref = get_most_close_fr(array, elem)
        res[fr_ref["top"]].append(elem)
    return res


def get_closest_lang(elem):
    res = "français"
    for langue in COLLUMN_TO_LANGUE:
        # print(elem["left"])
        # print(COLLUMN_TO_LANGUE[langue])
        if abs(elem["left"] - COLLUMN_TO_LANGUE[langue]) < abs(
            elem["left"] - COLLUMN_TO_LANGUE[res]
        ):
            res = langue
    if res == "français_tab":
        return "français"
    return res


def from_line_to_csv(array):
    res = ""
    tmp = {}
    for elem in array:
        # print(array)
        lang = get_closest_lang(elem)
        elem["langue"] = lang
        if lang in tmp:
            tmp[lang]["text"] += " ||" + elem["text"] + " (error)"
        else:
            tmp[lang] = elem
    if len(tmp) > 1:
        for _, elem in tmp.items():
            res += (
                elem["langue"]
                + DELIM
                + " ".join(elem["text"].split())
                + DELIM
                + str(elem["top"])
                + DELIM
                + str(elem["left"])
                + DELIM
                + str(elem["width"])
                + DELIM
                + str(elem["height"])
                + ";"
            )
        return res[0 : len(res) - 1]
    else:
        return ""


def find_title_coord(array):
    tmp = []
    for elem in array:
        if len(list(set(elem["text"].lower().split()).intersection(LANGUE_LIST))) != 0:
            tmp.append(elem)
    if len(tmp) == 0:
        return 0
    tmp_res = 9999999999999999
    for elem in tmp:
        if elem["top"] < tmp_res:
            tmp_res = elem["top"]
    res = 0
    count = 0
    for elem in tmp:
        if abs(elem["top"] - tmp_res) < 50:
            res += elem["top"]
            count += 1
    return res / count


def get_title_list(array):
    tmp = []
    for elem in array:
        if abs(elem["top"] - (TITLE_TOP - 50)) < 30:
            if not any(overlap(elem, elem2, tolerence_left=300) for elem2 in tmp):
                tmp.append(elem)
    res = []
    for elem in tmp:
        res.append(elem)
    res = sorted(res, key=lambda x: x["left"])
    return res


def find_clear_box(
    pdf_img, file_output_name, csv, output_type, pdf_file_output=None, num_page=0
):
    mat = fitz.Matrix(6, 6)
    pix = pdf_img.get_pixmap(matrix=mat)
    imgData = pix.tobytes("png")
    nparr = np.frombuffer(imgData, np.uint8)
    open_cv_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    img = open_cv_image[:, :, ::-1].copy()
    img_height, img_width, _ = img.shape
    pytesseract.pytesseract.tesseract_cmd = r"lib\Tesseract-OCR\tesseract"

    dict_ocr = pytesseract.image_to_data(
        img,
        output_type=pytesseract.Output.DICT,
        config="--psm 12 -l fra",
    )

    array_boxe = []

    for i in range(len(dict_ocr["text"])):
        if not dict_ocr["text"][i] == "":
            my_dict = {
                "top": int(dict_ocr["top"][i]),
                "left": int(dict_ocr["left"][i]),
                "width": int(dict_ocr["width"][i]),
                "height": int(dict_ocr["height"][i]),
                "text": dict_ocr["text"][i],
            }

            array_boxe.append(my_dict)

    if len(array_boxe) > 20:
        global TITLE_TOP
        TITLE_TOP = find_title_coord(array_boxe) + 50

        min_scale = get_the_min(array_boxe)
        list_of_title = get_title_list(array_boxe)
        if len(list_of_title) != 5:
            with open("output/log.txt", "a+") as f:
                for eleme in list_of_title:
                    f.write(json.dumps(eleme) + " | ")
                f.write(str(num_page) + "\n")
        # print(TITLE_TOP - 50)
        # print(list_of_title)
        global COLLUMN_TO_LANGUE
        COLLUMN_TO_LANGUE = {
            "français": min_scale,
            "français_tab": min_scale + 200,
            "pije": list_of_title[0]["left"],
            "fwâi": list_of_title[1]["left"],
            "nemi 1 (Temala)": list_of_title[2]["left"],
            "nemi 2 (côte est)": list_of_title[3]["left"],
            "jawe": list_of_title[4]["left"],
        }
        array_boxe = suppr_overlap(array_boxe)
        array_boxe_save = array_boxe.copy()

        first_filter = concat_box(array_boxe, global_compare)
        second_filter = concat_box(first_filter, fr_compare)
        save_overlap = overlap_from_two_array(
            array_base=array_boxe_save, array_clean=second_filter
        )
        triRapide(save_overlap, compare_sort)
        # print(save_overlap)
        if output_type == "img":
            for element in save_overlap:
                img = cv2.rectangle(
                    img,
                    (
                        element["left"],
                        element["top"],
                        element["width"],
                        element["height"],
                    ),
                    (255, 0, 0),
                    2,
                )
            cv2.imwrite(
                file_output_name + ".jpg",
                img,
            )

        save_line_array = from_array_to_line(save_overlap)
        for line in save_line_array.items():
            res = from_line_to_csv(line[1])
            if res != "":
                if output_type == "pdf" and pdf_file_output is not None:
                    pdf_output_width = pdf_file_output[num_page - 1].rect.width
                    pdf_output_height = pdf_file_output[num_page - 1].rect.height
                    for element in line[1]:
                        pdf_file_output[num_page - 1].draw_rect(
                            [
                                (element["left"] * pdf_output_width) / img_width,
                                (element["top"] * pdf_output_height) / img_height,
                                ((element["left"] * pdf_output_width) / img_width)
                                + ((element["width"] * pdf_output_width) / img_width),
                                ((element["top"] * pdf_output_height) / img_height)
                                + (
                                    (element["height"] * pdf_output_height) / img_height
                                ),
                            ],
                            color=(0, 0, 1),
                            width=1,
                        )
                    min_left = min(line[1], key=lambda x: x["left"])
                    min_left_val = (min_left["left"] * pdf_output_width) / img_width
                    min_top = min(line[1], key=lambda x: x["top"])
                    min_top_val = (min_top["top"] * pdf_output_height) / img_height
                    max_width = max(
                        line[1],
                        key=lambda x: (x["left"] + x["width"]) - min_left["left"],
                    )
                    max_width_val = (
                        ((max_width["left"] + max_width["width"])) * pdf_output_width
                    ) / img_width
                    max_height = max(
                        line[1],
                        key=lambda x: (x["top"] + x["height"]) - min_top["top"],
                    )
                    max_height_val = (
                        ((max_height["top"] + max_height["height"])) * pdf_output_height
                    ) / img_height
                    # print(
                    #     [
                    #         min_left_val - 1,
                    #         min_top_val - 1,
                    #         (min_left_val - 1) + max_width_val + 1,
                    #         (min_top_val - 1) + max_height_val + 1,
                    #     ]
                    # )
                    pdf_file_output[num_page - 1].draw_rect(
                        [
                            min_left_val - 1,
                            min_top_val - 1,
                            max_width_val + 1,
                            max_height_val + 1,
                        ],
                        color=(0.8, 0, 0),
                        width=1,
                    )
                csv.write(res + ";" + str(num_page) + "\n")


if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))
    args = get_parser().parse_args()
    file_input = "pdf/" + args.filename
    with open(file_input, "rb") as pdf_file:
        START = 64
        END = 252

        i = 1

        numero_page = args.page
        file_output = "output/" + args.output
        if numero_page != 0:
            file_output += "-" + str(numero_page)

        with open(file_output + ".csv", "w", encoding="utf-8") as file:
            with fitz.open(file_input) as pdf_file:
                if numero_page == 0:
                    with tqdm(total=END - START) as pbar:
                        with fitz.open(file_input) as rectangle_pdf:
                            for page_pdf in pdf_file:
                                if START <= i <= END:
                                    find_clear_box(
                                        page_pdf,
                                        file_output + "-" + str(i),
                                        file,
                                        "pdf",
                                        rectangle_pdf,
                                        i,
                                    )
                                    pbar.update()
                                i += 1
                            rectangle_pdf.save(file_output + ".pdf")
                elif 0 < numero_page < pdf_file.page_count:
                    find_clear_box(
                        pdf_file.load_page(numero_page - 1),
                        file_output,
                        file,
                        "img",
                        num_page=numero_page,
                    )
                else:
                    print("Le numeros de page est en dehors du pdf")
