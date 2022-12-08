from pandas import array
import pytesseract
import fitz
import numpy as np
import cv2
import os

os.chdir(os.path.dirname(__file__))


def save_as_img(array, img, file_output_name, num_page):
    for element in array:
        try:
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
        except:
            print(element["left"])
    cv2.imwrite(
        file_output_name + "-" + str(num_page) + ".jpg",
        img,
    )


def test(pdf_img):
    mat = fitz.Matrix(6, 6)
    pix = pdf_img.get_pixmap(matrix=mat)
    img_data = pix.tobytes("png")
    nparr = np.frombuffer(img_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    kernel = np.ones((8, 8), np.floating)
    only_bold = cv2.dilate(img, kernel, iterations=1)
    cv2.imwrite("test.jpg", only_bold)
    img_tess = img
    dict_ocr = pytesseract.image_to_data(
        img_tess,
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
            sub_img = only_bold[
                my_dict["top"] : my_dict["top"] + my_dict["height"],
                my_dict["left"] : my_dict["left"] + my_dict["width"],
            ]
            percent_black_pixel = np.sum(sub_img < 50) / sub_img.size
            my_dict["bold_percent"] = percent_black_pixel
            if my_dict["bold_percent"] > 0.01:
                my_dict["bold"] = True
            else:
                my_dict["bold"] = False
            array_boxe.append(my_dict)
    bold_array = []
    for element in array_boxe:
        if element["bold"]:
            bold_array.append(element)
    save_as_img(bold_array, img, "test_bold", 80)


def get_array_tess(pdf_img):
    mat = fitz.Matrix(6, 6)
    pix = pdf_img.get_pixmap(matrix=mat)
    img_data = pix.tobytes("png")
    nparr = np.frombuffer(img_data, np.uint8)
    open_cv_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    img = open_cv_image[:, :, ::-1].copy()
    img_height, img_width, _ = img.shape
    pytesseract.pytesseract.tesseract_cmd = r"lib\Tesseract-OCR\tesseract"

    dict_ocr = pytesseract.image_to_data(
        img,
        output_type=pytesseract.Output.DICT,
        config="--psm 12 -l fra",
    )
    for index in range(len(dict_ocr["text"])):
        if dict_ocr["conf"][index] < 94:
            print(
                dict_ocr["line_num"][index],
                dict_ocr["text"][index],
                dict_ocr["conf"][index],
            )


file_input = "pdf/le_nyelayu_de_balade.pdf"
with fitz.open(file_input) as rectangle_pdf:
    test(rectangle_pdf.load_page(80))
