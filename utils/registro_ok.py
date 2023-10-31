def registro_ok(eventos):
    html = f"""
        <!DOCTYPE html>
        <html>
        <body>
        <div>
        <p>Te damos la bienvenida a De País en País Centroamérica y el Caribe.</p>
        </div>

        <div>
        <p>Gracias por registrarse en los eventos:</p>
            {eventos}
        </div>

        <div>
        <p>El QR adjunto es válido para confirmar su asistencia a los eventos a los que se haya registrado.</p>

        <p>Por favor recuerde presentar este QR en la entrada a cada evento.</p>
        </div>
        </body>
        </html>
        """
    return html
