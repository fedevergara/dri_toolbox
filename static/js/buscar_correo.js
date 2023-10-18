function buscarCorreo() {
    var email = document.getElementById("email").value;

    // Hacer una solicitud AJAX para buscar el correo electrónico en el servidor
    var xhr = new XMLHttpRequest();
    xhr.open("GET", "/buscar_correo?email=" + email, true);
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

          var tipoDocumentoSelect = document.getElementById("tipo_documento");
          var tipoDocumentoOption = tipoDocumentoSelect.querySelector(
            "option[value='" + data.tipo_documento + "']"
          );
          if (tipoDocumentoOption) {
            tipoDocumentoOption.selected = true;
          }

          var paisSelect = document.getElementById("pais");
          var paisOption = paisSelect.querySelector("option[value='" + data.pais + "']");
          if (paisOption) {
            paisOption.selected = true;
          }

          var unidad_academicaSelect = document.getElementById("unidad");
          var unidad_academicaOption = unidad_academicaSelect.querySelector("option[value='" + data.unidad + "']");
          if (unidad_academicaOption) {
            unidad_academicaOption.selected = true;
          }

          var sede_seccionalSelect = document.getElementById("sede");
          var sede_seccionalOption = sede_seccionalSelect.querySelector("option[value='" + data.sede + "']");
          if (sede_seccionalOption) {
            sede_seccionalOption.selected = true;
          }

          var vinculo_udeaDiv = document.getElementById("vinculo");
          var radioButtons = vinculo_udeaDiv.querySelectorAll("input[name='vinculo']");
          radioButtons.forEach(function(radioButton) {
            if (radioButton.value === data.vinculo_udea) {
              radioButton.checked = true;
            }
          });

          // Ocultar el mensaje de error vinculo_udea-error
          var vinculoUdeaError = document.getElementById("vinculo_udea-error");
          vinculoUdeaError.textContent = "";
        }
      }
    };
    xhr.send();
  }