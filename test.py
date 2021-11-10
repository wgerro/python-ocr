#!C:\Users\gerro\AppData\Local\Programs\Python\Python39\python.exe

print("Content-Type: text/html; charset=utf-8\n\n")
import ocr
import cgi
import cgitb
import os
import time
import sys
import re
import unicodereplace

sys.stdout.reconfigure(encoding='utf-8')
cgitb.enable()

form = cgi.FieldStorage()
lineheight =  form.getvalue('lineheight')
dpi = form.getvalue('dpi')
psm = form.getvalue('psm')

file = form['file']
dirFolder = 'ocr-uploaded'

if file.filename:
     customFileName = str(round(time.time() * 1000)) + os.path.basename(file.filename)
     fn = dirFolder + "/" + customFileName
     open(fn, 'wb').write(file.file.read())

     results = ocr.generate(fn, lineheight, dpi, psm, False)

     insurance = ""

     dataPolicy = {}
     params = {
          "number_policy": "", 
          "start_date": "", 
          "end_date": "", 
          "vehicle": "", 
          "amount": "",
          "images": []
     }

     for key, result in results.items():
          
          for r in result['texts']:
               if len(re.findall(r'warta', r.lower())) > 0:
                    insurance = "WARTA"
                    break
               elif len(re.findall(r'ergo', r.lower())) > 0:
                    insurance = "ERGO"
                    break

          number_policy = 0
          # print(insurance)
          if insurance == "WARTA":
               for r in result['texts']:
                    if len(re.findall(r'(POLISA[\s]NR).*([0-9]{12,13})', r.upper())) > 0 or len(re.findall(r'(POTWIERDZENIE.*ASSIST).*([0-9]{12,13})', r.upper())) > 0:
                         number_policy = re.findall(r'([0-9]{12,13})', r.upper())[0]
                         if (number_policy not in dataPolicy):
                              dataPolicy[number_policy] = params.copy()
                              dataPolicy[number_policy]['number_policy'] = number_policy
                         
                    
                    if number_policy in dataPolicy:
                         if dataPolicy[number_policy]['start_date'] == "" and dataPolicy[number_policy]['end_date'] == "":
                              if len(re.findall(r'(OKRES.*OC).*([0-9]{4}-[0-9]{2}-[0-9]{2}).*([0-9]{4}-[0-9]{2}-[0-9]{2})$', r.upper())) > 0:
                                   dataPolicy[number_policy]['start_date'] = re.findall(r'(OKRES.*OC).*([0-9]{4}-[0-9]{2}-[0-9]{2}).*([0-9]{4}-[0-9]{2}-[0-9]{2})$', r.upper())[0][1]
                                   dataPolicy[number_policy]['end_date'] = re.findall(r'(OKRES.*OC).*([0-9]{4}-[0-9]{2}-[0-9]{2}).*([0-9]{4}-[0-9]{2}-[0-9]{2})$', r.upper())[0][2]
                              elif len(re.findall(r'(OC).*([0-9]{4}-[0-9]{2}-[0-9]{2}).*([0-9]{4}-[0-9]{2}-[0-9]{2})', r.upper())) > 0:
                                   dataPolicy[number_policy]['start_date'] = re.findall(r'(OC).*([0-9]{4}-[0-9]{2}-[0-9]{2}).*([0-9]{4}-[0-9]{2}-[0-9]{2})', r.upper())[0][1]
                                   dataPolicy[number_policy]['end_date'] = re.findall(r'(OC).*([0-9]{4}-[0-9]{2}-[0-9]{2}).*([0-9]{4}-[0-9]{2}-[0-9]{2})', r.upper())[0][2]
                              

                         if dataPolicy[number_policy]['vehicle'] == "":
                              if len(re.findall(r'(REJESTRACYJNY[\s\:\"\=]+)([A-Z\w]{2,3}[\s]?[A-Z0-9]{4,5})', r.upper())) > 0:
                                   dataPolicy[number_policy]['vehicle'] = unicodereplace.generate((re.findall(r'(REJESTRACYJNY[\s\:\"\=]+)([A-Z\w]{2,3}[\s]?[A-Z0-9]{4,5})', r.upper())[0][1]).replace(' ', ''), 'PL')

                         if dataPolicy[number_policy]['amount'] == "":
                              if len(re.findall(r'(SKŁADKA OC[\s\W]+)([0-9\.\,]+)([\s]ZŁ)', r.upper())) > 0:
                                   dataPolicy[number_policy]['amount'] = (re.findall(r'(SKŁADKA OC[\s\W]+)([0-9\.\,]+)([\s]ZŁ)', r.upper())[0][1]).replace('.','').replace(',','.')
                              elif len(re.findall(r'(SKŁADKA.*KWOTA[\s\:]+)(.*)(ZŁ)', r.upper())) > 0:
                                   dataPolicy[number_policy]['amount'] = (re.findall(r'(SKŁADKA.*KWOTA[\s\:]+)(.*)(ZŁ)', r.upper())[0][1]).replace('.','').replace(',','.')
          elif insurance == "ERGO":
               for r in result['texts']:
                    if len(re.findall(r'(NUMER CERTYFIKATU|CERTIFICATE NUMBER).*([0-9]{12,13})', r.upper())) > 0:
                         number_policy = re.findall(r'([0-9]{12,13})', r.upper())[0]
                         if (number_policy not in dataPolicy):
                              dataPolicy[number_policy] = params.copy()
                              dataPolicy[number_policy]['number_policy'] = number_policy

                    if number_policy in dataPolicy:
                         if dataPolicy[number_policy]['start_date'] == "" and dataPolicy[number_policy]['end_date'] == "":
                              if len(re.findall(r'([0-9]{2}-[0-9]{2}-[0-9]{4}).*([0-9]{2}-[0-9]{2}-[0-9]{4})', r.upper())) > 0:
                                   s_date = (re.findall(r'([0-9]{2}-[0-9]{2}-[0-9]{4}).*([0-9]{2}-[0-9]{2}-[0-9]{4})', r.upper())[0][0]).split('-')
                                   e_date = (re.findall(r'([0-9]{2}-[0-9]{2}-[0-9]{4}).*([0-9]{2}-[0-9]{2}-[0-9]{4})', r.upper())[0][1]).split('-')
                                   dataPolicy[number_policy]['start_date'] = str(s_date[2]) + '-' + str(s_date[1]) + '-' + str(s_date[0])
                                   dataPolicy[number_policy]['end_date'] = str(e_date[2]) + '-' + str(e_date[1]) + '-' + str(e_date[0])

                         if dataPolicy[number_policy]['vehicle'] == "":
                              if len(re.findall(r'^([A-Z]{2,3}[\s]?[A-Z0-9]{4,5})', r)) > 0 and len(re.findall(r'(HESTIA)', r.upper())) == 0:
                                   dataPolicy[number_policy]['vehicle'] = unicodereplace.generate((re.findall(r'^([A-Z]{2,3}[\s]?[A-Z0-9]{4,5})', r.upper())[0]).replace(' ', ''), 'PL')

                         if dataPolicy[number_policy]['amount'] == "":
                              if len(re.findall(r'([\w\,\.]+)\s(ZŁ)', r.upper())) > 0:
                                   dataPolicy[number_policy]['amount'] = (re.findall(r'([\w\,\.]+)\s(ZŁ)', r.upper())[0][0]).replace('.','').replace(',','.')
          elif insurance == "COMPENSA":
               print('ERGO')

          if (number_policy in dataPolicy):
               dataPolicy[number_policy]['images'].append(result['filename'])
                              

     print("<pre>")
     for data in dataPolicy.values():
          print(data)
          if (data['start_date'] != '' and data['end_date'] != '' and data['vehicle'] != ''):
               ocr.saveFilePDF(data['images'], data['number_policy'] + '-' + data['start_date'] + '-' + data['end_date'] + '-' + data['vehicle'])
     print("</pre>")                    
     
     for key, result in results.items():
          i = 0
          print("<div style='background: #f3f3f3;padding-bottom: 20px;'><b style='font-size: 18px;padding-left:5px;padding-top:5px;'>Page nr: " + str(key) + "</b>") 
          print("<pre>")
          for r in result['texts']:
               print("     [" + str(i) + "] => " + r + "")
               i = i + 1
          print("</pre></div>")

     os.remove(fn)



# ocr.generate('test.pdf')