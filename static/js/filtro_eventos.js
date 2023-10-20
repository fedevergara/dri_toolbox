function FiltroEventos() {
    // Selecciona todos los elementos checkbox por su clase ".btn-check"
    const checkboxes = document.querySelectorAll(".btn-check");

    checkboxes.forEach(checkbox => {
        checkbox.addEventListener("change", function () {
            if (this.checked) {
                // Checkbox presionado
                const label = document.querySelector(`label[for="${this.id}"]`);
                if (label) {
                    const labelText = label.textContent;
                    console.log(`Checkbox ${this.id} presionado. Nombre del botón: ${labelText}`);
                    const valor = `add-${labelText}`;
                    // Envía una solicitud AJAX al servidor con el valor del checkbox
                    enviarSolicitudAjax(valor);
                }
            } else {
                // Checkbox deseleccionado
                const label = document.querySelector(`label[for="${this.id}"]`);
                if (label) {
                    const labelText = label.textContent;
                    console.log(`Checkbox ${this.id} deseleccionado. Nombre del botón: ${labelText}`);
                    const valor = `del-${labelText}`; // Agregar 'del' al valor
                    enviarSolicitudAjax(valor);
                }
            }
        });
    });
}

function enviarSolicitudAjax(valorCheckbox) {
    const xhr = new XMLHttpRequest();

    // Define la ruta de la solicitud AJAX, reemplaza '/ruta_al_servidor' con la ruta correcta
    xhr.open("GET", "/filtrar_eventos?dia=" + valorCheckbox, true);

    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            const data = JSON.parse(xhr.responseText);
            console.log(data);
        }
    };

    // Envía la solicitud AJAX
    xhr.send();
}

// Añade el evento 'load' para llamar a la función FiltroEventos cuando la página se cargue completamente
window.addEventListener("load", FiltroEventos);