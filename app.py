from flask import Flask, request
from urllib.request import Request, urlopen

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def handle_request():
  url = request.args.get('url') if request.method == 'GET' else request.form.get('url')
  req = Request(
      url=url,
      headers={'User-Agent': 'Mozilla/5.0'}
  )
  webpage = urlopen(req).read()
  return webpage
