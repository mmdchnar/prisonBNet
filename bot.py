from re import findall
from time import sleep, strftime
from requests import get
from textwrap import wrap
from dotenv import load_dotenv
from os import remove, mkdir, getenv
from os.path import join as join_path, dirname, abspath
from shutil import make_archive, rmtree


from redbox import EmailBox
from redmail import EmailSender
from redbox.query import UNSEEN

from telethon import TelegramClient
from telethon.sessions import StringSession


load_dotenv()

# Define Privates 
EMAIL = getenv('EMAIL') # Bot email address
PASS = getenv('PASS') # Bot email password
API_ID = getenv('API_ID') # API_id
API_HASH = getenv('API_HASH') # API_hash
SESSION = getenv('SESSION') # String Session 
OWNER = getenv('OWNER') # Owner email

BASE_DIR = dirname(abspath(__file__))
MEDIA_DIR = join_path(BASE_DIR, "media")


# Connect to Gmail
mailbox = EmailBox(
    host="imap.gmail.com", 
    port=993,
    username=EMAIL,
    password=PASS
)["INBOX"]


send_mail = EmailSender(
    host="smtp.gmail.com", 
    port=587,
    username=EMAIL,
    password=PASS
).send


# Define a function for read inbox and return the unread messages
def get_msgs():
    msgs = []
    for msg in mailbox.search(UNSEEN):
        msg.read()
        msgs.append(msg)
    return msgs


# Start the bot
if __name__ == '__main__':
    print('Ready to response...')

    bot = TelegramClient(StringSession(SESSION), API_ID, API_HASH).start() # Connect to Telegram
    bot_sync = bot.loop.run_until_complete # Bypass asynco client

    while True: # Define a inifity loop to response email's
        try: # Define a try-except option for error's
            msgs = get_msgs() # Get unread messages
            counter = 1
            for msg in msgs:
                sub = msg.subject.lower().split(' ') # Split subject to easy find command's
                if sub[0] == 'help': # Define the help command
                    with open(join_path(MEDIA_DIR, 'templates', 'help.html'), 'r') as html_file:
                        send_mail(
                            'Prison Break Tutorial', 
                            receivers=[msg.from_], 
                            html=html_file.read(), 
                            body_params={
                                'email_address': EMAIL,
                            }
                        )
                    print('Help ~> ', msg.from_)


                elif sub[0] == 'get' and msg.from_.split('<')[1][:-1] == OWNER: # Define get messages command (owner only)
                    file_name = join_path(BASE_DIR, f'{sub[2]}_{strftime("%H-%M_%d-%m-%y")}_{counter}.txt')
                    with open(file_name, 'w') as _f:
                        for message in bot.iter_messages(sub[2], limit=int(sub[1])):
                            _f.write('\n'.join(wrap(message.message, 50)))
                            _f.write('\n\n' + '-'*60 + '\n\n') # Write a line between messages

                    # send_mail the file of messages
                    send_mail(
                        f'{sub[1]} messages from @{sub[2]}',
                        receivers=[msg.from_],
                        text = 'Dear ' + msg.from_.split('<')[0] + 'Here is the file of messages: ',
                        attachments=[file_name]
                    )

                    counter += 1
                    remove(file_name) # Remove the file
                    print(f'{sub[1]} messages from @{sub[2]}', 'to', msg.from_)


                elif sub[0] in ['mtproto', 'mtproxy']: # Define Mtproto proxy command
                    channels = ['hack_proxy', 'NetAccount']

                    file_name = join_path(BASE_DIR, f'mtproto_{strftime("%H-%M_%d-%m-%y")}_{counter}.txt')
                    with open(file_name, 'w') as _f:
                        # Write proxies to file
                        for channel in channels:
                            for message in bot.iter_messages(channel, limit=30):
                                proxies = findall(
                                    r'((https://t\.me/|tg://)proxy\?server=.+&port=[0-9]{0,5}&secret=[a-z0-9A-Z_]+)(\s|\n)?',
                                    message.message
                                )

                                for proxy in proxies:
                                    _f.write(proxy[0])
                                    _f.write('\n\n' + '-'*60 + '\n\n') # Write a line between messages

                    # send_mail the file of proxies
                    send_mail('Mtproto porxies',
                        receivers=[msg.from_],
                        text = 'Dear ' + msg.from_.split('<')[0] + 'Here is the proxies: ',
                        attachments=[file_name]
                    )

                    counter += 1
                    remove(file_name) # Remove the file
                    print('sent mtproto to', msg.from_)


                elif sub[0] == 'sstp': # Define SSTP server command

                    file_name = join_path(BASE_DIR, f'sstp_{strftime("%H-%M_%d-%m-%y")}_{counter}.txt')
                    with open(file_name, 'w') as _f:
                        # Write servers to file
                        request = get('https://vpngate.net')
                        servers = findall(
                            r'''SSTP Hostname :<br /><b><span style='color: #006600;' >(.*?)</span>''',
                            request.text
                        )
                        _f.write('\n'.join(servers))

                    # send_mail the file of servers
                    send_mail('Open-SSTP servers',
                        receivers=[msg.from_],
                        text = 'Dear ' + msg.from_.split('<')[0] + 'Here is the SSTP servers: ',
                        attachments=[file_name]
                    )

                    counter += 1
                    remove(file_name) # Remove the file
                    print('sent sstp to', msg.from_)


                elif sub[0] == 'config': # Define HTTP config command
                    channels = ['mypremium98', 'NetAccount', 'injector2', 'barcode_tm', 'Free_Nettm']

                    config_name = f'config_{strftime("%H-%M_%d-%m-%y")}_{counter}'
                    mkdir(join_path(BASE_DIR, config_name))

                    # Write proxies to file
                    for channel in channels:
                        mkdir(join_path(config_name, channel)) # Make sub-folder
                        for message in bot.iter_messages(channel, limit=20):
                            if message.file is not None and message.file.name is not None:
                                if message.file.name[-3:] in ['.hc', 'ehi']:
                                    bot_sync(
                                        message.download_media(
                                            join_path(config_name, channel, message.file.name)
                                        )
                                    )
                    make_archive(config_name, 'zip', join_path(BASE_DIR, config_name))

                    # send_mail the file of configs
                    send_mail(
                        'HTTP Config',
                        receivers=[msg.from_],
                        text = 'Dear ' + msg.from_.split('<')[0] + 'Here is the configs: ',
                        attachments=[f'{config_name}.zip']
                    )

                    counter += 1
                    remove(join_path(BASE_DIR, f'{config_name}.zip'))
                    rmtree(join_path(BASE_DIR, config_name), ignore_errors=True) # Remove the folder
                    print('sent config to', msg.from_)


                elif sub[0] in ['v2ray', 'vmess', 'vless', 'trojan']: # Define V2ray server command
                    channels = ['v2rayng_org', 'NetBox2', 'freelancer_gray']

                    file_name = join_path(BASE_DIR, f'v2ray_{strftime("%H-%M_%d-%m-%y")}_{counter}.txt')
                    with open(file_name, 'w') as _f:
                        # Write servers to file
                        for channel in channels:
                            for message in bot.iter_messages(channel, limit=30):
                                servers = findall(
                                    r"((vmess|trojan|vless|trojan-go)://[a-z0-9A-Z=\%\@\#\-\&\/\:\.\?]+)(\s|\n)?",
                                    message.message
                                )

                                for server in servers:
                                    _f.write(server[0])
                                    _f.write('\n\n' + '-'*60 + '\n\n') # Write a line between messages

                    # send_mail the file of servers
                    send_mail(
                        'V2ray servers',
                        receivers=[msg.from_],
                        text = 'Dear ' + msg.from_.split('<')[0] + 'Here is the V2ray servers: ',
                        attachments=[file_name]
                    )

                    counter += 1
                    remove(file_name)
                    print('sent v2ray to', msg.from_)


                elif sub[0] == 'apk': # Define APK link command
                    drive = {
                        'injector': 'https://drive.google.com/file/d/1Wc5ocL4feKtN1oIIenU6SGxlFdImDddS',
                        'plugin': 'https://drive.google.com/file/d/1D4aJ8xSQfl45bvXEM5S3L5LEaOfX3Hlp',
                        'custom': 'https://drive.google.com/file/d/1ir2qfJija1NxFBzubLikPd5BHBqg9GXS',
                        'v2ray': 'https://drive.google.com/file/d/1Gj_jeOaAqwLDqtoQU_9DiXLY1gvucT06',
                        'every': 'https://drive.google.com/file/d/1JVzCw0hNHb259T14xPA7xOuOXlQT7bCQ',
                        'sstp': 'https://drive.google.com/file/d/11Pd9VYYQjdKnS3nYXZaUqcvV7y6Z1xuF',
                        'ultrasurf': 'https://drive.google.com/file/d/1UY_aF7N8hTNVxiv3Af5sIMmP6wilf6qe'
                    }

                    bayan = {
                        'injector': 'https://bayanbox.ir/download/2423418780594137086/HTTP-Injector-5.7.1.apk',
                        'plugin': 'https://bayanbox.ir/download/4779056004617586889/V2Ray-plugin-v1.5.1.apk',
                        'custom': 'https://bayanbox.ir/download/6627542560266652761/HTTP-Custom-v3.10.28.apk',
                        'v2ray': 'https://bayanbox.ir/download/2026735872615532411/v2rayNG-v1.7.20.apk',
                        'every': 'https://bayanbox.ir/download/5857325977849443639/Every-Proxy-9.2.apk',
                        'sstp': 'https://bayanbox.ir/download/4488497287460583704/Open-SSTP-v1.5.7.1.apk',
                        'ultrasurf': 'https://bayanbox.ir/download/9064590006485030472/Ultrasurf-v2.3.0.apk'
                    }

                    if sub[1] in drive and sub[1] != 'plugin':
                        html = f'<p>Dear <b>{msg.from_.split("<")[0]}</b>\nHere is the APK links:</p><p></p>\
                            <p><b><a href="{drive[sub[1]]}">Download from Google Drive</a></b></p>\
                                <p><b><a href="{bayan[sub[1]]}">Download from Bayan Box</a></b></p>'

                        if sub[1] == 'injector':
                            html += f'<br><p><b><a href="{drive["plugin"]}">V2ray-Plugin Download from Google Drive</a></b></p>\
                                <p><b><a href="{bayan["plugin"]}">V2ray-Plugin Download from Bayan Box</a></b></p></br>'

                        # send_mail the APK file
                        send_mail(
                            f'APK {sub[1]}',
                            receivers=[msg.from_],
                            html=html
                        )

                        print(f'sent {sub[1]} to', msg.from_)


        # Define the Keyboard Interrupt detector to stop the bot
        except KeyboardInterrupt:
            print('\n\n|-----Bot stoped-----|')
            break
        # Define an except to pass other error's to continue bot if get an error 
        except Exception as error:
            print(error)
        except:
            pass
        
        sleep(10)
