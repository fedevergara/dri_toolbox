// script.js
document.addEventListener('DOMContentLoaded', function () {
    const categoriaField = document.querySelector('#categoriaInternacional');
    const seccionInternacional = document.querySelector('#seccionInternacional');
    const seccionNacional = document.querySelector('#seccionNacional');

    // Función para mostrar u ocultar las secciones en función de la categoría seleccionada
    function mostrarOcultarSecciones() {
        if (categoriaField.value === 'internacional') {
            seccionInternacional.classList.remove('hidden-section');
            seccionNacional.classList.add('hidden-section');
        } else if (categoriaField.value === 'nacional') {
            seccionNacional.classList.remove('hidden-section');
            seccionInternacional.classList.add('hidden-section');
        }
    }

    // Detectar cambios en la categoría
    categoriaField.addEventListener('change', mostrarOcultarSecciones);

    // Mostrar u ocultar secciones en función de la categoría inicial
    mostrarOcultarSecciones();
});