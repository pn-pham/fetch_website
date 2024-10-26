from flask import Flask
from urllib.request import Request, urlopen

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def handle_request():
  req = Request(
      url='https://www.livesoccertv.com/',
      headers={'User-Agent': 'Mozilla/5.0'}
  )
  webpage = urlopen(req).read()
  # print(webpage)
  return webpage
