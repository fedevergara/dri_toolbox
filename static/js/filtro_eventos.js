function FiltroEventos() {
    // Selecciona todos los elementos checkbox por su clase ".btn-check"
    const checkboxes = document.querySelectorAll(".btn-check");
    const eventosContainer = document.getElementById("eventos-container"); // Obtén el contenedor de eventos

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
                    enviarSolicitudAjax(valor, actualizarEventos);
                }
            } else {
                // Checkbox deseleccionado
                const label = document.querySelector(`label[for="${this.id}"]`);
                if (label) {
                    const labelText = label.textContent;
                    console.log(`Checkbox ${this.id} deseleccionado. Nombre del botón: ${labelText}`);
                    const valor = `del-${labelText}`; // Agregar 'del' al valor
                    enviarSolicitudAjax(valor, actualizarEventos);
                }
            }
        });
    });

    function actualizarEventos(eventosFiltrados) {
        // Limpia el contenedor de eventos
        eventosContainer.innerHTML = '';

        // Agrega eventos filtrados al contenedor
        for (const evento of eventosFiltrados) {
            const div = document.createElement('div');
            div.className = 'form-check form-switch';
            div.innerHTML = `
                <input class="form-check-input" type="checkbox" id="evento_${evento.id}" name="eventos" value="${evento.valor}" ${evento.checked ? 'checked' : ''}>
                <label class="form-check-label" for="evento_${evento.id}">${evento.evento}</label>
                <i class="bi bi-info-circle"></i>
            `;

            eventosContainer.appendChild(div);
        }
    }
}


function enviarSolicitudAjax(valorCheckbox, callback) {
    const xhr = new XMLHttpRequest();

    // Define la ruta de la solicitud AJAX, reemplaza '/ruta_al_servidor' con la ruta correcta
    xhr.open("GET", "/filtrar_eventos?dia=" + valorCheckbox, true);

    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            console.log('Respuesta del servidor:', xhr.responseText);
            const data = JSON.parse(xhr.responseText);
            callback(data);
        }
    };

    // Envía la solicitud AJAX
    xhr.send();
}

// Añade el evento 'load' para llamar a la función FiltroEventos cuando la página se cargue completamente
window.addEventListener("load", FiltroEventos);