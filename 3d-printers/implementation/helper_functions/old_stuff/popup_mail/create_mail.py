
import os
import uuid
from email import generator
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# where to write the output file
directory = "./test_env/"

body = "Hello email!"

subject = "your print is shit"

toAddress = "g.s.groote@student.tudelft.nl"

fromAddress = "gijsgroote@hotmail.com"

def create_message():
    msg = MIMEMultipart()
    msg["To"] = toAddress
    msg["From"] = fromAddress
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    return msg

def write_eml_file(msg):
    os.chdir(directory)
    # filename = str(uuid.uuid4()) + ".eml"
    filename = str("test.eml")
    print(f"filename is {filename}")

    with open(filename, 'w') as file:
        emlGenerator = generator.Generator(file)
        emlGenerator.flatten(msg)

def main():
    msg = create_message()
    write_eml_file(msg)
    print(f"message {msg}")

if __name__ == "__main__":
    main()


