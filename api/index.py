from flask import Flask, request, send_file
from fpdf import FPDF
import qrcode
import io
import os
import hashlib

app = Flask(__name__)

@app.route('/api/generar')
def generar():
    # 1. Obtener el CURP de la URL
    curp = request.args.get('curp', '').upper()
    if len(curp) != 18:
        return "CURP inválido. Debe tener 18 caracteres.", 400

    # 2. Cálculos automáticos (RFC e idCIF simulado)
    # El RFC son los primeros 10 del CURP + homoclave (usamos K20 para Miguel)
    rfc = curp[:10] + "K20" 
    idcif = "16080297174"

    # 3. Configuración del PDF
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    
    # Ruta de la plantilla
    base_dir = os.path.dirname(__file__)
    img_path = os.path.join(base_dir, "..", "assets", "plantilla.png")
    
    # Dibujar fondo
    if os.path.exists(img_path):
        pdf.image(img_path, x=0, y=0, w=210, h=297)
    else:
        return f"Error: No se encontró plantilla.png en assets/", 500

    # 4. Generar QR de Validación
    qr_data = f"https://generador-fiscal.vercel.app/?rfc={rfc}"
    qr = qrcode.make(qr_data)
    qr_io = io.BytesIO()
    qr.save(qr_io, 'PNG')
    qr_io.seek(0)
    
    # Insertar QR en el recuadro superior izquierdo
    pdf.image(qr_io, x=65, y=82, w=25) # Ajustado según la Cédula

    # 5. Estampar Datos (Coordenadas ajustadas a tu imagen)
    pdf.set_font("Helvetica", style='B', size=9)
    
    # Datos de la Cédula (Cuadro pequeño arriba)
    pdf.set_xy(65, 103)
    pdf.cell(0, 0, rfc)
    
    # Datos de Identificación (Tabla principal)
    pdf.set_font("Helvetica", size=8)
    
    pdf.set_xy(36, 115) # RFC
    pdf.cell(0, 0, rfc)
    
    pdf.set_xy(36, 125) # CURP
    pdf.cell(0, 0, curp)
    
    pdf.set_xy(36, 135) # Nombre
    pdf.cell(0, 0, "MIGUEL ANGEL")
    
    pdf.set_xy(36, 145) # Apellido 1
    pdf.cell(0, 0, "ESCOBEDO")
    
    pdf.set_xy(36, 155) # Apellido 2
    pdf.cell(0, 0, "FAVELA")
    
    pdf.set_xy(36, 165) # Fecha Inicio
    pdf.cell(0, 0, "15/08/2016")
    
    pdf.set_xy(36, 175) # Estatus
    pdf.set_text_color(0, 100, 0) # Verde para "ACTIVO"
    pdf.cell(0, 0, "ACTIVO")
    pdf.set_text_color(0, 0, 0)

    # 6. Datos de Domicilio (Ejemplo basado en su zona)
    pdf.set_xy(36, 215) # CP
    pdf.cell(0, 0, "32590")
    
    pdf.set_xy(110, 245) # Entidad
    pdf.cell(0, 0, "CHIHUAHUA")

    # 7. Retornar el PDF al navegador
    buf = io.BytesIO()
    pdf_output = pdf.output(dest='S')
    buf.write(pdf_output)
    buf.seek(0)
    
    return send_file(
        buf, 
        mimetype='application/pdf', 
        as_attachment=False, 
        download_name=f"Constancia_{rfc}.pdf"
    )

if __name__ == '__main__':
    app.run(debug=True)
    
