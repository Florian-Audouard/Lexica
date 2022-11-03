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

dict_ocr = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)


array_boxe = []


def concat_boxe(array_boxe_func, dict_test, index_dict, aprox_x=50, aprox_y=10):
    for index, element_boxe in enumerate(array_boxe_func):
        if not index == index_dict:
            space_horizontal_between = abs(
                dict_test["left"] - (element_boxe["left"] + element_boxe["width"])
            )
            space_vertical_between = abs(
                dict_test["top"] - (element_boxe["top"] + element_boxe["height"])
            )
            if element_boxe["text"] in "aller" and dict_test["text"] in "(déplacement":
                print("dict test", dict_test)
                print("element_boxe", element_boxe)
            if space_horizontal_between < aprox_x and space_vertical_between < aprox_y:
                array_boxe_func.pop(index)
                array_boxe_func.pop(index_dict)
                array_boxe_func.append(
                    {
                        "top": min(dict_test["top"], element_boxe["top"]),
                        "left": min(dict_test["left"], element_boxe["left"]),
                        "width": element_boxe["width"]
                        + dict_test["width"]
                        + space_horizontal_between,
                        "height": element_boxe["height"]
                        + dict_test["height"]
                        + space_vertical_between,
                        "text": dict_test["text"] + " " + element_boxe["text"],
                    }
                )

                return (array_boxe_func, True)
    return (array_boxe_func, False)


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


test = True
while test:
    for index_recur, element_recur in enumerate(array_boxe):
        array_boxe, test = concat_boxe(array_boxe, element_recur, index_recur)


for element in array_boxe:
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
