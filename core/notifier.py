import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
import config

def enviar_email(assunto, corpo):
    try:
        # parte responsavel pela estrutura da mensagem
        msg = MIMEMultipart()
        msg['From'] = config.SENDER_EMAIL
        msg['To'] = config.RECEIVER_EMAIL
        msg['Subject'] = assunto

        msg.attach(MIMEText(corpo, 'plain'))

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
    enviar_email("Email teste", "Isso aq eh um email de teste")