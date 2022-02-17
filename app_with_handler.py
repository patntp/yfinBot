import os
import sys
from argparse import ArgumentParser

from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

import yfinance as yf
import pandas as pd

app = Flask(__name__)

line_bot_api = LineBotApi('JjWG+YhzofS2nxYVMBeX8zoccqDvhnLT2wa2XwxNK7R1iuuOFR8f7ro4M+y68NTmYBOPYW1ckksYapi4b/OSERdmj4C3Ej6zBPbB+Ap8Mwm0DlbuiRb5DXy9KpFP42ngIWWIFtcHkBTISwF21fPkoQdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('1b07eddfdfe07c5cc5be695166bb6706')


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def message_text(event):
    #use the user's text as tickers to retrieve price data
    data=yf.download(tickers=event.messages.text,period='1d',interval='1d')
    tic = data.iloc[-1]['Adj Close'].index[0]
    price=data.iloc[-1]['Adj Close'][0]
    print(tic+' price is found.')    

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=tic+' price : '+str(price))
    )


if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-p', '--port', default=8000, help='port')
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()

    app.run(debug=options.debug, port=options.port)
