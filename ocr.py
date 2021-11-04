from PIL import Image
import pytesseract
import sys
from pdf2image import convert_from_path
import os
import re

def cmpY(a, b):
     if (a['yCenter'] <= b['yCenter']):
          return -1
     else:
          return 1

def cmpX(a, b):
     if (a['xMin'] <= b['xMax']):
          return -1
     else:
          return 1

def generate(file, lineHeight = 8, dpi = 500):
     dir_folder_images = "ocr-images"
     results = {}
     pages = convert_from_path(os.path.abspath(os.getcwd()) + '/' + file, dpi)
     image_counter = 1

     lineHeight = int(lineHeight)

     for page in pages:
          results[image_counter] = []
          filename = dir_folder_images + "/page_" + str(image_counter) + ".jpg"
          page.save(filename, 'JPEG')
          
          image_counter = image_counter + 1
          
     for i in range(1, image_counter):
          filename = dir_folder_images + "/page_" + str(i) + ".jpg"
          boxes = pytesseract.image_to_data(Image.open(filename), lang="pol")
          filesize = float(os.path.getsize(filename)) / 1000000 #to mb

          if (filesize > 0.2): #not empty image
               dataPage = []
               for box in boxes.splitlines():
                    row = box.split('\t')
                    # print(row)
                    if (row[2].isdigit()):
                         checkText = re.sub(r'^\s+', '', row[11])
                         if (row[11] != '' and len(checkText) > 0):
                              xMin = float(row[6])
                              xMax = xMin + float(row[8])
                              yMin = float(row[7])
                              yMax = yMin + float(row[9])
                              xCenter = ((xMax - xMin) / 2) + xMin
                              yCenter = ((yMax - yMin) / 2) + yMin
                              obj = {
                                   "x": float(row[6]), 
                                   "y": float(row[7]), 
                                   "width": float(row[8]), 
                                   "height": float(row[9]), 
                                   "text": row[11],
                                   "xCenter": xCenter,
                                   "yCenter": yCenter,
                                   "xMin": xMin,
                                   "xMax": xMax
                              }
                              # print(obj)
                              dataPage.append(obj)

               dataPage.sort(key=lambda b:b['yCenter'], reverse=False)

               values = {}

               for dPage in dataPage:
                    check = False
                    if len(values) > 0:
                         for key, value in values.items():
                              for v in value:
                                   if ((dPage['yCenter'] >= (v['yCenter'] - lineHeight)) and (dPage['yCenter'] <= (v['yCenter'] + lineHeight))):
                                        values[key].append(dPage)
                                        check = True
                                        break
                         if (check == False):
                              lastKey = len(values)
                              values[lastKey] = []
                              values[lastKey].append(dPage)
                    else:
                         values[0] = []
                         values[0].append(dPage)

               if (len(values) > 0):
                    for key, value in values.items():
                         for v in value:
                              values[key].sort(key=lambda b:(b['xMin'], b['xMax']), reverse=False)

               onlyTexts = []
               if (len(values) > 0):
                    for key, value in values.items():
                         text = ""
                         for v in value:
                              text = text + " " + v['text']
                         text = text.strip()
                         onlyTexts.append(text)

               # results[i].append(values)
               results[i] = onlyTexts

          os.remove(filename)
     return results