import os
from sys import api_version

import pytesseract

import PIL

from pdf2image import convert_from_path
import cv2
import numpy

os.chdir(os.path.dirname(__file__))


FILE_NAME = r"full-pdf\hienghene\083.pdf"

pil_img = convert_from_path(FILE_NAME, 500, poppler_path=r"lib\poppler-0.68.0\bin")[0]
open_cv_image = numpy.array(pil_img)
img = open_cv_image[:, :, ::-1].copy()
h, w, _ = img.shape

pytesseract.pytesseract.tesseract_cmd = r"lib\Tesseract-OCR\tesseract"

dict_ocr = pytesseract.image_to_data(
    img, output_type=pytesseract.Output.DICT, config="--psm 12 -l fra"
)


array_boxe = []
# todo coordonnées dynamique


def overlap(elem1, elem2):
    if (
        (elem1["top"] >= elem2["top"] + elem2["height"])
        or (elem1["top"] + elem1["height"] <= elem2["top"])
        or (elem1["left"] + elem1["width"] <= elem2["left"])
        or (elem1["left"] >= elem2["left"] + elem2["width"])
    ):
        return False
    return True


def compare(elem1, elem2, tolerence=1):
    return (
        abs(elem1["top"] - elem2["top"]) < tolerence
        and abs(elem1["left"] - elem2["left"]) < tolerence
    )


def return_index_of_array(array, element):
    for test in array:
        if compare(test, element):
            return array.index(test)


def concat(array, res, element1, element2):
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
    array.append(to_add)
    res.append(to_add)

    try:
        del res[res.index(element2)]
    except:
        print("element2", element2)
    try:
        del res[return_index_of_array(res, element1)]
    except:
        print("element1", element1)


def global_compare(element1, element2, array, approx_top=20, approx_left=50):
    dif_top = element1["top"] - element2["top"]
    dif_left = element1["left"] - (element2["left"] + element2["width"])
    dif_left3 = element2["left"] - (element1["left"] + element1["width"])
    dif_top2 = element1["top"] - (element2["top"] + element2["height"])
    dif_left2 = element1["left"] - element2["left"]
    if (
        1400 < element2["top"] < 1450
        and 1400 < element1["top"] < 1450
        and element2["left"] < 1000
        and element1["left"] < 1000
    ):
        print(element1)
        print(element2)
    return (
        abs(dif_top) < approx_top
        and (abs(dif_left) < approx_left or abs(dif_left3) < approx_left)
        or (
            abs(COLLUMN_TO_LANGUE["français"] - element1["left"]) < approx_left
            and abs(COLLUMN_TO_LANGUE["français"] - element2["left"]) < approx_left
            and abs(dif_top2) < approx_top
            and abs(dif_left2) < approx_left
        )
    )


def get_fr_column(array):
    res = []
    for element in array:
        if (
            abs(element["left"] - COLLUMN_TO_LANGUE["français"]) < 50
            or abs(element["left"] - COLLUMN_TO_LANGUE["français_tab"]) < 50
        ):
            res.append(element)
    return res


def get_most_close_fr(array, element):
    res = array[0]
    fr_array = get_fr_column(array)
    for element_fr in fr_array:
        if abs(element_fr["top"] - element["top"]) < abs(res["top"] - element["top"]):
            res = element_fr
    return res


def fr_compare(element1, element2, array):
    return abs(element2["left"] - element1["left"]) < 200 and compare(
        get_most_close_fr(array, element1), get_most_close_fr(array, element2)
    )


def concat_box(array, func_compare):

    change = True
    while change:
        change = False
        res = []
        for element1 in array:
            if (
                not any(overlap(element1, elem2) for elem2 in res)
                and element1["top"] > 500
            ):
                res.append(element1)
                for element2 in res:
                    if not overlap(element1, element2) and func_compare(
                        element1, element2, array
                    ):
                        change = True
                        concat(array, res, element1, element2)
        array = res

    return res


def get_the_min(array):
    res = 999999999999
    for element in array:
        if element["top"] > 600:
            res = min(res, element["left"])
    return res


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


min_scale = get_the_min(array_boxe)
COLLUMN_TO_LANGUE = {
    "français": min_scale,
    "français_tab": min_scale + 100,
    "pije": 900 + min_scale,
    "fwai": 1500 + min_scale,
    "nemi1": 2100 + min_scale,
    "nemi2": 2700 + min_scale,
    "jawe": 3300 + min_scale,
}

first_filter = concat_box(array_boxe, global_compare)
# for element in first_filter:
#     if "arriv" in element["text"]:
#         print(element)
second_filter = concat_box(first_filter, fr_compare)

for element in second_filter:
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

# show annotated image and wait for keypress
cv2.imwrite(
    "output/output.jpg",
    img,
)
