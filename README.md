# Table of Contents 
- [Table of Contents](#table-of-contents)
- [a2utils](#a2utils)
- [Installation](#installation)
- [CLI utilities](#cli-utilities)
  - [a2vhost](#a2vhost)
  - [a2conf](#a2conf)
  - [a2certbot](#a2certbot)
    - [Requesting new certificate and troubleshooting](#requesting-new-certificate-and-troubleshooting)
    - [Troubleshooting renew certificates](#troubleshooting-renew-certificates)
    - [a2certbot warnings (false positives)](#a2certbot-warnings-false-positives)
  - [a2okerr](#a2okerr)


# a2utils 

Package consist of few CLI utilities (based on [a2conf](https://github.com/yaroslaff/a2conf) library)

- `a2conf` -  query apache2 config (e.g. get DocumentRoot or get all hostnames for specific VirtualHost)
- `a2certbot` - diagnose problems with Apache2 VirtualHost and LetsEncrypt certificates and make SSL sites easily
- `a2vhost` - manipulate apache2 VirtualHosts
- `a2okerr` - generate indicators for SSL VirtualHosts in [okerr](https://okerr.com/) monitoring system.

All utilities 

# Installation
Usual simple way:
~~~
pip3 install a2utils
~~~

or get sources from git repo:
~~~
git clone https://github.com/yaroslaff/a2utils
~~~
If using git sources (without installing), work from root dir of repo and do `export PYTONPATH=.`


# CLI utilities

## a2vhost

a2vhost is utility to create new http/https websites from CLI. Easy to use from your scripts.

Example uses hosts echoN.sysattack.com, but you should test with your hostname(s).

Mighty one-liner: create HTTP/HTTPS websites (http will redirect to https), obtain certificate for https. (as root)

```shell
a2vhost --both -d echo2.sysattack.com echo3.sysattack.com echo4.sysattack.com echo5.sysattack.com --auto
```
`--both` instructs to make both https website (main) and small plain http website to handle letsencrypt verification and redirect to https.

`--auto` auto-detects virtualhost config file name (you may override with `-c`) and guesses and creates webroot directory if it's missing (override with `-w`)

Following commands will make similar job step-by-step and without `--auto`:

Create basic HTTP website
```shell
# Create files for new site
$ mkdir /var/www/virtual/echo2.sysattack.com
$ echo hello > /var/www/virtual/echo2.sysattack.com/index.html

# Create HTTP VirtualHost and test
$ a2vhost --basic -d echo2.sysattack.com echo3.sysattack.com echo4.sysattack.com -w /var/www/virtual/echo2.sysattack.com -c /etc/apache2/sites-available/echo2.sysattack.com.conf
$ a2ensite echo2.sysattack.com
$ systemctl reload apache2
$ curl http://echo2.sysattack.com/
hello
```

Now, lets make this site HTTPS and make new plain HTTP site which will redirect to secure HTTPS
```shell
# Generate LetsEncrypt certificate. Yes, thats very simple. We do not need --alises for this vhost, but we may need it if VirtualHost has ServerAlias'es and we want certificates for them.
$ a2certbot --create -d echo2.sysattack.com --aliases

# Convert to HTTPS
$ a2vhost --convert -d echo2.sysattack.com

# Make HTTP-to-HTTPS redirection
$ a2vhost --redirect -d echo2.sysattack.com

# Reload
$ systemctl reload apache2

# List all websites
$ a2vhost --list
```

In the end we got this config file 
<details>
<summary>/etc/apache2/sites-enabled/echo2.sysattack.com.conf</summary>

```
  <VirtualHost *:443> 
    ServerName echo2.sysattack.com 
    ServerAlias echo3.sysattack.com echo4.sysattack.com echo5.sysattack.com 
    DocumentRoot /var/www/virtual/echo2.sysattack.com 
    
    SSLEngine On 
    SSLCertificateFile /etc/letsencrypt/live/echo2.sysattack.com/fullchain.pem 
    SSLCertificateKeyFile /etc/letsencrypt/live/echo2.sysattack.com/privkey.pem 
    Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains" 
  </VirtualHost> 

  # auto-generated plain HTTP site for redirect
  <VirtualHost *:80> 
    ServerName echo2.sysattack.com 
    ServerAlias echo3.sysattack.com echo4.sysattack.com echo5.sysattack.com 
    DocumentRoot /var/www/virtual/echo2.sysattack.com 
    RewriteEngine On 
    RewriteCond %{HTTPS} !=on 
    RewriteCond %{REQUEST_URI} !^/\.well\-known 
    RewriteRule (.*) https://%{SERVER_NAME}$1 [R=301,L] 
  </VirtualHost> 
```
</details>

Optionally, you can add any directive to any VirtualHost. We will add comment:
```shell
# add directive
sudo bin/a2vhost --add '# This site is main https site'  -d echo2.sysattack.com --vhost '*:443'
```

## a2conf
### Examples <!-- omit in toc -->

For all examples we will use file 
[examples/example.conf](https://github.com/yaroslaff/a2conf/raw/master/examples/example.conf).
You can omit this parameter to use default `/etc/apache2/apache2.conf`.

Use `export PYTHONPATH=.` to use module if it's not installed.

Most useful examples:
```shell
$ bin/a2conf examples/example.conf --dump --vhost secure.example.com 
# examples/example.conf:15
<VirtualHost *:443> 
    # SSL site
    DocumentRoot /var/www/example 
    ServerName example.com # .... OUR TEST SITE ....
    ServerAlias www.example.com 1.example.com 2.example.com secure.example.com 
    DirectoryIndex index.html index.htm default.htm index.php 
    Options -Indexes +FollowSymLinks 
    SSLEngine On # SSL Enabled for this virtual host
    SSLCertificateFile /etc/letsencrypt/live/example.com/fullchain.pem 
    SSLCertificateKeyFile /etc/letsencrypt/live/example.com/privkey.pem 
    SSLCertificateChainFile /etc/letsencrypt/live/example.com/chain.pem 
</VirtualHost> 

# Only specific commands with --vhost filter
$ bin/a2conf examples/example.conf --vhost www.example.com:443 --cmd documentroot sslcertificatefile 
DocumentRoot /var/www/example
SSLCertificateFile /etc/letsencrypt/live/example.com/fullchain.pem

# Same output achieved with other way of filtering (based on SSLEngine directive)
$ bin/a2conf examples/example.conf --filter sslengine on --cmd documentroot sslcertificatefile
DocumentRoot /var/www/example
SSLCertificateFile /etc/letsencrypt/live/example.com/fullchain.pem

# All hostnames configured in this config file
$ bin/a2conf examples/example.conf --cmd servername serveralias --uargs
secure.example.com example.com www.example.com 2.example.com 1.example.com

# per-vhost summary with filtering
$ bin/a2conf examples/example.conf --cmd servername serveralias --vhfmt 'Host: {servername} Root: {documentroot} Cert: {sslcertificatefile}' --filter sslcertificatefile
Host: example.com Root: /var/www/example Cert: /etc/letsencrypt/live/example.com/fullchain.pem
```

You can get list of all available tokens for `--vhfmt` option in verbose mode (`-v` option).

## a2certbot
a2certbot utility used to quickly detect common [LetsEncrypt](https://letsencrypt.org/) configuration errors such as:
- DocumentRoot mismatch between VirtualHost and LetsEncrypt renew config file (e.g. if someone moved site content)
- RewriteRule or Redirect apache directives preventing verification
- DNS record points to other host or not exists at all
- And **ANY OTHER** problem (such as using wrong certificate path in apache or whatever). `a2certbot` 
simulates HTTP verification (If LetsEncrypt verification fails, `a2certbot` will fail too, and vice versa).

a2certbot does not calls LetsEncrypt servers for verification, so if you will use a2certbot to verify your 
configuration, you will not hit [failed validation limit](https://letsencrypt.org/docs/rate-limits/) 
(*5 failures per account, per hostname, per hour* at moment) and will not be blacklisted on LetsEncrypt site.

### Requesting new certificate and troubleshooting

Before requesting new certificates:
```shell
# Verify configuration for website for which you want to request certificate for first time.
bin/a2certbot --prepare -w /var/www/virtual/static.okerr.com/ -d static.okerr.com
=== manual ===
Info:
    (static.okerr.com) is local 37.59.102.26
    (static.okerr.com) Vhost: /etc/apache2/sites-enabled/static.okerr.com.conf:1
    (static.okerr.com) DocumentRoot: /var/www/virtual/static.okerr.com/
    (static.okerr.com) DocumentRoot /var/www/virtual/static.okerr.com/ matches LetsEncrypt and Apache
    (static.okerr.com) Simulated check match root: /var/www/virtual/static.okerr.com/
---

# You can verify all hostnames for site
bin/a2certbot --prepare -w /var/www/virtual/static.okerr.com/ -d static.okerr.com -d static2.okerr.com

# ... and finally simple main all-in-one command, it guesses aliases and root (command below does same as command above):
bin/a2certbot --prepare -d static.okerr.com --aliases
```

a2certbot can generate letsencrypt certificates in simple way (automatically detecting all aliases and 
DocumentRoot, but you can use -d instead of --aliases):
```
root@bravo:/home/xenon# a2certbot --create -d static.okerr.com --aliases
Create cert for static.okerr.com
RUNNING: certbot certonly --webroot -w /var/www/virtual/static.okerr.com/ -d static.okerr.com -d static2.okerr.com
Saving debug log to /var/log/letsencrypt/letsencrypt.log
Plugins selected: Authenticator webroot, Installer None
Obtaining a new certificate
Performing the following challenges:
http-01 challenge for static2.okerr.com
Using the webroot path /var/www/virtual/static.okerr.com for all unmatched domains.
Waiting for verification...
Cleaning up challenges

IMPORTANT NOTES:
 - Congratulations! Your certificate and chain have been saved at:
...
```

### Troubleshooting renew certificates

If `certbot renew` fails:
```shell
# Check (verify) ALL existing LetsEncrypt certificates (to check why 'certbot renew' may fail ):
root@bravo:/home/xenon# a2certbot 
=== /etc/letsencrypt/renewal/bravo.okerr.com.conf PROBLEM ===
Info:
    (bravo.okerr.com) Vhost: /etc/apache2/sites-enabled/okerr.conf:17
    LetsEncrypt conf file: /etc/letsencrypt/renewal/bravo.okerr.com.conf
    bravo.okerr.com is local 37.59.102.26
Problems:
    No DocumentRoot in vhost at /etc/apache2/sites-enabled/okerr.conf:17
---

# Verify only one certificate 
root@bravo:/home/xenon# a2certbot --host bravo.okerr.com
=== /etc/letsencrypt/renewal/bravo.okerr.com.conf PROBLEM ===
Info:
    (bravo.okerr.com) Vhost: /etc/apache2/sites-enabled/okerr.conf:17
    LetsEncrypt conf file: /etc/letsencrypt/renewal/bravo.okerr.com.conf
    bravo.okerr.com is local 37.59.102.26
Problems:
    No DocumentRoot in vhost at /etc/apache2/sites-enabled/okerr.conf:17
---
```


### a2certbot warnings (false positives)
a2certbot expects that requests to .well-known directory of HTTP (port 80) virtualhost must not be redirected.
If you have redirection like this: `Redirect 301 / https://example.com/` it will report problem:
```
Problems:
    Requests will be redirected: Redirect 301 / https://www.example.com/
```

Actually, this could be OK (false positive) and real verification from `certbot renew` may pass (if https 
site has same  DocumentRoot). To see if this is real problem or not see result for 'Simulated check'. 
If simulated check matches - website will pass certbot verification. 

To avoid such false positive, do not use such 'blind' redirection, better use this:
```
      RewriteCond %{REQUEST_URI} !^/\.well\-known        
      RewriteRule (.*) https://%{SERVER_NAME}$1 [R=301,L]
```
This code in `<VirtuaHost *:80>` context will redirect all requests to HTTPS site EXCEPT LetsEncrypt verification 
requests.

## a2okerr
a2okerr is useful only if you are using [okerr](https://okerr.com/): free and open source hybrid (host/network) monitoring system. 

[Okerr](https://okerr.com/) is like [nagios](https://www.nagios.org/) or [zabbix](https://www.zabbix.com/), but can perform network checks 
from remote locations, has tiny and optional local client  which can run from cron, has powerful logical
indicators (notify me only if more then 2 servers are dead, notify me if any problem is not fixed for more then 30 minutes, ...), 
public status pages (like https://status.io/ but free), fault-tolerant sites 
(okerr will redirect dynamic DNS record to backup server if main server is dead, and point it back to main server
 when it's OK), supports [Telegram](https://telegram.org/) and has many other nice features. 
 
You can use it as free service (like wordpress or gmail) or you can install okerr server on your own linux machine 
from  [okerr git repository](https://gitlab.com/yaroslaff/okerr-dev/).

You will need to install small [okerrupdate](https://gitlab.com/yaroslaff/okerrupdate) package to use a2okerr: `pip3 install okerrupdate`.

a2okerr discovers all https sites from apache config and creates SSL-indicator in your okerr project 
for each website. You will get alert message to email and/or telegram if any of your https sites has any problem 
(certificate is not updated in time for any reason and will expire soon or already expired. 
Website unavailable for any reason). If you have linux server or website - you need okerr.

```shell
# Create indicator for all local https websites. If indicator already exists, HTTP error 400 will be received - this is OK.
a2okerr

# alter prefix, policy and description
a2okerr --prefix my:prefix: --policy Hourly --desc "I love okerr and a2okerr"

# do not really create indicators, just dry run
a2okerr --dry
```


