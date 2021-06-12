


  ////////////////////////////////////////////////////////////
  function exportar(tableID, filename = ''){
    
var downloadLink;
var dataType = 'application/vnd.ms-excel';
var tableSelect = document.getElementById(tableID);
var tableHTML = tableSelect.outerHTML.replace(/ /g, '%20');

// Specify file name
filename = filename?filename+'.xls':'excel_data.xls';

// Create download link element
downloadLink = document.createElement("a");

document.body.appendChild(downloadLink);

if(navigator.msSaveOrOpenBlob){
    var blob = new Blob(['\ufeff', tableHTML], {
        type: dataType
    });
    navigator.msSaveOrOpenBlob( blob, filename);
}else{
    // Create a link to the file
    downloadLink.href = 'data:' + dataType + ', ' + tableHTML;

    // Setting the file name
    downloadLink.download = filename;
    
    //triggering the function
    downloadLink.click();
}
}

function esperar2(ticker){
  document.location.href="datos/"+ticker;
}

function esperar3(ticker){
  document.location.href="indice/"+ticker;
}

function mostrar(){
  var x = document.getElementById("barra");
  if (x.style.display === "none") {
    x.style.display = "block";
  } else {
    x.style.display = "none";
  }
}