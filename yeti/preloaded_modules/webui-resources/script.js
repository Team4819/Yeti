//$("#modtable").bootgrid()

function onData(data){
    $("#modtable tbody tr").remove()
    html = "";
    for(var i = 0; i < data.modules.length; i++){
        html += '<tr><td>' + data.modules[i].subsystem + '</td><td>'
                           + data.modules[i].filename + '</td><td>'
                           + data.modules[i].filename + '</td><td>'
                           + data.modules[i].status + '</td></tr>'
    }
    $("#modtable tbody").html(html)
}

function getDataLoop() {
    $.getJSON("/json", onData);
    //setTimeout(getDataLoop, 1000);
}

$(document).ready(function(){
    setTimeout(getDataLoop, 1000);
})