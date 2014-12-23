

function onData(data){
    $("#modtable tbody tr").remove()
    html = "";
    for(var i = 0; i < data.modules.length; i++){
        unload_command = 'command_unloadmod("' + data.modules[i].subsystem + '")'
        reload_command = 'command_reloadmod("' + data.modules[i].subsystem + '")'
        mod_select = 'watch_module("' + data.modules[i].subsystem + '")'
        commands = "<button class='btn btn-warning' onClick='" + unload_command + "'>unload</button>   <button class='btn btn-danger' onClick='" + reload_command +"'>reload</button>"
        status_tag = "<h4 style='display: inline;'><span class='label label-default'>" + data.modules[i].status + "</span></h4>"
        if(data.modules[i].status == "Loaded"){
            status_tag = "<h4 style='display: inline;'><span class='label label-success'>" + data.modules[i].status + "</span></h4>"
        }
        html += '<tr onClick=' + mod_select  + '><td>' + data.modules[i].subsystem + '</td><td>'
                                                       + data.modules[i].filename + '</td><td>'
                                                       + status_tag + '</td><td>'
                                                       + commands + '</td></tr>'
    }

    $("#modtable tbody").html(html)
}

function watch_module(modname){
    var watchingmod = modname
    getData()
}

function load_handler(){
    send_command("load", $("#module_target")[0].value)
}

function command_unloadmod(modname){
    send_command("unload", modname)
}

function command_reloadmod(modname){
    send_command("reload", modname)
}

function send_command(command, target){
    data = { command: command, target: target }
    $.post("/api/command", data)
    setTimeout(getData, 200);
}

function getDataLoop() {
    getData()
    //setTimeout(getDataLoop, 1000);
}

function getData(){$.getJSON("/api/json", onData)}

$(document).ready(function(){
    $("#modtable").bootgrid()
    $("#load_button").click(load_handler)
    $('#module_target').keypress(function (e) {
        if (e.which == 13) {
            load_handler();
            return false;
        }
    });
    setTimeout(getDataLoop, 100);
})