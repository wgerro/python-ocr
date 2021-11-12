<!DOCTYPE html>
<html lang="en">
<head>
     <meta charset="UTF-8">
     <meta http-equiv="X-UA-Compatible" content="IE=edge">
     <meta name="viewport" content="width=device-width, initial-scale=1.0">
     <title>Document</title>
     <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous">
     <link href="https://unpkg.com/dropzone@6.0.0-beta.1/dist/dropzone.css" rel="stylesheet" type="text/css" />
     <style>
          .dropzone{
               border-color: transparent;
          }
          button.dz-button {
               color: #cfcfcf !important;
          }
     </style>
</head>
<body>
     <div class="container">
          <div class="row">
               <div class="col-12 mt-2">
                    <div class="card">
                         <div class="card-header">
                              Ustawienia
                         </div>
                         <div class="card-body">
                              <p>
                                   Dla <b>ERGO</b> zalecane jest PSM 11 <br>
                                   Dla <b>WARTA NOWA</b> zalecane jest PSM 3 <br>
                                   Dla <b>WARTA</b> zalecane jest PSM 11 <br>
                                   Dla <b>COMPENSA</b> zalecane jest PSM 11 <br>
                              </p>
                              <div style='display: inline-block'>
                                   <b>Line height:</b>
                                   <input type="number" name="lineheight" value="8">
                              </div>
                              <div style='display: inline-block'>
                                   <b>DPI:</b>
                                   <input type="number" name="dpi" value="200">
                              </div>
                              <div style='margin-top:5px;'>
                                   <b>PSM:</b>
                                   <select name="psm" style="padding-top: 3px;padding-bottom: 3px;">
                                        <option value="0" disabled>0 - PSM_OSD_ONLY - Tylko orientacja i wykrywanie skryptów. (Niedostępne) </option>
                                        <option value="1" disabled>1 - PSM_AUTO_OSD	- Automatyczna segmentacja stron z wykrywaniem orientacji i skryptu. (OSD) (Niedostępne) </option>
                                        <option value="2">2 - PSM_AUTO_ONLY - Automatyczna segmentacja stron, ale bez OSD lub OCR.</option>
                                        <option value="3"  >3 - PSM_AUTO - W pełni automatyczna segmentacja stron, ale bez OSD.</option>
                                        <option value="4">4 - PSM_SINGLE_COLUMN	- Załóż jedną kolumnę tekstu o różnych rozmiarach.</option>
                                        <option value="5">5 - PSM_SINGLE_BLOCK_VERT_TEXT - Załóż pojedynczy jednolity blok tekstu wyrównanego w pionie.</option>
                                        <option value="6" >6 - PSM_SINGLE_BLOCK - Załóż pojedynczy jednolity blok tekstu.</option>
                                        <option value="7">7 - PSM_SINGLE_LINE - Traktuj obraz jako pojedynczą linię tekstu.</option>
                                        <option value="8">8 - PSM_SINGLE_WORD - Traktuj obraz jako jedno słowo.</option>
                                        <option value="9">9 - PSM_CIRCLE_WORD - Potraktuj obraz jako pojedyncze słowo w kółku.</option>
                                        <option value="10">10 - PSM_SINGLE_CHAR - Traktuj obraz jako pojedynczy znak.</option>
                                        <option value="11" selected>11 - PSM_SPARSE_TEXT - Znajdź jak najwięcej tekstu w dowolnej kolejności.</option>
                                        <option value="12">12 - PSM_SPARSE_TEXT_OSD - Rzadki tekst z orientacją i det. skryptu.</option>
                                        <option value="13">13 - PSM_RAW_LINE - Traktuj obraz jako pojedynczą linię tekstu, omijając hacki specyficzne dla Tesseractu.</option>
                                   </select>
                              </div>
                              <div style='display: block'>
                                   <b>Pokaż logi:</b>
                                   <input type="checkbox" name="islog" value="1">
                              </div>
                         </div>
                    </div>
               </div>
               <div class="col-12  mt-2">
                    <div class="card">
                         <div class="card-body p-0" style="background: #f7f7f7;">
                              <form  class="dropzone" id="uploadFiles" method="POST" enctype="multipart/form-data"></form>
                         </div>
                    </div>
               </div>
               <div class="col-12  mt-2">
                    <div class="card">
                         <div class="card-header">
                              Zczytane dane
                         </div>
                         <div class="card-body">
                              <div class="row">
                                   <div id="logs" class="col-12"></div>
                              </div>
                         </div>
                    </div>
               </div>
               <div class="col-12  mt-2">
                    <div class="card">
                         <div class="card-header">
                              Logi
                         </div>
                         <div class="card-body">
                              <div class="row">
                                   <div id="logs" class="col-12"></div>
                              </div>
                         </div>
                    </div>
               </div>
          </div>
     </div>
     

     

     <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/js/bootstrap.bundle.min.js" integrity="sha384-MrcW6ZMFYlzcLA8Nl+NtUVF0sA7MsXsP1UyJoMp4YLEuNSfAP+JcXn/tWtIaxVXM" crossorigin="anonymous"></script>
     <script src="https://unpkg.com/dropzone@6.0.0-beta.1/dist/dropzone-min.js"></script>
     <script> 
     
     let lineHeight = document.querySelector('input[name=lineheight]');
     let dpi = document.querySelector('input[name=dpi]');
     let psm = document.querySelector('select[name=psm]');
     let islog = document.querySelector('input[name=islog]');
     let logsDiv = document.getElementById('logs');

     let myDropzone = new Dropzone("#uploadFiles", { 
          url: "test.py",
          addRemoveLinks: true,
          init: function() {
               let dz = this;
               this.on('sending', function(file, xhr, formData) {
                    formData.append('lineheight', lineHeight.value)
                    formData.append('dpi', dpi.value)
                    formData.append('psm', psm.value)
                    formData.append('islog', islog.checked ? 1 : 0)
                    logsDiv.innerHTML = "";
               })

               this.on('success', function(file, response) {
                    let html = ''
                    response = JSON.parse(response);
                    for (i in response.data) {
                         html += printLog(response.data[i]);
                    }
                    logsDiv.innerHTML = html;
               })
          }
     });

     function printLog(data = {}) {
          data.number_policy = data.number_policy ? data.number_policy : '';
          data.vehicle = data.vehicle ? data.vehicle : '';
          data.start_date = data.start_date ? data.start_date : '';
          data.end_date = data.end_date ? data.end_date : '';
          data.amount = data.amount ? data.amount : '';
          data.file_url = data.file_url ? data.file_url : '';

          let text = `
               <form class='border-bottom mb-2'>
                    <div class="row">
                         <div class="col-md-4 mb-2">
                              <input type="text" class="form-control form-control-sm" id="validationCustom01" title="Numer polisy" value="${data.number_policy}" required>
                         </div>
                         <div class="col-md-4 mb-2">
                              <input type="text" class="form-control form-control-sm" id="validationCustom01" title="Nr rejestracyjny" value="${data.vehicle}" required>
                         </div>
                         <div class="col-md-4 mb-2">
                              <input type="text" class="form-control form-control-sm" id="validationCustom01" title=">Data zakończenia" value="${data.amount}" required>
                         </div>
                         <div class="col-md-4 mb-2">
                              <input type="text" class="form-control form-control-sm" id="validationCustom01" title="Data rozpoczecia" value="${data.start_date}" required>
                         </div>
                         <div class="col-md-4 mb-2">
                              <input type="text" class="form-control form-control-sm" id="validationCustom01" title="Data zakończenia" value="${data.end_date}" required>
                         </div>
                         <div class="col-md-4 mb-2 d-flex">
                              <a href="${data.file_url}" class="btn btn-warning btn-sm w-50 rounded-0" target="_blank">PDF</a>
                              <button class="btn btn-primary btn-sm w-50 rounded-0" type="submit">Importuj</button>
                         </div>
                    </div>
                    
               </form>
          `;
          return text;
     }
     
     </script>
</body>
</html>