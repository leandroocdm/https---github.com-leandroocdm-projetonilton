from flask import Flask, request, render_template, send_file, Response
from weasyprint import HTML
import os
from datetime import datetime
import re
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def escape_html(text):
    """Escape HTML special characters to prevent injection."""
    if not text:
        return text
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;')

@app.route('/', methods=['GET', 'POST'])
def orcamento():
    if request.method == 'POST':
        try:
            # Get form data
            nome_cliente = escape_html(request.form.get('nomeCliente'))
            cpf_cnpj = escape_html(request.form.get('cpfCnpjCliente'))
            descricao_servico = escape_html(request.form.get('descricaoServico'))
            observacoes = escape_html(request.form.get('observacoes'))
            valor_total = request.form.get('valorTotal')

            # Validate form inputs
            if not nome_cliente or not descricao_servico or not valor_total:
                logger.error("Campos obrigatórios não preenchidos.")
                return "Por favor, preencha todos os campos obrigatórios.", 400

            try:
                valor_total = float(valor_total)
                if valor_total <= 0:
                    logger.error("Valor total inválido: %s", valor_total)
                    return "O valor total deve ser maior que zero.", 400
            except ValueError:
                logger.error("Valor total não é um número válido: %s", valor_total)
                return "O valor total deve ser um número válido.", 400

            # Validate CPF/CNPJ
            if cpf_cnpj:
                cpf_cnpj_clean = re.sub(r'[^\d]', '', cpf_cnpj)
                if not re.match(r'^(\d{11}|\d{14})$', cpf_cnpj_clean):
                    logger.error("CPF/CNPJ inválido: %s", cpf_cnpj)
                    return "Por favor, insira um CPF (11 dígitos) ou CNPJ (14 dígitos) válido.", 400

            # Calculate payment options
            valor_a_vista = f"{valor_total:.2f}"
            taxa_cartao = 0.05  # 5% fee
            valor_cartao = f"{valor_total * (1 + taxa_cartao):.2f}"

            # Get current date
            today = datetime.now().strftime('%d/%m/%Y')

            # Render PDF template
            html_content = render_template(
                'pdf_template.html',
                nome_cliente=nome_cliente,
                cpf_cnpj=cpf_cnpj or "Não informado",
                descricao_servico=descricao_servico,
                observacoes=observacoes or "Nenhuma observação fornecida.",
                valor_a_vista=valor_a_vista,
                valor_cartao=valor_cartao,
                today=today
            )

            # Generate PDF
            pdf_path = f"orcamento_{nome_cliente}_{today.replace('/', '-')}.pdf"
            try:
                HTML(string=html_content, base_url=os.path.dirname(__file__)).write_pdf(pdf_path)
                logger.info("PDF gerado com sucesso: %s", pdf_path)
            except Exception as e:
                logger.error("Erro ao gerar PDF: %s", str(e))
                return f"Erro ao gerar PDF: {str(e)}", 500

            # Send PDF as download
            return send_file(
                pdf_path,
                as_attachment=True,
                download_name=pdf_path,
                mimetype='application/pdf'
            )

        except Exception as e:
            logger.error("Erro geral no processamento do formulário: %s", str(e))
            return f"Erro ao processar o formulário: {str(e)}", 500

    # Render form for GET request
    return render_template('form.html')

if __name__ == '__main__':
    app.run(debug=True)