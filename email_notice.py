import smtplib

from email.mime.multipart import MIMEMulitpart
from email.mime.text import MIMEText

class Email:
    """
    Them Email class allows the program to build customized messages automatically.
    The objects are meant to be sent to an emailer object as a string to be mailed
    """

    def __init__(self, address, job_name, batch_name, run_name, slurm_name, out_path, ntasks)
        self.body = ""
        self.add_message(message_type, data_dict)

        self.msg = MIMEMultipart()
        self.msg["To"] = address
        self.msg["Subject"] = "Job: {job_name} has terminated".format(job_name)

    def build_and_send_message(self):
        """Attaches all the body string to the message"""
        body = MIMEText(self.body, 'plain')
        self.msg.attach(body)

        server = smtplib.SMTP('localhost')
        server.sendmail("LogoPipe", self.msg["To"], self.msg.as_string())
        #server.sendmail("Do-Not-Reply", "wpatt2@pdx.edu", self.msg.as_string())

    def add_message(self, message_type, data_dict):
        """Loads a pre-written message from external file and adds info to it from data_dict"""
        message_file = os.path.abspath("./email_template.txt")

        try:
            with open(message_file, 'r') as mfile:
                message_str = mfile.read()
            self.body += message_str.format(**data_dict)

        except KeyError as keyerr:
            self.logger.error("Key %s does not exist", keyerr.args[0])
            raise keyerr

    def attach_file_stream(self, stream, attached_file_name):
        """
        This method allows you to attach a file to a message
        ***NOT USED***
        """
        stream.seek(0)
        attachment = MIMEText(stream.read())
        attachment.add_header('Content-Disposition', 'attachment', filename=attached_file_name)
        self.msg.attach(attachment)
