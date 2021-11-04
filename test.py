#!C:\Users\gerro\AppData\Local\Programs\Python\Python39\python.exe

print("Content-Type: text/html; charset=utf-8\n\n")
import ocr
import cgi
import cgitb
import os
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')
cgitb.enable()

form = cgi.FieldStorage()
lineheight =  form.getvalue('lineheight')

file = form['upload_file']
dirFolder = 'ocr-pdf'

if file.filename:
     customFileName = str(round(time.time() * 1000)) + os.path.basename(file.filename)
     fn = dirFolder + "/" + customFileName
     open(fn, 'wb').write(file.file.read())

     results = ocr.generate(fn, lineheight)

     
     
     for key, result in results.items():
          i = 0
          print("<br><br><div style='background: #f3f3f3;padding-bottom: 20px;'><b style='font-size: 18px;padding-left:5px;padding-top:5px;'>Page nr: " + str(key) + "</b>") 
          print("<pre>")
          for r in result:
               print("     [" + str(i) + "] => " + r + "")
               i = i + 1
          print("</pre></div>")

     os.remove(fn)



# ocr.generate('test.pdf')