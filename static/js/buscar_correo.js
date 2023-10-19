function buscarCorreo() {
    var email = document.getElementById("email").value; // Obtener el valor del campo de correo electrónico
  
    // Crear una solicitud AJAX para buscar el correo electrónico en el servidor
    var xhr = new XMLHttpRequest();
    xhr.open("GET", "/buscar_correo?email=" + email, true);
  
    // Definir una función que maneja la respuesta de la solicitud
    xhr.onreadystatechange = function() {
      if (xhr.readyState === 4 && xhr.status === 200) {
        // Parsear la respuesta JSON con los datos encontrados
        var data = JSON.parse(xhr.responseText);
  
        // Asignar los valores a los campos relevantes si se encontraron datos
        if (data) {
          document.getElementById("nombres").value = data.nombres;
          document.getElementById("apellidos").value = data.apellidos;
          document.getElementById("documento").value = data.numero_documento_identidad;
          document.getElementById("ciudad").value = data.ciudad;
          document.getElementById("entidad").value = data.entidad;
          document.getElementById("programa").value = data.programa;

          // Asignar valores a las listas desplegables
          document.getElementById("tipos_documento").value = data.tipo_documento_identidad;
          document.getElementById("pais").value = data.pais;
          document.getElementById("vinculo").value = data.vinculo;
          document.getElementById("unidad").value = data.unidad;
          document.getElementById("sede").value = data.sede;
        }
      }
    };
    xhr.send(); // Enviar la solicitud al servidor
  }