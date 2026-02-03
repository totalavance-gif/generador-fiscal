from flask import Flask, request, send_file
from fpdf import FPDF
import qrcode
import io
import os
import hashlib

app = Flask(__name__)

@app.route('/api/generar')
def generar():
    curp = request.args.get('curp', '').upper()
    if len(curp) != 18: return "CURP inválido", 400
    
    # [span_1](start_span)Datos basados en tu documento[span_1](end_span)
    # Generamos un RFC y idCIF consistente usando el CURP
    rfc = curp[:10] + hashlib.md5(curp.encode()).hexdigest()[:3].upper()
    idcif = str(int(hashlib.sha256(rfc.encode()).hexdigest(), 16))[:11]
    
    pdf = FPDF()
    pdf.add_page()
    
    # [span_2](start_span)Cargar la imagen de fondo (la que subiste)[span_2](end_span)
    base_dir = os.path.dirname(__file__)
    img_path = os.path.join(base_dir, "..", "assets", "plantilla.png")
    pdf.image(img_path, x=0, y=0, w=210, h=297)
    
    # [span_3](start_span)Escribir RFC en la Cédula (pág 1)[span_3](end_span)
    pdf.set_font("Helvetica", size=10)
    pdf.set_xy(53, 42) 
    pdf.cell(0, 10, rfc)
    
    # [span_4](start_span)Escribir RFC y CURP en la tabla de datos[span_4](end_span)
    pdf.set_xy(40, 105) 
    pdf.cell(0, 10, rfc)
    pdf.set_xy(40, 115) 
    pdf.cell(0, 10, curp)
    
    buf = io.BytesIO()
    pdf_text = pdf.output()
    buf.write(pdf_text)
    buf.seek(0)
    return send_file(buf, mimetype='application/pdf')
  
