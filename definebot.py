import tweepy
from bs4 import BeautifulSoup
import requests
import json
import urllib.request
import re
import time
import os 
import re
from google_images_search import GoogleImagesSearch
import csv

from tweepy_keys import *

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)

def addPTracking(screen_name):
    with open(r'C:\Users\noahk\DefineEveryWordBot\PTracking.csv', mode='r') as infile:
        reader = csv.reader(infile)
        reader = list(reader)
        pdi = {rows[0]:int(rows[1]) for rows in reader}

        if not onBlockList(screen_name):
            if screen_name in pdi:
                if pdi[screen_name] >= 2:
                    addBlockList(screen_name)
                    print("BLOCKING USER ", screen_name, " DUE TO REPEATED PROFRANITY")
                    pdi.pop(screen_name, None)
                else:
                    pdi[screen_name] += 1
            else:
                pdi[screen_name] = 1

    with open(r'C:\Users\noahk\DefineEveryWordBot\PTracking.csv', 'w') as outfile:
        for key in pdi.keys():
            outfile.write("%s,%s\n"%(key,pdi[key]))

def onBlockList(screen_name):
    with open(r'C:\Users\noahk\DefineEveryWordBot\blocklist.txt', 'r') as read_obj:
        for line in read_obj:
            if screen_name in line:
                return True
    return False

def addBlockList(screen_name):
    b = open(r'C:\Users\noahk\DefineEveryWordBot\blocklist.txt', 'a')
    if not onBlockList(screen_name):
        b.write(screen_name)
        print("User ", screen_name, " added to block list.")
    else:
        print("User ", screen_name, " already on block list.")
    b.close()

def killCheck(phrase):
    k = open(r'C:\Users\noahk\DefineEveryWordBot\kill.txt', 'r')
    klist = []

    for line in k:
        klist.append(line.strip())
    
    phrase = ''.join(e for e in phrase if e.isalnum())

    for word in klist:
        if word in phrase:
            return True

    return False

def pCheck(phrase):
    p = open(r'C:\Users\noahk\DefineEveryWordBot\profanity.txt', 'r')
    plist = []

    for line in p:
        plist.append(line.strip())

    for word in phrase.split():
        if word in plist:
            return True

    return False
    
def defineWordBS(word): #beautifulsoup version, web-scrapes in case of TypeError exception
    try:
        page = requests.get("https://www.merriam-webster.com/dictionary/" + str(word))
        soup = BeautifulSoup(page.content, 'html.parser')
        info = soup.find(class_="vg")
        text = info.find(class_='dtText').get_text()
        actual = soup.find(class_="hword").get_text()
        text=text[2:]
        word_type = soup.find(class_='fl').get_text()

        if actual == word:
            return(str(word) + ' (' + word_type + '): ' + text)
        else:
            return(str(word) + " --> " + actual + ' (' + word_type + '): ' + text)
    except:
            return str(word) + ": We're not sure about this one... or at least Merriam Webster isn't..."


def defineWord(word): #defines word directly from merriam-webster api if possible
    keyfile = open(r"C:\Users\noahk\DefineEveryWordBot\mwkey.txt", 'r')
    keys = keyfile.readline()
    word = str(word)
    result=[]
    urlfrmt = "https://dictionaryapi.com/api/v3/references/collegiate/json/"+word+"?key=" + keys
    response = urllib.request.urlopen(urlfrmt)
    jsStruct = json.load(response)
    if jsStruct == []:
        return word + ": We're not too sure about this one... or at least Merriam Webster isn't..."

    for meaning in jsStruct:
        try:
            definitions = meaning['shortdef']
        except TypeError:
            print("---------Unknown Word, Rerouting to Scraper--------")
            return defineWordBS(word)

        page = requests.get("https://www.merriam-webster.com/dictionary/" + str(word))
        soup = BeautifulSoup(page.content, 'html.parser')

        actual = soup.find(class_="hword").get_text()

        if actual != word:
            word = word + " --> " + actual

        for i, eachDef in enumerate(definitions, 1):
            result.append(str(i) + ". " + eachDef)
        try:
            return (word + ' ('+meaning['fl']+'): ' + '\n' +
                    result[0] + '\n' +
                    result[1] + '\n' +
                    result[2])
        except:
            try:
                return (word + ' ('+meaning['fl']+'): ' + '\n' +
                        result[0] + '\n' +
                        result[1])
            except:
                try:
                    return (word + ' ('+meaning['fl']+'): ' + '\n' +
                            result[0])
                except:
                    try:
                        return word + ': ' + soup.find(class_="cxl-ref").get_text()
                    except:
                        return word + ": We're not too sure about this one... or at least Merriam Webster isn't..."
                


def getMediaID(word): #downloads and retrieves the media ID for an image of a requested word
    d = os.listdir(r'C:\Users\noahk\DefineEveryWordBot\twitter-images')
    if len(d)!=0:
        for f in d:
            os.remove(r'C:\Users\noahk\DefineEveryWordBot\twitter-images' + "\\"+ f)
    keyfile = open(r"C:\Users\noahk\DefineEveryWordBot\gkey.txt", 'r')
    gkey = keyfile.readline()
    cx_file = open(r"C:\Users\noahk\DefineEveryWordBot\cx_id.txt", 'r')
    cx_id = str(cx_file.readline())

    keyfile2 = open(r"C:\Users\noahk\DefineEveryWordBot\gkey2.txt", 'r')
    gkey2 = keyfile2.readline()
    cx_file2 = open(r"C:\Users\noahk\DefineEveryWordBot\cx_id2.txt", 'r')
    cx_id2 = str(cx_file2.readline())

    try:
        gis = GoogleImagesSearch(gkey, cx_id)
        # define search params:
        _search_params = {
            'q': word,
            'num': 1,
            'safe': 'off',
            # 'fileType': 'jpg|gif|png',
            # 'imgType': 'clipart|face|lineart|news|photo',
            # 'imgSize': 'huge|icon|large|medium|small|xlarge|xxlarge',
            # 'imgDominantColor': 'black|blue|brown|gray|green|pink|purple|teal|white|yellow'
        }

        # this will search and download:
        gis.search(search_params=_search_params, path_to_dir=r'C:\Users\noahk\DefineEveryWordBot\twitter-images')

        img = os.listdir(r'C:\Users\noahk\DefineEveryWordBot\twitter-images')[0]
        img_file = r'C:\Users\noahk\DefineEveryWordBot\twitter-images' + "\\" + img

        media_list = []

        p = open(r'C:\Users\noahk\DefineEveryWordBot\profanity.txt', 'r')
        plist = []
        for line in p:
            plist.append(line.strip())

        if word not in plist:
            response = api.media_upload(img_file)
            media_list.append(response.media_id_string)

        return media_list
    except:
        try:
            gis = GoogleImagesSearch(gkey2, cx_id2)
            _search_params = {
            'q': word,
            'num': 1,
            'safe': 'off',
            # 'fileType': 'jpg|gif|png',
            # 'imgType': 'clipart|face|lineart|news|photo',
            # 'imgSize': 'huge|icon|large|medium|small|xlarge|xxlarge',
            # 'imgDominantColor': 'black|blue|brown|gray|green|pink|purple|teal|white|yellow'
        }

            # this will search and download:
            gis.search(search_params=_search_params, path_to_dir=r'C:\Users\noahk\DefineEveryWordBot\twitter-images')

            img = os.listdir(r'C:\Users\noahk\DefineEveryWordBot\twitter-images')[0]
            img_file = r'C:\Users\noahk\DefineEveryWordBot\twitter-images' + "\\" + img

            media_list = []

            p = open(r'C:\Users\noahk\DefineEveryWordBot\profanity.txt', 'r')
            plist = []
            for line in p:
                plist.append(line.strip())

            if word not in plist:
                response = api.media_upload(img_file)
                media_list.append(response.media_id_string)

            return media_list
        except:
            return []


def deleteImage():
    d = os.listdir(r'C:\Users\noahk\DefineEveryWordBot\twitter-images')
    if len(d)==1:
        img = d[0]
        img_file = r'C:\Users\noahk\DefineEveryWordBot\twitter-images' + "\\" + img
        os.remove(img_file)

def makeTweets(word,most_recent_id): #tweets reply with definition, and tweets out own definition
    phrase = "In case you didn't know..."
    definition = defineWord(word)
    reply_definition = definition
    media_id = getMediaID(word)
    print("-------------REPLYING WITH:--------------")
    if len(reply_definition) <= 239:
        if reply_definition.split()[1] == "We're":
            api.update_status(status = reply_definition, in_reply_to_status_id = most_recent_id, auto_populate_reply_metadata=True)
            print(reply_definition)
        else:
            api.update_status(status = phrase + '\n' + reply_definition, in_reply_to_status_id = most_recent_id, media_ids=media_id, auto_populate_reply_metadata=True)
            print(reply_definition)
    else:
        first_definition = reply_definition[:239]
        last_id = api.update_status(status = phrase + '\n' + first_definition, in_reply_to_status_id = most_recent_id, media_ids=media_id, auto_populate_reply_metadata=True).id_str
        print(first_definition)
        leftover = reply_definition[239:]
        new_tweets = len(leftover)//280 + 1
        last_length = len(leftover) % 280

        print('Beginning reply chain: @' + 'fckeveryword' + ' ' + phrase + '\n' + first_definition)
        for i in range(new_tweets):
            if i == new_tweets - 1:
                reply_tweet = leftover[:last_length]
                api.update_status(status = reply_tweet, in_reply_to_status_id = last_id)
                print(reply_tweet)
            else:
                reply_tweet = leftover[:280]
                leftover = leftover[280:]
                last_id = api.update_status(status = reply_tweet, in_reply_to_status_id = last_id).id_str
                print(reply_tweet)
    
    print("------------- TWEETING OUT --------------")

    if len(definition) <= 247-len(word):
        tweet_string = "Yay! It's time to fuck " + word + "!" + '\n' + definition
        api.update_status(status = tweet_string, media_ids=media_id)
        print(tweet_string)
        print("------------FINISHED-------------")
    else:
        first_definition = definition[:247-len(word)]
        leftover = definition[247-len(word):]

        new_tweets = len(leftover)//280 + 1
        last_length = len(leftover) % 280

        tweet_string = "Yay! It's time to fuck " + word + "!" + '\n' + first_definition

        last_id  = api.update_status(status = tweet_string, media_ids=media_id).id_str

        print("Beginning reply chain: " + tweet_string)

        for i in range(new_tweets):
            if i == new_tweets - 1:
                reply_tweet = leftover[:last_length]
                api.update_status(status = reply_tweet, in_reply_to_status_id = last_id)
                print(reply_tweet)
            else:
                reply_tweet = leftover[:280]
                leftover = leftover[280:]
                last_id = api.update_status(status = reply_tweet, in_reply_to_status_id = last_id).id_str
                print(reply_tweet)

        print("------------FINISHED-------------")

    deleteImage()
    return 

class MyStreamListener(tweepy.StreamListener): #Twitter StreamListener

    def on_status(self, status):
        processTweet(status)
        return True

    def on_error(self, status_code):
        if status_code == 420:
            #returning False in on_error disconnects the stream
            return False

def processTweet(status): #Define on command functionality, reroutes to makeTweets if appropriate

    if "@DefineAllWords" in status.text and "#define" in status.text and "RT" not in status.text:
        try:
            print("Define request found: " + status.text)
            words = status.text.split()
            i = words.index("#define") + 1
            chars = "".join(re.split("[^a-zA-Z]*", words[i]))

            if killCheck(chars) or killCheck(status.text) or killCheck(status.user.name) or killCheck(status.user.screen_name):
                # api.create_block(status.user.screen_name)
                # api.report_spam(status.user.screen_name)
                print("USER " + status.user.screen_name + " IS BEING BLOCKED")
                addBlockList(status.user.screen_name)
                return
            
            if pCheck(chars) or pCheck(status.text) or pCheck(status.user.name):
                print("USER " + status.user.screen_name + " USED PROFRANITY. IGNORING AND ADDING TO PTRACKING...")
                addPTracking(status.user.screen_name)
                return

            media_id = getMediaID(chars)
            definition = defineWord(chars)
            definition_phrase = "Here's " + chars + " defined! " + '\n' + definition
            # definition_phrase = "@" + status.user.screen_name + ' ' + "Here's " + chars + " defined! " + '\n' + definition
            print(definition_phrase)
            definition_length = len(definition_phrase)

            if not killCheck(definition_phrase) and not pCheck(definition_phrase) and not onBlockList(status.user.screen_name):
                if definition_length <= 280:
                    if "We're" not in definition_phrase:
                        api.update_status(status = definition_phrase, in_reply_to_status_id = status.id_str, media_ids=media_id, auto_populate_reply_metadata=True)
                    else:
                        api.update_status(status = definition_phrase, in_reply_to_status_id = status.id_str, auto_populate_reply_metadata=True)

                else:
                    first_definition = definition_phrase[:280]
                    leftover = definition_phrase[280:]

                    new_tweets = len(leftover)//280 + 1
                    last_length = len(leftover) % 280
                    last_id = api.update_status(status = first_definition, in_reply_to_status_id = status.id_str, media_ids=media_id, auto_populate_reply_metadata=True).id_str

                    print("Beginning reply chain...")

                    for i in range(new_tweets):
                        if i == new_tweets - 1:
                            reply_tweet = leftover[:last_length]
                            api.update_status(status = reply_tweet, in_reply_to_status_id = last_id)
                            print(reply_tweet)
                        else:
                            reply_tweet = leftover[:280]
                            leftover = leftover[280:]
                            last_id = api.update_status(status = reply_tweet, in_reply_to_status_id = last_id).id_str
                            print(reply_tweet)
            else:
                print(status.user.screen_name + "'s REQUEST FAILED PROFANITY SCREEN.")
            deleteImage()

        except Exception as e:
            print("Define Request Exception Encountered:")
            print(e)
            exception_reply = "Whoops! We either don't know that word or your request wasn't formatted correctly... To request a definition, tag me and include #define <insert a real word here>."
            api.update_status(status = exception_reply, in_reply_to_status_id = status.id_str, auto_populate_reply_metadata=True)
            try:
                deleteImage()
            except:
                pass
        print("------------FINISHED-------------")

    elif status.user.id_str == "944864788336824321":
        print("New @fckeveryword tweet: " + status.text)
        makeTweets(getWord(status),status.id_str)

    else:
        pass

def getWord(status):
    return status.text.split()[1]

def main(): #initialize stream and handle the numerous potential exceptions
    print("Running...")
    while(True):
        api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
        myStreamListener = MyStreamListener(api)
        myStream = tweepy.Stream(auth = api.auth, listener=myStreamListener)
        try:
            myStream.filter(follow=["944864788336824321"], track=["@DefineAllWords"])
        except TimeoutError as t:
            print("t")
            print(t)
            print("Connection timeout exception encountered, 15 min sleep...")
            time.sleep(900)
            print("Started over, Running...")
        except ConnectionError as c:
            print("c")
            print(c)
            print("Connection timeout exception encountered, 15 min sleep...")
            time.sleep(900)
            print("Started over, Running...")
        except KeyboardInterrupt:
            print("Stream manually interrupted, exiting.... program must be ran again. WARNING: Don't rerun too many times too quickly. It's best to wait 15 minutes.")
            myStream.disconnect()
            break
        except TypeError as ty:
            print("ty")
            print(ty)
            print("Tweet/Definition exception encountered, powering through in 10 seconds...")
            time.sleep(10)
            print("Started over, Running...")
        except AttributeError as a:
            print("a")
            print(a)
            print("Tweet/Definition exception encountered, powering through in 10 seconds...")
            time.sleep(10)
            print("Started over, Running...")
        except ValueError as v:
            print("v")
            print(v)
            print("Tweet/Definition exception encountered, powering through in 10 seconds...")
            time.sleep(10)
            print("Started over, Running...")
        except Exception as e:
            print(e)
            print("Miscellaneous exception (potentially timeout) encountered, 15 min sleep...")
            time.sleep(900)
            print("Started over, Running...")

if __name__ == '__main__':
    main()