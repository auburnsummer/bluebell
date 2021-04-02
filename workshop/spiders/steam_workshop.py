"""
notes on logging into steam

STEP 1

POST http://store.steampowered.com/login/getrsakey

It’s a form type input:
 - username: the username

STEP 2

Check success is true!

You get:

 - publickey_mod
-  publickey_exp
- Timestamp
- token_gid

STEP 3

Calculate the hashy thing

Call RSA.getPublicKey on the public key mod and the public key exponent

Then encrypt the password with this public key

Also make sure you keep the timestamp with you

STEP 4

FINALLY:

Call http://store.steampowered.com/login/dologin

password: the encrypted password in step 3
username
rsatimestamp
remember_login = false

THESE ARE ALL BLANK USUALLY
twofactorcode
loginfriendlyname
captchagid
captcha_text
emailsteamid

THIS IS BLANK UNLESS STEAM GUARD ACTIVATES
emailauth

If steam guard activates you have to get the password from your email and insert into that field.

nvm you can just disable steam guard and then you don't have to worry about this


STEP 5

Now you get transfer_parameters with these:

 steamid = this is the steam id I guess
 token_secure = I think we pass this when we go to other sites???
auth = not sure what this is
remember_login

STEP 6

Make cookies like this:

steamLoginSecure = steamid||token_secure
steamMachineAuth{{steamid}} = auth

And put those cookies in your thing!
"""

import scrapy
import os
import rsa
import base64
import json
from scrapy.shell import inspect_response
import subprocess


def make_curl_subprocess_form(d):
    accum = []
    for k, v in d.items():
        accum.append("--form")
        accum.append(f"{k}={v if v is not None else ''}")
    return accum



class WorkshopListingSpider(scrapy.Spider):
    name = "WorkshopListing"

    def start_requests(self):
        # get user + password from env variables
        self.user = os.environ.get("STEAM_USER")
        self.password = os.environ.get("STEAM_PASSWORD")

        # get RSA public key from steam...
        # we're using curl for this and not scrapy because...
        # ...steam auth requires a specific type of HTTP POST behaviour that curl supports
        # and scrapy doesn't.
        # specifically, we need to respond to a HTTP POST 302 with  another POST on the
        # same connection. scrapy always responds to a HTTP POST 302 with a GET instead.
        user = self.user
        completed = subprocess.run([
            "curl", "--request", "POST", "--url",
            "http://store.steampowered.com/login/getrsakey",
            "--location", "--post302", "--form", f"username={user}"
        ] + make_curl_subprocess_form(
            {'username' : user}
        ), capture_output=True, encoding='utf-8')
        res = json.loads(completed.stdout)

        print(res)
        if res['success'] is False:
            print("Unexpected error")
            print(res)
            raise

        # now make an encrypted password
        rsa_modulus = int(res['publickey_mod'], 16)
        rsa_exponent = int(res['publickey_exp'], 16)
        pk = rsa.PublicKey(rsa_modulus, rsa_exponent)
        encrypted = rsa.encrypt(self.password.encode('utf-8'), pk)
        payload = base64.b64encode(encrypted)

        # ALRIGHT now we can login!
        # a whole lotta empty forms... idk why steam wants them but eh
        curl_login_command = [
            "curl", "--request", "POST", "--url", "http://store.steampowered.com/login/dologin",
            "--location", "--post302"
        ] + make_curl_subprocess_form({
            'password' : payload.decode("utf-8"),
            'username' : user,
            'twofactorcode' : None,
            'emailauth' : None,
            'loginfriendlyname' : None,
            'captchagid' : None,
            'captcha_text' : None,
            'emailsteamid' : None,
            'rsatimestamp' : res['timestamp'],
            'remember_login' : 'false'
        })

        login_completed = subprocess.run(curl_login_command, capture_output=True, encoding='utf-8')
        lres = json.loads(login_completed.stdout)
        transfer_params = lres['transfer_parameters']
        # once we've logged in, we can make cookies! delicious
        self.trefoils = {
            'steamLoginSecure' : f"{transfer_params['steamid']}||{transfer_params['token_secure']}",
            f"steamMachineAuth{transfer_params['steamid']}" : transfer_params['auth']
        }

        game_id = getattr(self, 'game_id', None)
                
        urls = [
            f"https://steamcommunity.com/workshop/browse/?appid={game_id}&browsesort=mostrecent&section=readytouseitems&actualsort=mostrecent&p=1"
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse, cookies=self.trefoils)

            
    def parse(self, response):
        ids = response.xpath("//div[contains(@class, 'workshopItemPreviewHolder')]/parent::*/@data-publishedfileid").getall()
        for id in ids:
            yield {
                'id' : id,
                'game_id' : getattr(self, 'game_id', None)
            }
        
        next_page = response.xpath('//div[normalize-space(@class)="workshopBrowsePagingControls"]/a/@href').getall()
        # get last item
        for page in next_page:
            yield scrapy.Request(url=page, callback=self.parse)