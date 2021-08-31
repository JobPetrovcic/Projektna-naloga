import os
import io
import pytesseract
pytesseract.pytesseract.tesseract_cmd=r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
from PIL import Image
from wand.image import Image as WandImage

#POZOR: ta funkcija je skopirana iz receiptparser python modula
def ocr_image(input_file, language, sharpen=False):
    """
    :param input_file: str
        Path to image to prettify
    :return: str
    """
    with io.BytesIO() as transfer:
        with WandImage(filename=input_file) as img:
            if sharpen:
                img.auto_level()
                img.sharpen(radius=0, sigma=4.0)
                img.contrast()
            img.save(transfer)

        with Image.open(transfer) as img:
            return pytesseract.image_to_string(img, lang=language)

dovoljeni_formati=('.jpg', '.png')
#NASVET: slika naj bo crno bela, s cim vecjim kontrastom in locljivostjo, račun pa naj bo "svež", saj črnilo s časom zbledi
def dobi_besedilo(ime_datoteke):
    if(isinstance(ime_datoteke, str)):
        #preveri ali je slika pravega formata
        ime, koncnica = os.path.splitext(ime_datoteke)
        if koncnica in dovoljeni_formati:
            try:
                return ocr_image(ime_datoteke, "slv", True).lower().splitlines()
            except:
                raise Exception("Nekaj je šlo narobe pri branju besedila iz slike: "+ime_datoteke)
        else:
            raise ValueError(f"Slika mora biti v {dovoljeni_formati} formatih.")
            
    else:
        raise ValueError("Ime datoteke ni niz.")