from sparkpost import SparkPost
from bs4 import BeautifulSoup
from time import sleep
import pandas as pd
import argparse
import textwrap
import random
import sys
import os
import re

_sp_ = None

# Print iterations progress
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█'):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
    # Print New Line on Complete
    if iteration == total: 
        print()

def query_yes_no(question, default="no"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        print(question + prompt, end="")
        choice = input().lower()

        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            print("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n')")

def sparkpost(API):
    global _sp_
    _sp_ = SparkPost(API)

def transform_img_to_inline(html):
    # TODO: use beautifullsoup to look for all imgs and turn them into inline images
        
    soup = BeautifulSoup(html, 'html.parser')
    soup.find_all('img')
    images = soup.find_all('img')
    inlineImg = { "type" : None, "name" : None, "filename" : None }
    ret = []
    try:
        for img in images:
            src = img.get('src')
            if "https://" in src:
                # "HTTPS found", src, "not substituting it"
                continue
            
            if src.rfind("/") == -1:
                raise Exception("wrong format with image source! A source path was expected but found", src, "instead!")

            inlineImg["type"] = "image/"+src.split('.')[-1]
            inlineImg["name"] = src[src.rfind("/")+1:src.rfind(".")]
            inlineImg["filename"] = src
            html = html.replace(src,"cid:"+inlineImg["name"])
            ret.append(inlineImg.copy())

    except Exception as e:
        print(e)

    print("[ INLINE IMAGES ]:", len(ret), "where found and substituted!")

    return html, ret

def transmit_email(from_email, reply_to, recipient, text, message, subject, tags, format="HTML", inline_images=None):
    global _sp_
    #print(subject)
    subject = random.choice(subject)
    #print(subject)

    if format == "PLAIN_TEXT":
        response = _sp_.transmissions.send(
            recipients=[recipient],
            text = text,
            reply_to=reply_to,
            from_email=from_email,
            subject=subject,
            track_opens=True,
            track_clicks=True,
            substitution_data = tags,
        )
    else:
        response = _sp_.transmissions.send(
            recipients=[recipient],
            html=message,
            text = text,
            reply_to=reply_to,
            from_email=from_email,
            subject=subject,
            track_opens=True,
            track_clicks=True,
            substitution_data = tags,
            inline_images=inline_images,
        )

    return response

def get_tags(data):
    m = re.search('(\{\{.+\}\})', data)
    tags = m.group(0).split()
    tags = [t[2:-2] for t in tags]
    return tags

def main():

    parser = argparse.ArgumentParser(prog="Hothead Email Sender with SparkPost", 
            usage="Loads an email template and send to people in a list, the list can be either a pre-formated CSV or recipment list from sparkpost",
            description=textwrap.dedent('''\
            How to properly use this script:
            --------------------------------
                Loads up a list of emails.
                Loads an email template.
                Send this email template to
                 all your recipments.
                You can see a template doc
                 for the email along with
                 this script.
             '''),
            epilog="Developed by @developerscoppio", 
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )

    parser.add_argument('--A', type=str, default=None,
        help="just the path for the file and the filename WITHOUT the file extension")
    parser.add_argument('--B', type=str, default=None,
        help="just the path for the file and the filename WITHOUT the file extension")
    parser.add_argument('--csv', nargs='?', type=str, default=None, 
        help="csv file with email recipments")
    parser.add_argument('--reply', type=str, default='reply_to@email.com', 
        help="reply account, must be a verified one!")
    parser.add_argument('--from_email', type=str, default='John Doe <reply_to@email.com>', 
        help="sending account, must be a verified one!")
    parser.add_argument('--spark', type=str, 
        help="name of the mailing list saved at sparkpost")
    parser.add_argument('--mode',  nargs='?' ,choices=['test', 'live', 'schedule'], const='live', default='test',
        help="mode in which the system will run")
    parser.add_argument('--format',  nargs='?' ,choices=['HTML', 'PLAIN_TEXT'], const='PLAIN_TEXT', default='HTML',
        help="mode in which the emails will be sent")

    args = parser.parse_args()


    print("""Welcome to The Hothead Email Sender, a Sparkpost+Python script for bulk mail.""")

    print("STARTING")
    SPARKPOST_API_KEY = None
    print("[ MODE ]:", args.mode)
    print("[ API KEY ]: ", end="")
    try:
        with open("sparkpost_key.txt") as f:
            SPARKPOST_API_KEY = f.read()
            print( SPARKPOST_API_KEY)
    except Exception as e:
        print("sparkpost_key.txt could not be found or its content is corrupted. >>> Script terminated!!!")
        return

    if args.mode == 'live':
        sparkpost(SPARKPOST_API_KEY)

    reply_to =  args.reply
    from_email = args.from_email

    print("[ REPLY TO ]:", reply_to)
    print("[ FROM EMAIL ]:", from_email)

    A = {"subject" : None, "message" : None, "inline_images" : None, "text" : None, "tags" : None}
    B = {"subject" : None, "message" : None, "inline_images" : None, "text" : None, "tags" : None}
    
    ANB = False

    template = args.A
    if args.format == "HTML":
        print("[ HTML TEMPLATE A ]: ", end="")
        try:
            with open(template+'.html') as f:
                A["message"] = f.read()
                print(template+".html LOADED")
                A["message"], A["inline_images"] = transform_img_to_inline(A["message"])
        except Exception as e:
            print("FAILED TO LOAD")
            raise Exception(e)

    print("[ TXT TEMPLATE A ]: ", end="")
    try:        
        with open(template+'.txt') as f:
            text = f.readlines()
            print(template+".txt LOADED")
            A["subject"] = []
            i = 0
            for line in text:
                if "#" in line[0]:
                    print("[ SUBJECT A ]:", line[1:].strip())
                    A["subject"].append(line[1:].strip())
                else:
                    break
            
            if len(A["subject"]) == 0:
                print("SUBJECT NOT FOUND")
                raise Exception("File does not contain the expected #subject line as first line")

            A["text"] = ''.join(text[len(A["subject"]):])
            A["tags"] = get_tags(A["text"])

    except Exception as e:
        print("FAILED TO LOAD")
        raise Exception(e)

    if args.B:
        ANB = True
        template = args.B
        if agrs.format == "HTML":
            print("[ HTML TEMPLATE B ]: ", end="")
            try:
                with open(template+'.html') as f:
                    B["message"] = f.read()
                    B["message"], B["inline_images"] = transform_img_to_inline(B["message"])
                    print(template+".html LOADED")
            except Exception as e:
                print("FAILED TO LOAD")
                raise Exception(e)

        print("[ TXT TEMPLATE B ]: ", end="")
        try:        
            with open(template+'.txt') as f:
                text = f.readlines()
                print(template+".txt LOADED")
                B["subject"] = []
                for line in text:
                    if "#" in line[0]:
                        print("[ SUBJECT B ]:", line[1:].strip())
                        B["subject"].append(line[1:].strip())
                    else:
                        break
                
                if len(B["subject"]) == 0:
                    print("SUBJECT NOT FOUND")
                    raise Exception("File does not contain the expected #subject line as first line")

                B["text"] = ''.join(text[len(B["subject"]):])
                B["tags"] = get_tags(B["text"])

        except Exception as e:
            print("FAILED TO LOAD")
            raise Exception(e)

    recipment_list = None
    print("[ EMAIL LIST ]: ", end="")
    try:
        if args.spark:
            print(args.spark, "- sparkpost email list loaded")
        elif args.csv:
            recipment_list = pd.read_csv(args.csv)
            recipment_list.columns = [i.lower() for i in recipment_list.columns]
            print(args.csv, "LOADED")
            print("[ EMAIL RECIPMENT ]:", len(recipment_list))
        else:
            raise Exception("No recipment list loaded! Stoping script")

    except Exception as e:
        print(e)
        return

    print("[ EMAIL MODE ]:", args.format)


    if not query_yes_no(">>>Do you want to continue?"):
        print("Cancelling the process")
        return

    tot = 0;
    snt = 0;
    fail = 0;
    l = len(recipment_list)
    # Initial call to print 0% progress   
    print("")
    printProgressBar(tot, l, prefix = 'Progress:', suffix = 'Sent', length = 50)

    for i in range(len(recipment_list)):
        chosen = A
        temp = {}
        if ANB:
            chosen = random.choice([A, B])

        for tag in chosen["tags"]:
            temp[tag] =  recipment_list.iloc[i][tag.lower()]
        
        email = recipment_list.iloc[i]["e-mail"]

        if args.mode == "live":
            resp = None

            try:

                resp = transmit_email(from_email, reply_to, email, chosen["text"], chosen["message"], chosen["subject"], temp, format=args.format, 
                    inline_images=chosen["inline_images"])
                snt += 1
            except Exception as e:
                resp = {'total_accepted_recipients' : 0, 'id': 0 }
                fail += 1
            
            with open("output_log.txt", 'a') as f:
                f.write(str(resp['total_accepted_recipients'])+','+str(resp['id']))       

            printProgressBar(tot, l, prefix = 'Progress:', suffix = 'Sent', length = 50)

            tot += resp['total_accepted_recipients']
            
        else:
            tot += 1
            sleep(0.2)
            printProgressBar(tot, l, prefix = 'Progress:', suffix = 'Sent', length = 50)

    print("")
    print("[ EMAILS SENT     ]:", snt)
    print("[ EMAILS ACCEPTED ]:", tot)
    print("[ EMAILS FAIED    ]:", fail)

if __name__ == '__main__':
    main()