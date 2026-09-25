import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
import logging
import config

def enviar_email(assunto, corpo, status):
    try:

        caminho = ( Path(__file__).parent.parent / "templates" / "email_alert.html" )

        with open(caminho, "r", encoding="utf-8") as file:
            html = file.read()

        html = html.replace("{{ titulo }}", "Novo Alerta")
        html = html.replace("{{ nome }}", "Silva")
        html = html.replace("{{ mensagem }}", corpo)
        if status:
            html = html.replace("{{ status }}", "Sucesso")
            html = html.replace("{{ status_text }}", "Tudo Certo!")
        else:
            html = html.replace("{{ status }}", "Erro")
            html = html.replace("{{ status_text }}", "Erro")

        # parte responsavel pela estrutura da mensagem
        msg = MIMEMultipart("alternative")
        msg['From'] = config.SENDER_EMAIL
        msg['To'] = config.RECEIVER_EMAIL
        msg['Subject'] = "Alerta CryptoTradingBot"

        msg.attach(MIMEText(html, "html", "utf-8"))

        # parte responsavel pelo envio da mensagem
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(config.SENDER_EMAIL, config.SENDER_PASSWORD)
        server.sendmail(config.SENDER_EMAIL, config.RECEIVER_EMAIL, msg.as_string())
        server.quit()

        logging.info("Email enviado")

    except Exception as ex:
        logging.error(f"Erro ao enviar a mensagem: {ex}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    print("Testando envio de email")
    enviar_email("Email teste", "Isso aq eh um email de teste", True)