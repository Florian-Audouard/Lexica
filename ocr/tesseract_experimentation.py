import os
from sys import api_version

import pytesseract

import PIL

from pdf2image import convert_from_path
import cv2
import numpy

os.chdir(os.path.dirname(__file__))


FILE_NAME = r"full-pdf\hienghene\082.pdf"

pil_img = convert_from_path(FILE_NAME, 500, poppler_path=r"lib\poppler-0.68.0\bin")[0]
open_cv_image = numpy.array(pil_img)
img = open_cv_image[:, :, ::-1].copy()
h, w, _ = img.shape

pytesseract.pytesseract.tesseract_cmd = r"lib\Tesseract-OCR\tesseract"

dict_ocr = pytesseract.image_to_data(
    img, output_type=pytesseract.Output.DICT, config="--psm 4"
)


array_boxe = []


def compare(elem1, elem2):
    if elem1["top"] == elem2["top"] and elem1["left"] == elem2["left"]:
        return True


def return_index_of_array(array, element):
    for test in array:
        if compare(test, element):
            return array.index(test)
    # print(element, array)


def concat_box(array, approx_top=50):
    res = []
    for element1 in array:
        res.append(element1)
        for element2 in res:
            if not compare(element1, element2):
                dif_top = element1["top"] - element2["top"]
                dif_left = element1["left"] - element2["left"]
                if abs(dif_top) < approx_top:
                    if element1["left"] < element2["left"]:
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
                    del res[res.index(element2)]

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


for element in concat_box(array_boxe):
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
