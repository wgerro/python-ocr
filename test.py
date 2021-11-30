#!/usr/bin/python3

import ocr
import cgi
import cgitb
import os
import time
import sys
import re
import unicodereplace
import json
import mimetypes

cgitb.enable()
# print(os.environ.keys())

allows_url = ['https://localhost', 'https://erp.avenir-as.pl', 'https://erp.avenir-as.pl/', 'http://192.168.1.42/', 'http://192.168.1.42', '192.168.1.42', 'https://api.avenir-as.pl/', 'https://api.avenir-as.pl', 'https://avenir-as.pl', 'https://avenir-as.pl/']

print("Access-Control-Allow-Headers: *")
print("Access-Control-Allow-Methods: *")

if 'HTTP_ORIGIN' not in os.environ.keys():
     print("Content-Type: text/html; charset=utf-8\n\n")
     print('403 Forbidden')
     exit()

if os.environ['HTTP_ORIGIN'] not in allows_url:
     print("Content-Type: text/html; charset=utf-8\n\n")
     print('403 Forbidden')
     exit()
else:
     print("Access-Control-Allow-Origin: *")

if os.environ['REQUEST_METHOD'] != 'POST':
     print("Content-Type: text/html; charset=utf-8\n\n")
     print('403 Forbidden')
     exit()
     
print("Content-Type: text/html; charset=utf-8\n\n")
     
form = cgi.FieldStorage()
lineheight =  form.getvalue('lineheight')
dpi = form.getvalue('dpi')
psm = form.getvalue('psm')
islog = form.getvalue('islog')

file = form['file']
dirFolder = 'ocr-uploaded'

mimetype = mimetypes.guess_type(file.filename)[0] # 'application/pdf', 'image/jpeg'
mimetypes_allows = ['image/jpeg', 'application/pdf']

if mimetype in mimetypes_allows:
     customFileName = str(round(time.time() * 1000)) + os.path.basename(file.filename)

     if not os.path.exists(dirFolder):
          os.makedirs(dirFolder)

     fn = dirFolder + "/" + customFileName
     open(fn, 'wb').write(file.file.read())

     results = ocr.generate(fn, lineheight, dpi, psm, False)

     insurance = ""
     insurer_kind = ""
     insurer_type = ""
     insurer_type_id = 0
                         
     dataPolicy = {}
     params = {
          "number_policy": "", 
          "start_date": "", 
          "end_date": "", 
          "vehicle": "", 
          "vehicle_type": "", 
          "vehicle_type_id": "",
          "vehicle_vin": "",
          "amount": "",
          "file_url": "",
          "insurer": "",
          "insurer_type": "",
          "insurer_type_id": "",
          "insurer_kind": "",
          "payment_deadline": "",
          "account_number": "",
          "images": [],
          "client_name": "",
          "client_address": "",
          "client_regon": "",
          "client_nip": "",
          "client_pesel": "",
     }
     
     typesInsurances = {1: 'KOMUNIKACYJNA', 2: 'ŻYCIE', 3: 'NIERUCHOMOŚĆ', 4: 'PODRÓŻ', 5: 'KORPORACJA'}
     kindInsurances = {'OC': 1, 'NWW': 1, 'AC': 1, 'WMA': 1, 'UBEZPIECZENIE MASZYN I URZĄDZEŃ OD WSZYSTKICH RYZYK': 5, 'TRAVEL': 4, 'DOM': 3, 'EKSTRABIZNES PLUS': 3, 'MTPL': 1, 'MOTOR THIRD PART LIABILITY': 1}
     
     typesVehicles = {         
          1: "CIĄGNIK SIODŁOWY",
          2: "CIĘŻAROWY DO 3.5 TONY",
          3: "CIĘŻAROWY",
          4: "KOPARKA",
          5: "MOTOCYKL",
          6: "MOTOROWER",
          7: "NACZEPA",
          8: "POJAZD INNY",
          9: "POJAZD SPECJALNY",
          10: "POJAZD WOLNOBIEŻNY",
          11: "PRZYCZEPA",
          12: "QUAD",
          13: "SAMOCHÓD OSOBOWY",
          14: "TRAKTOR",
          15: "WALEC",
          16: "WÓZEK WIDŁOWY",
          17: "ZŁOM",
          18: "BUS",
          19: "OSOBOWY"
     }

     for key, result in results.items():
          
          for r in result['texts']:
               if (len(insurance) == 0):
                    if len(re.findall(r'warta', r.lower())) > 0:
                         insurance = "WARTA"
                    elif len(re.findall(r'ergo', r.lower())) > 0:
                         insurance = "ERGO"
                    elif len(re.findall(r'compensa', r.lower())) > 0:
                         insurance = "COMPENSA"
               
               if (insurer_type_id == 0):
                    for kKey, kItem in kindInsurances.items():
                         if len(re.findall(rf"(\s{kKey}\s)", r.upper())) > 0:
                              insurer_kind = kKey
                              insurer_type = typesInsurances[kItem] 
                              insurer_type_id = kItem
                         elif len(re.findall(rf"(^{kKey}$)", r.upper())) > 0:
                              insurer_kind = kKey
                              insurer_type = typesInsurances[kItem] 
                              insurer_type_id = kItem
                         elif len(re.findall(rf"(\({kKey}\))", r.upper())) > 0:
                              insurer_kind = kKey
                              insurer_type = typesInsurances[kItem] 
                              insurer_type_id = kItem
                         elif len(re.findall(rf"(^{kKey})", r.upper())) > 0:
                              insurer_kind = kKey
                              insurer_type = typesInsurances[kItem] 
                              insurer_type_id = kItem
               
               if (len(insurance) > 0 and insurer_type_id > 0):
                    break
                         
          number_policy = 0
          
          if insurance == "WARTA":
               for r in result['texts']:
                    if len(re.findall(r'(POLISA[\s]NR).*([0-9]{12,13})', r.upper())) > 0 or len(re.findall(r'(POTWIERDZENIE.*ASSIST).*([0-9]{12,13})', r.upper())) > 0 or len(re.findall(r'(POLISY[\s]NR).*([0-9]{12,13})', r.upper())) > 0 or len(re.findall(r'(WNIOSEK-POLISA.*NR[\s\:]+)(.*)', r.upper())) > 0 or len(re.findall(r'^(\d{11,13})\/[A-Z0-9]+\/[A-Z0-9]+', r)) > 0:
                         if len(re.findall(r'^(\d{11,13})\/[A-Z0-9]+\/[A-Z0-9]+', r)) > 0:
                              number_policy = re.findall(r'^([0-9]{12,13})', r.upper())[0]
                         else:
                              number_policy = re.findall(r'([0-9]{12,13})', r.upper())[0]

                         if (number_policy not in dataPolicy):
                              dataPolicy[number_policy] = params.copy()
                              dataPolicy[number_policy]['images'] = []
                              dataPolicy[number_policy]['number_policy'] = number_policy
                              dataPolicy[number_policy]['insurer'] = insurance
                              dataPolicy[number_policy]['insurer_kind'] = insurer_kind
                              dataPolicy[number_policy]['insurer_type'] = insurer_type
                              dataPolicy[number_policy]['insurer_type_id'] = insurer_type_id
                         
                    
                    if number_policy in dataPolicy:
                         if dataPolicy[number_policy]['start_date'] == "" and dataPolicy[number_policy]['end_date'] == "":
                              if len(re.findall(r'(OKRES.*OC).*([0-9]{4}-[0-9]{2}-[0-9]{2}).*([0-9]{4}-[0-9]{2}-[0-9]{2})$', r.upper())) > 0:
                                   dataPolicy[number_policy]['start_date'] = re.findall(r'(OKRES.*OC).*([0-9]{4}-[0-9]{2}-[0-9]{2}).*([0-9]{4}-[0-9]{2}-[0-9]{2})$', r.upper())[0][1]
                                   dataPolicy[number_policy]['end_date'] = re.findall(r'(OKRES.*OC).*([0-9]{4}-[0-9]{2}-[0-9]{2}).*([0-9]{4}-[0-9]{2}-[0-9]{2})$', r.upper())[0][2]
                              elif len(re.findall(r'(OC).*([0-9]{4}-[0-9]{2}-[0-9]{2}).*([0-9]{4}-[0-9]{2}-[0-9]{2})', r.upper())) > 0:
                                   dataPolicy[number_policy]['start_date'] = re.findall(r'(OC).*([0-9]{4}-[0-9]{2}-[0-9]{2}).*([0-9]{4}-[0-9]{2}-[0-9]{2})', r.upper())[0][1]
                                   dataPolicy[number_policy]['end_date'] = re.findall(r'(OC).*([0-9]{4}-[0-9]{2}-[0-9]{2}).*([0-9]{4}-[0-9]{2}-[0-9]{2})', r.upper())[0][2]
                              elif len(re.findall(r'(OKRES\sUBEZP).*([0-9]{4}-[0-9]{2}-[0-9]{2}).*([0-9]{4}-[0-9]{2}-[0-9]{2})$', r.upper())) > 0:
                                   dataPolicy[number_policy]['start_date'] = re.findall(r'(OKRES\sUBEZP).*([0-9]{4}-[0-9]{2}-[0-9]{2}).*([0-9]{4}-[0-9]{2}-[0-9]{2})$', r.upper())[0][1]
                                   dataPolicy[number_policy]['end_date'] = re.findall(r'(OKRES\sUBEZP).*([0-9]{4}-[0-9]{2}-[0-9]{2}).*([0-9]{4}-[0-9]{2}-[0-9]{2})$', r.upper())[0][2]
                              elif len(re.findall(r'(PODRÓŻY|TRAVEL).*(\d{4}-\d{2}-\d{2}).*(\d{4}-\d{2}-\d{2})', r.upper())) > 0:
                                   dataPolicy[number_policy]['start_date'] = re.findall(r'(PODRÓŻY|TRAVEL).*(\d{4}-\d{2}-\d{2}).*(\d{4}-\d{2}-\d{2})', r.upper())[0][1]
                                   dataPolicy[number_policy]['end_date'] = re.findall(r'(PODRÓŻY|TRAVEL).*(\d{4}-\d{2}-\d{2}).*(\d{4}-\d{2}-\d{2})', r.upper())[0][2]
                              elif len(re.findall(r'(OD).*([0-9]{4}-[0-9]{2}-[0-9]{2}).*([0-9]{4}-[0-9]{2}-[0-9]{2})', r.upper())) > 0 and len(re.findall(r'(OD).*(DO)', r.upper())) > 0:
                                   dataPolicy[number_policy]['start_date'] = re.findall(r'(OD).*([0-9]{4}-[0-9]{2}-[0-9]{2}).*([0-9]{4}-[0-9]{2}-[0-9]{2})', r.upper())[0][1]
                                   dataPolicy[number_policy]['end_date'] = re.findall(r'(OD).*([0-9]{4}-[0-9]{2}-[0-9]{2}).*([0-9]{4}-[0-9]{2}-[0-9]{2})', r.upper())[0][2]
                              

                         if dataPolicy[number_policy]['vehicle'] == "":
                              if len(re.findall(r'(REJESTRACYJNY[\s\:\"\=]+)([A-Z\w]{2,3}[\s]?[A-Z0-9]{4,5})', r.upper())) > 0:
                                   dataPolicy[number_policy]['vehicle'] = unicodereplace.generate((re.findall(r'(REJESTRACYJNY[\s\:\"\=]+)([A-Z\w]{2,3}[\s]?[A-Z0-9]{4,5})', r.upper())[0][1]).replace(' ', ''), 'PL')

                         if dataPolicy[number_policy]['amount'] == "":
                              if len(re.findall(r'(SKŁADKA OC[\s\W]+)([0-9\.\,]+)([\s]ZŁ)', r.upper())) > 0:
                                   dataPolicy[number_policy]['amount'] = (re.findall(r'(SKŁADKA OC[\s\W]+)([0-9\.\,]+)([\s]ZŁ)', r.upper())[0][1]).replace('.','').replace(',','.').replace(' ','')
                              elif len(re.findall(r'(SKŁADKA\s.*CZNA\s)(.*)(ZŁ)', r.upper())) > 0:
                                   dataPolicy[number_policy]['amount'] = (re.findall(r'(SKŁADKA\s.*CZNA\s)(.*)(ZŁ)', r.upper())[0][1]).replace('.','').replace(',','.').replace(' ','')
                              elif len(re.findall(r'(SKŁADKA.*KWOTA[\s\:]+)(.*)(ZŁ)', r.upper())) > 0:
                                   dataPolicy[number_policy]['amount'] = (re.findall(r'(SKŁADKA.*KWOTA[\s\:]+)(.*)(ZŁ)', r.upper())[0][1]).replace('.','').replace(',','.').replace(' ','')
                              elif len(re.findall(r'(SKŁADKA\sW\sKWOCIE[\s]+)(.*)(ZŁ)', r.upper())) > 0 and len(re.findall(r'(BEZSK)', r.upper())) == 0:
                                   dataPolicy[number_policy]['amount'] = (re.findall(r'(SKŁADKA\sW\sKWOCIE[\s]+)(.*)(ZŁ)', r.upper())[0][1]).replace('.','').replace(',','.').replace(' ','')
                         
                         if dataPolicy[number_policy]['account_number'] == "":
                              if len(re.findall(r'(PRZELEW).*([\s\d]{32})$', r.upper())) > 0:
                                   dataPolicy[number_policy]['account_number'] = (re.findall(r'(PRZELEW).*([\s\d]{32})$', r.upper())[0][1]).replace(' ', '')
                              elif len(re.findall(r'(SKŁADKA.*PRZELEW).*([\s\d]{32})', r.upper())) > 0:
                                   dataPolicy[number_policy]['account_number'] = (re.findall(r'(SKŁADKA.*PRZELEW).*([\s\d]{32})', r.upper())[0][1]).replace(' ', '')
                              elif len(re.findall(r'(PRZELEW).*([\s\d]{26,32})$', r.upper())) > 0:
                                   dataPolicy[number_policy]['account_number'] = (re.findall(r'(PRZELEW).*([\s\d]{26,32})$', r.upper())[0][1]).replace(' ', '')
                                   
                         if dataPolicy[number_policy]['payment_deadline'] == "":
                              if len(re.findall(r'(TERMIN\sPŁATNOŚCI).*(\d{4}-\d{2}-\d{2})', r.upper())) > 0:
                                   dataPolicy[number_policy]['payment_deadline'] = re.findall(r'(TERMIN\sPŁATNOŚCI).*(\d{4}-\d{2}-\d{2})', r.upper())[0][1]
                              elif len(re.findall(r'(SKŁADKA.*PRZELEW).*(\d{4}-\d{2}-\d{2})', r.upper())) > 0:
                                   dataPolicy[number_policy]['payment_deadline'] = re.findall(r'(SKŁADKA.*PRZELEW).*(\d{4}-\d{2}-\d{2})', r.upper())[0][1]
                         
                         if dataPolicy[number_policy]['client_name'] == "":
                              if len(re.findall(r'(NAZWISKO.*NAZWA[\s\:]+)(.*)', r.upper())) > 0:
                                   dataPolicy[number_policy]['client_name'] = re.findall(r'(NAZWISKO.*NAZWA[\s\:]+)(.*)', r.upper())[0][1]
                              elif len(re.findall(r'([A-Z\s]+)(PESEL[\W]+\d{11})', r.upper())) > 0:
                                   dataPolicy[number_policy]['client_name'] = re.findall(r'([A-Z\s]+)(PESEL[\W]+\d{11})', r.upper())[0][0]
                              
                         
                         if dataPolicy[number_policy]['client_address'] == "":
                              if len(re.findall(r'(ADRES.*\:)(.*)(!?ADRES)', r.upper())) > 0:
                                   dataPolicy[number_policy]['client_address'] = re.findall(r'(ADRES.*\:)(.*)(!?ADRES)', r.upper())[0][1]
                              elif len(re.findall(r'(ADRES.*\:)(.*)', r.upper())) > 0:
                                   dataPolicy[number_policy]['client_address'] = re.findall(r'(ADRES.*\:)(.*)', r.upper())[0][1]
                              elif len(re.findall(r'(SIEDZIBA.*\:)(.*)', r.upper())) > 0:
                                   dataPolicy[number_policy]['client_address'] = re.findall(r'(SIEDZIBA.*\:)(.*)', r.upper())[0][1]
                         
                         if dataPolicy[number_policy]['client_pesel'] == "":
                              if len(re.findall(r'(PESEL[\W]+)(\d{11})', r.upper())) > 0:
                                   dataPolicy[number_policy]['client_pesel'] = re.findall(r'(PESEL[\W]+)(\d{11})', r.upper())[0][1]
                                   
                         if dataPolicy[number_policy]['client_nip'] == "" and dataPolicy[number_policy]['client_pesel'] == "":
                              if len(re.findall(r'(NIP[\s\:]+)(\d{10})', r.upper())) > 0:
                                   dataPolicy[number_policy]['client_nip'] = re.findall(r'(NIP[\s\:]+)(\d{10})', r.upper())[0][1]
                                   
                         if dataPolicy[number_policy]['client_regon'] == "" and dataPolicy[number_policy]['client_pesel'] == "":
                              if len(re.findall(r'(REGON[\s\:]+)(\d{9})', r.upper())) > 0 and len(re.findall(r'(BANK)', r.upper())) == 0:
                                   dataPolicy[number_policy]['client_regon'] = re.findall(r'(REGON[\s\:]+)(\d{9})', r.upper())[0][1]
                              elif len(re.findall(r'(REGON.*)(\d{9})', r.upper())) > 0 and len(re.findall(r'(BANK)', r.upper())) == 0:
                                   dataPolicy[number_policy]['client_regon'] = re.findall(r'(REGON.*)(\d{9})', r.upper())[0][1]
                         
                         if dataPolicy[number_policy]['vehicle_vin'] == "":
                              if len(re.findall(r'(VIN).*([\w\S]{17})', r.upper())) > 0:
                                   dataPolicy[number_policy]['vehicle_vin'] = re.findall(r'(VIN).*([\w\S]{17})', r.upper())[0][1]
                                   
                         if dataPolicy[number_policy]['vehicle_type'] == "":
                              if len(re.findall(r'(RODZAJ[\W]+)', r.upper())) > 0:
                                   for vKey, vItem in typesVehicles.items():
                                        if len(re.findall(rf"{vItem}", r.upper())) > 0:
                                             dataPolicy[number_policy]['vehicle_type'] = vItem
                                             dataPolicy[number_policy]['vehicle_type_id'] = vKey
                                             break
                              else:
                                   for vKey, vItem in typesVehicles.items():
                                        if len(re.findall(rf"({vItem}\))", r.upper())) > 0:
                                             dataPolicy[number_policy]['vehicle_type'] = vItem
                                             dataPolicy[number_policy]['vehicle_type_id'] = vKey
                                             break
                                   
                                 
                                 
                                 
                                   
          elif insurance == "ERGO":
               for r in result['texts']:
                    if len(re.findall(r'(NUMER CERTYFIKATU|CERTIFICATE NUMBER).*([0-9]{12,13})', r.upper())) > 0:
                         number_policy = re.findall(r'([0-9]{12,13})', r.upper())[0]
                         if (number_policy not in dataPolicy):
                              dataPolicy[number_policy] = params.copy()
                              dataPolicy[number_policy]['images'] = []
                              dataPolicy[number_policy]['number_policy'] = number_policy
                              dataPolicy[number_policy]['insurer'] = insurance
                              dataPolicy[number_policy]['insurer_kind'] = insurer_kind
                              dataPolicy[number_policy]['insurer_type'] = insurer_type
                              dataPolicy[number_policy]['insurer_type_id'] = insurer_type_id

                    if number_policy in dataPolicy:
                         if dataPolicy[number_policy]['start_date'] == "" and dataPolicy[number_policy]['end_date'] == "":
                              if len(re.findall(r'([0-9]{2}-[0-9]{2}-[0-9]{4}).*([0-9]{2}-[0-9]{2}-[0-9]{4})', r.upper())) > 0:
                                   s_date = (re.findall(r'([0-9]{2}-[0-9]{2}-[0-9]{4}).*([0-9]{2}-[0-9]{2}-[0-9]{4})', r.upper())[0][0]).split('-')
                                   e_date = (re.findall(r'([0-9]{2}-[0-9]{2}-[0-9]{4}).*([0-9]{2}-[0-9]{2}-[0-9]{4})', r.upper())[0][1]).split('-')
                                   dataPolicy[number_policy]['start_date'] = str(s_date[2]) + '-' + str(s_date[1]) + '-' + str(s_date[0])
                                   dataPolicy[number_policy]['end_date'] = str(e_date[2]) + '-' + str(e_date[1]) + '-' + str(e_date[0])
                         # (USER.*NAME\s)(.*)
                         if dataPolicy[number_policy]['vehicle'] == "":
                              if len(re.findall(r'^([A-Z]{2,3}[\s]?[A-Z0-9]{4,5})', r)) > 0 and len(re.findall(r'(HESTIA)', r.upper())) == 0:
                                   dataPolicy[number_policy]['vehicle'] = unicodereplace.generate((re.findall(r'^([A-Z]{2,3}[\s]?[A-Z0-9]{4,5})', r.upper())[0]).replace(' ', ''), 'PL')
                                   
                         if dataPolicy[number_policy]['client_name'] == "":
                              if len(re.findall(r'(USER.*NAME\s)(.*)', r.upper())) > 0:
                                   dataPolicy[number_policy]['client_name'] = re.findall(r'(USER.*NAME\s)(.*)', r.upper())[0][1]
                         
                         if dataPolicy[number_policy]['client_address'] == "":
                              if len(re.findall(r'(USER.*ADDRESS\s)(.*)', r.upper())) > 0:
                                   dataPolicy[number_policy]['client_address'] = re.findall(r'(USER.*ADDRESS\s)(.*)', r.upper())[0][1]
                                   
                         if dataPolicy[number_policy]['vehicle_vin'] == "":
                              if len(re.findall(r'^([A-Z]{2,3}[\s]?[A-Z0-9]{4,5})[\s]([\w\S]{17})', r.upper())) > 0:
                                   dataPolicy[number_policy]['vehicle_vin'] = re.findall(r'^([A-Z]{2,3}[\s]?[A-Z0-9]{4,5})[\s]([\w\S]{17})', r.upper())[0][1]
                                   
                         if dataPolicy[number_policy]['vehicle_type'] == "":
                              if len(re.findall(r'(DANE\sPOJAZDU[\W]+)', r.upper())) > 0:
                                   for vKey, vItem in typesVehicles.items():
                                        if len(re.findall(rf"{vItem}", r.upper())) > 0:
                                             dataPolicy[number_policy]['vehicle_type'] = vItem
                                             dataPolicy[number_policy]['vehicle_type_id'] = vKey
                                             break

                         if dataPolicy[number_policy]['amount'] == "":
                              if len(re.findall(r'([\w\,\.]+)\s(ZŁ)', r.upper())) > 0:
                                   dataPolicy[number_policy]['amount'] = (re.findall(r'([\w\,\.]+)\s(ZŁ)', r.upper())[0][0]).replace('.','').replace(',','.')
                    prev_text = r
          elif insurance == "COMPENSA":
               for r in result['texts']:
                    if len(re.findall(r'(\d{4,6}\/\d{6,7})', r.upper())) > 0:
                         number_policy = re.findall(r'(\d{4,6}\/\d{6,7})', r.upper())[0]
                         if (number_policy not in dataPolicy):
                              dataPolicy[number_policy] = params.copy()
                              dataPolicy[number_policy]['images'] = []
                              dataPolicy[number_policy]['number_policy'] = number_policy
                              dataPolicy[number_policy]['insurer'] = insurance
                              dataPolicy[number_policy]['insurer_kind'] = insurer_kind
                              dataPolicy[number_policy]['insurer_type'] = insurer_type
                              dataPolicy[number_policy]['insurer_type_id'] = insurer_type_id

                    if number_policy in dataPolicy:
                         if dataPolicy[number_policy]['start_date'] == "" and dataPolicy[number_policy]['end_date'] == "":
                              if len(re.findall(r'(\d{2}-\d{2}-\d{4}).*(\d{4}-\d{2}-\d{2})', r.upper())) > 0:
                                   s_date = (re.findall(r'(\d{2}-\d{2}-\d{4}).*(\d{4}-\d{2}-\d{2})', r.upper())[0][0]).split('-')
                                   e_date = (re.findall(r'(\d{2}-\d{2}-\d{4}).*(\d{4}-\d{2}-\d{2})', r.upper())[0][1]).split('-')
                                   dataPolicy[number_policy]['start_date'] = str(s_date[2]) + '-' + str(s_date[1]) + '-' + str(s_date[0])
                                   dataPolicy[number_policy]['end_date'] = str(e_date[0]) + '-' + str(e_date[1]) + '-' + str(e_date[2])
                              elif len(re.findall(r'(\d{4}-\d{2}-\d{2}).*(\d{4}-\d{2}-\d{2})', r.upper())) > 0:
                                   s_date = (re.findall(r'(\d{4}-\d{2}-\d{2}).*(\d{4}-\d{2}-\d{2})', r.upper())[0][0]).split('-')
                                   e_date = (re.findall(r'(\d{4}-\d{2}-\d{2}).*(\d{4}-\d{2}-\d{2})', r.upper())[0][1]).split('-')
                                   dataPolicy[number_policy]['start_date'] = str(s_date[0]) + '-' + str(s_date[1]) + '-' + str(s_date[2])
                                   dataPolicy[number_policy]['end_date'] = str(e_date[0]) + '-' + str(e_date[1]) + '-' + str(e_date[2])

                         if dataPolicy[number_policy]['vehicle'] == "":
                              if len(re.findall(r'^([A-Z]{2,3}[\s]?[A-Z0-9]{4,5})', r)) > 0:
                                   dataPolicy[number_policy]['vehicle'] = unicodereplace.generate((re.findall(r'^([A-Z]{2,3}[\s]?[A-Z0-9]{4,5})', r.upper())[0]).replace(' ', ''), 'PL')

                         if dataPolicy[number_policy]['vehicle_vin'] == "":
                              if len(re.findall(r'^([A-Z]{2,3}[\s]?[A-Z0-9]{4,5})[\s]([\w\S]{17})', r.upper())) > 0:
                                   dataPolicy[number_policy]['vehicle_vin'] = re.findall(r'^([A-Z]{2,3}[\s]?[A-Z0-9]{4,5})[\s]([\w\S]{17})', r.upper())[0][1]
                                   
                         if dataPolicy[number_policy]['amount'] == "":
                              if len(re.findall(r'(SKŁADKA[\s\/]+PREMIUM\s)([\d\s,.]+)(ZŁ)', r.upper())) > 0:
                                   dataPolicy[number_policy]['amount'] = (re.findall(r'(SKŁADKA[\s\/]+PREMIUM\s)([\d\s,.]+)(ZŁ)', r.upper())[0][1]).replace('.','').replace(',','.').replace(' ', '')

          if (number_policy in dataPolicy):
               dataPolicy[number_policy]['images'].append(result['filename'])
                              

     # print("<pre>")
     # for data in dataPolicy.values():
     #      print(data)
     #      if (data['start_date'] != '' and data['end_date'] != '' and data['vehicle'] != ''):
     #           ocr.saveFilePDF(data['images'], data['number_policy'] + '-' + data['start_date'] + '-' + data['end_date'] + '-' + data['vehicle'])
     # print("</pre>")  

     for key, data in dataPolicy.items():
          for key2, d in data.items():  
               d = dataPolicy[key]
               if (d['number_policy'] != ''):
                    dataPolicy[key]['file_url'] = ocr.saveFilePDF(d['images'], d['number_policy'])

     logHtml = ''
     if islog == '1':
          # for key, data in dataPolicy.items():
          #      for key2, d in data.items():  
          #           print(d)     

          for key, result in results.items():
               i = 0
               logHtml = logHtml + "<div style='background: #f3f3f3;padding-bottom: 20px;'><b style='font-size: 18px;padding-left:5px;padding-top:5px;'>Page nr: " + str(key) + "</b><hr>"

               for r in result['texts']:
                    logHtml = logHtml + "     [" + str(i) + "] => " + r + "<br>"
                    i = i + 1
               logHtml = logHtml + "</div>"

     

     os.remove(fn)

     response = {"status": 200, "data": dataPolicy, "log": logHtml}
     print(json.dumps(response))
else:
     response = {"status": 400, "data": [], "message": "Zly format pliku"}
     print(json.dumps(response))
