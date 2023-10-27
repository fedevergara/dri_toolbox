def registro_ok(eventos):
    html = f"""
        <html>

        <body>
            <div>
                <p>Gracias por registrarse en los eventos: </p>
                {eventos}
            </div>
            </br>
            <div></br></br>
                <p>El QR adjunto es válido para confirmar su asistencia a los eventos a los que se haya registrado</p>
                </br>
                <p>Por favor recuerde presentar este QR en la entrada al evento.</p>
                </br>
            </div>
        </body>
        </html>
        """
    return html