function Vinculo() {
    var vinculo = document.getElementById("vinculo").value;

    if (vinculo == "Externo") {
        document.getElementById("unidad").disabled = true;
        document.getElementById("unidad").value = "N/A";
        document.getElementById("programa").disabled = true;
        document.getElementById("programa").value = "N/A";
        document.getElementById("sede").disabled = true;
        document.getElementById("sede").value = "N/A";
    } else {
        document.getElementById("unidad").disabled = false;
        document.getElementById("programa").disabled = false;
        document.getElementById("sede").disabled = false;
    }
}