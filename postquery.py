import requests
import json
import html
import sys
import websockets
import asyncio
import config
from bs4 import BeautifulSoup as BS


def get_fkey_and_cookie(email, password):
    url = "https://stackoverflow.com/users/login"
    login_data = {"email": email, "password": password}
    session = requests.Session()
    x = session.post(url,login_data)
    #TODO: perform some cursory checking to confirm that logging in actually worked

    x = session.get("http://chat.stackoverflow.com")

    soup = BS(x.content, "html.parser")
    fkey = soup.find(id="fkey")["value"]

    #I wonder if this is the right way to do this?
    cookie = "; ".join("{}={}".format(name,value) for name, value in session.cookies.iteritems())

    return fkey, cookie

fkey, cookie = get_fkey_and_cookie(config.email, config.password)

def get_ws_url(roomid):
    s="roomid={}&fkey={}".format(roomid, fkey)
    header={
        "Content-Length": str(len(fkey)),
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": cookie
    }

    x = requests.post(
        "http://chat.stackoverflow.com/ws-auth", 
        headers=header,
        data=s
    )
    if x.status_code != 200:
        raise Exception("Got status code {} {}".format(x.status_code, x.reason))

    url = json.loads(x.text)["url"] + "?l=99999999"
    return url

def query_messages_test(roomid):
    x = requests.post(
        "http://chat.stackoverflow.com/chats/{}/events".format(roomid),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data = "since=0&mode=Messages&msgCount=10&fkey=" + fkey
    )

    if x.status_code != 200:
        raise Exception("Got status code {} {}".format(x.status_code, x.reason))

    data = json.loads(x.content.decode("utf-8"))
    for event in data["events"]:
        print("{}: {}".format(event["user_name"], event["content"]))

def post_message_test(roomid, text):
    s = "text={}&fkey={}".format(html.escape(text), fkey)

    x = requests.post(
        "https://chat.stackoverflow.com/chats/{}/messages/new".format(roomid),
        headers={
            "Content-Length": str(len(s)),
            "Content-Type": "application/x-www-form-urlencoded",
            "Cookie": cookie,
        },
        data=s
    )

    print(x.status_code, x.reason)

def post_join_test(roomid):
    s = "fkey={}".format(fkey)
    x = requests.post("https://chat.stackoverflow.com/chats/{}/join".format(roomid),
            headers={
            "Content-Length": str(len(s)),
            "Content-Type": "application/x-www-form-urlencoded",
            "Cookie": cookie,
        },
        data=s
    )
    print (x.status_code, x.reason)
