from PIL import Image
import pytesseract
import sys
from pdf2image import convert_from_path
import os
import re
import mimetypes
import numpy as np 
import cv2

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

def generate(file, lineHeight = 8, dpi = 200, psm = 6, removeFile = True):
     dir_folder_images = "ocr-images"

     if not os.path.exists(dir_folder_images):
          os.makedirs(dir_folder_images)

     results = {}
     image_counter = 1
     config_txt = '--oem 3 --psm ' + str(psm)
     lineHeight = int(lineHeight)
     
     mimetype = mimetypes.guess_type(os.path.abspath(os.getcwd()) + '/' + file)[0] # 'application/pdf'

     if (mimetype == "application/pdf"):
          pages = convert_from_path(os.path.abspath(os.getcwd()) + '/' + file, dpi)
          for page in pages:
               results[image_counter] = []
               filename = dir_folder_images + "/page_" + str(image_counter) + ".jpg"
               pages = Image.fromarray(imageSkew(np.array(page)))
               pages.save(filename, 'JPEG')
               image_counter = image_counter + 1
     else:
          filename = dir_folder_images + "/page_" + str(image_counter) + ".jpg"
          img = Image.fromarray(imageSkew(file, True))
          img.save(filename, "JPEG", quality=100, optimize=True, progressive=True)
          image_counter = 2

          
     for i in range(1, image_counter):
          filename = dir_folder_images + "/page_" + str(i) + ".jpg"
          
          boxes = pytesseract.image_to_data(Image.open(filename), lang="pol", config=config_txt)
          filesize = float(os.path.getsize(filename)) / 1000000 #to mb
          emptyPage = False
          onlyTexts = []
          
          # if (filesize < 0.15):
          #      emptyPage = True

          if (emptyPage == False): #not empty image
               dataPage = []
               for box in boxes.splitlines():
                    row = box.split('\t')
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

               
               if (len(values) > 0):
                    for key, value in values.items():
                         text = ""
                         for v in value:
                              text = text + " " + v['text']
                         text = text.strip()
                         onlyTexts.append(text)

               # results[i].append(values)
          results[i] = {'page': i, 'filename': filename, 'empty': emptyPage, 'texts': []}
          results[i]['texts'] = onlyTexts

          if removeFile:
               os.remove(filename)
     return results

def imageSkew(image, isPath = False):
     if isPath:
          image = cv2.imread(image)
          
     gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
     gray = cv2.bitwise_not(gray)
     blur = cv2.GaussianBlur(gray,(5,5),0)
     thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

     coords = np.column_stack(np.where(thresh > 0))
     angle = cv2.minAreaRect(coords)[-1]

     if angle < -45:
          angle = -(90 + angle)
     else:
          angle = -angle

     (h, w) = image.shape[:2]
     center = (w // 2, h // 2)
     M = cv2.getRotationMatrix2D(center, angle, 1.0)
     rotatedImage = cv2.warpAffine(image, M, (w, h),
          flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

     return rotatedImage

def saveFilePDF(images, title):
     title = title.replace('/', '')

     if len(images) == 0:
          return 

     dirUploaded = 'ocr-saved'

     if not os.path.exists(dirUploaded):
          os.makedirs(dirUploaded)

     listImages = []
     for image in images:
          im = Image.open(image)
          listImages.append(im)

     if len(listImages) > 1:
          copyImages = listImages.copy()
          copyImages.pop(0)
          listImages[0].save(dirUploaded + '/' + str(title) + '.pdf', 'PDF', resolution=100.00, save_all=True, append_images=copyImages)
     else: 
          listImages[0].save(dirUploaded + '/' + str(title) + '.pdf', 'PDF', resolution=100.00, save_all=True)

     return dirUploaded + '/' + str(title) + '.pdf'