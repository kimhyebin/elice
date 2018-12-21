# -*- coding: utf-8 -*-
import json
import os
import re
import urllib.request

from bs4 import BeautifulSoup
from slackclient import SlackClient
from flask import Flask, request, make_response, render_template

app = Flask(__name__)

slack_token = "xoxp-506652758256-507485013618-507374980436-58849ee2e59fe08a9ea036bb8b905981"
slack_client_id = "506652758256.506940430913"
slack_client_secret = "714110f0bb0e67434431bd1501272f96"
slack_verification = "7w9uJemGJuqlLMlwdgx5hxgp"
sc = SlackClient(slack_token)

# 크롤링 함수 구현하기
def _crawl_naver_keywords(text):
    url = "https://search.naver.com/search.naver?where=nexearch&sm=tab_etc&query=%EB%B0%95%EC%8A%A4%EC%98%A4%ED%94%BC%EC%8A%A4%20%ED%8F%89%EC%A0%90%EC%88%9C%EC%9C%84"
    req= urllib.request.Request(url)
    sourcecode = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(sourcecode, "html.parser")

    title_list_tmp = []
    title_list = []
    star_list_tmp = []
    star_list = []

    for i in soup.find_all("strong", class_ = "scm_ellipsis_text _text"):
           title_list.append(i.get_text())

   #for i in range(10, 20) :
   #    title_list.append(title_list_tmp[i])

    for i in soup.find_all("dl", class_ = "movie_item"):
           star_list.append(i.get_text())


    movie_list = []
    for i in range(11) :
        movie_list.append(str(i+1) + "위 : " + str(title_list[i]) + " / " + str(star_list[i]))
    return u'\n'.join(movie_list)    

# 이벤트 핸들하는 함수
def _event_handler(event_type, slack_event):
    print(slack_event["event"])

    if event_type == "app_mention":
        channel = slack_event["event"]["channel"]
        text = slack_event["event"]["text"]

        keywords = _crawl_naver_keywords(text)
        sc.api_call(
            "chat.postMessage",
            channel=channel,
            text=keywords
        )

        return make_response("App mention message has been sent", 200,)

    # ============= Event Type Not Found! ============= #
    # If the event_type does not have a handler
    message = "You have not added an event handler for the %s" % event_type
    # Return a helpful error message
    return make_response(message, 200, {"X-Slack-No-Retry": 1})

@app.route("/listening", methods=["GET", "POST"])
def hears():
    slack_event = json.loads(request.data)

    if "challenge" in slack_event:
        return make_response(slack_event["challenge"], 200, {"content_type":
                                                             "application/json"
                                                            })

    if slack_verification != slack_event.get("token"):
        message = "Invalid Slack verification token: %s" % (slack_event["token"])
        make_response(message, 403, {"X-Slack-No-Retry": 1})
    
    if "event" in slack_event:
        event_type = slack_event["event"]["type"]
        return _event_handler(event_type, slack_event)

    # If our bot hears things that are not events we've subscribed to,
    # send a quirky but helpful error response
    return make_response("[NO EVENT IN SLACK REQUEST] These are not the droids\
                         you're looking for.", 404, {"X-Slack-No-Retry": 1})

@app.route("/", methods=["GET"])
def index():
    return "<h1>Server is ready.</h1>"

if __name__ == '__main__':
    app.run('0.0.0.0', port=8080)
