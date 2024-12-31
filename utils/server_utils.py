from subprocess import Popen, PIPE, STDOUT
from pyngrok import ngrok


def expose_port_expose(port):
    p = Popen(f'expose {port}', stdout=PIPE, stderr=STDOUT, shell=True, text=True)
    line = p.stdout.readline()
    webhook_url = line[:line.find(" ")].replace('http', 'https')
    return webhook_url


def expose_port_ngrok(port):
    return ngrok.connect(port, bind_tls=True).public_url
