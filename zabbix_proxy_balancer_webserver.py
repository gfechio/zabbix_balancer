import sys,os
import string,cgi,time
import logging
import zabbix_proxy_balancer as proxy_balancer
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import zabbix_proxy_balancer_config as config

token = proxy_balancer.get_token()
output_file = config.log['file']

logger = logging.getLogger('zabbix_proxy_balancer')
hndlr = logging.FileHandler(output_file)
formatter = logging.Formatter('%(asctime)s %(message)s')
hndlr.setFormatter(formatter)
logger.addHandler(hndlr)
logger.setLevel(logging.INFO)


class http(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()
            self.wfile.write(proxy_balancer.get_zabbix_best_proxy(token))
            return


        except IOError:
            self.send_error(404,'File Not Found: %s' % self.path)

    def log_message(self, format, *args):
            file = open(output_file, "a")
            file.write("%s - - [%s] %s\n" %(self.address_string(),self.log_date_time_string(),format%args))
            file.close()

    def log_error(self, format, *args):
            file = open(output_file, "a")
            file.write("%s - - [%s] %s\n" %(self.address_string(),self.log_date_time_string(),format%args))
            file.close()

def main(NameVirtualHost):
    try:
        virtualhost = string.split(NameVirtualHost,":")
        if virtualhost[0] == "*":
            virtualhost[0] = ""
        server = HTTPServer((virtualhost[0], int(virtualhost[1])), http)
        logging.info('Start server HTTP  in 8080')
        server.serve_forever()

    except KeyboardInterrupt:
        logging.info('Shutting down server HTTP')
        server.socket.close()

try:
    main("localhost:8080")
except:
    logging.info('===== Error binding server on port 8080 for localhost !!')
