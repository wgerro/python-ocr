#!C:\Users\gerro\AppData\Local\Programs\Python\Python39\python.exe

print("Content-Type: text/html; charset=utf-8\n\n")
import ocr
import cgi
import cgitb
import os
import time
cgitb.enable()

form = cgi.FieldStorage()
lineheight =  form.getvalue('lineheight')

file = form['upload_file']
dirFolder = 'ocr-pdf'

if file.filename:
     customFileName = str(round(time.time() * 1000)) + os.path.basename(file.filename)
     fn = dirFolder + "/" + customFileName
     open(fn, 'wb').write(file.file.read())
     print(ocr.generate(fn))


# ocr.generate('test.pdf')