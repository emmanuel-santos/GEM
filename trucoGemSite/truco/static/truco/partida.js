
var mi_turno = false;
var fin = false;
var visto = false;

function me_toca() {
    // window.alert("ahora me toca");
    window.scrollTo(0,document.body.scrollHeight);
    mi_turno = true;
    if (visto) {
        $("#botones button").addClass("invisible");
    }
}

function se_termino(valor) {
    fin = valor;
}

function refresh(){
    if (!mi_turno || fin) {
        $("#content").load( $(location).attr('pathname') + "/refresh", function () {
            $("select").addClass("form-control");
            $("select").css("width","90%");
        });
    }
}

function accion(link){
    if (mi_turno) {
        $("#botones").addClass("invisible");
        $.get(link);
        refresh();
        mi_turno = false;
        if (link.search('continuar')) {
            visto = true;
            setTimeout( function () {
                visto = false;
                $("#botones button").removeClass("invisible");
            }, 2000)
            fin = true;
        }
    }
}

setInterval(refresh, 3000);
