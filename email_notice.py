import smtplib
import socket

from email.mime.multipart import MIMEMulitpart
from email.mime.text import MIMEText

class Email:
    """
    Them Email class allows the program to build customized messages automatically.
    The objects are meant to be sent to an emailer object as a string to be mailed
    """

    def __init__(self, address, job_name, batch_name, run_name, slurm_name, out_path, ntasks):
        self.insert_data = {"job_name": job_name,
                            "batch_name": batch_name,
                            "run_name": run_name,
                            "slurm_name": slurm_name,
                            "out_path": out_path,
                            "ntasks": ntasks,
                            "terminatet": datetime.datetime.now()}

        self.body = ""
        self.add_message(message_type)

        self.msg = MIMEMultipart()
        self.msg["To"] = address
        self.msg["Subject"] = "Job: {job_name} has terminated".format(job_name)

    def build_and_send_message(self):
        """Attaches all the body string to the message"""
        body = MIMEText(self.body, 'plain')
        self.msg.attach(body)

        server = smtplib.SMTP('localhost')
        sender = "LogoPipe-{host}".format(socket.gethostname())
        server.sendmail(sender, self.msg["To"], self.msg.as_string())
        #server.sendmail("Do-Not-Reply", "wpatt2@pdx.edu", self.msg.as_string())

    def add_message(self):
        """Loads a pre-written message from external file and adds info to it from data_dict"""

        self.scan_slurm_file()
        message_file = os.path.abspath("./email_template.txt")

        try:
            with open(message_file, 'r') as mfile:
                message_str = mfile.read()
            self.body += message_str.format(**self.insert_data)

        except KeyError as keyerr:
            raise keyerr

    def scan_slurm_file(self):
        with open(self.insert_data["slurm_name"], 'r') as sfile:
            sdata = sfile.read()

        sdata = sdata.lower()
        self.insert_data["err"] = sdata.count("error")
        self.insert_data["warn"] = sdata.count("warning")

    def generate_email_command(self):
        self.insert_data["fpath"] = __file__
        return "{fpath} {address} {job_name} {batch_name} {run_name} {slurm_name} {out_path} {ntasks}".format(**self.insert_data)

    def attach_file_stream(self, stream, attached_file_name):
        """
        This method allows you to attach a file to a message
        ***NOT USED***
        """
        stream.seek(0)
        attachment = MIMEText(stream.read())
        attachment.add_header('Content-Disposition', 'attachment', filename=attached_file_name)
        self.msg.attach(attachment)

def get_args():
    parser = ArgumentParser(description="")
    parser.add_argument("address", type=str, help="Email address")
    parser.add_argument("job_name", type=str, help="Job name")
    parser.add_argument("batch_name", type=str, help="Batch name")
    parser.add_argument("run_name", type=str, help="Run name")
    parser.add_argument("slurm_name", type=str, help="Slurm out file name")
    parser.add_argument("out_path", type=str, help="Path to output")
    parser.add_argument("ntasks", type=str, help="Number of tasks in the job")

    return parser.parse_args()

def main():
    args = get_args()
    email = Email(args.address,
                  args.job_name,
                  args.batch_name,
                  args.run_name,
                  args.slurm_name,
                  args.out_path,
                  args.ntasks)

    email.build_and_send_message()

