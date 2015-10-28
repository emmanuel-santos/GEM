
var categoria = 0

function refresh(){
    $("#partidas").load("/hall/" + categoria)
}

function cambiar_categoria(num){
    $(".active").removeClass("active");
    $("#categoria" + num).addClass("active").tab('show');
    categoria = num;
    refresh()
}

setInterval(refresh, 3000);