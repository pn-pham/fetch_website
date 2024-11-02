from flask import Flask, request
from urllib.request import Request, urlopen
import urllib.error
from datetime import datetime, timedelta
import json
import time

livesoccertv_url = "https://www.livesoccertv.com/"

leagues = [
    "england/premier-league", 
    "england/fa-cup",
    "england/championship",
    "england/football-league-cup",
    "france/ligue-1",
    "germany/bundesliga", 
    "germany/2-bundesliga",
    "germany/german-cup",
    "italy/serie-a",
    "italy/coppa-italia",
    "spain/primera-division",  
    "international/uefa-champions-league", 
    "international/uefa-europa-league", 
    "international/uefa-europa-conference-league",                   
    "international/uefa-european-championship"
]

def fetch_url(url):
    time.sleep(1)
    print("Fetching URL:", url)
    try:
        response = Request(
                            url=url,
                            headers={'User-Agent': 'Mozilla/5.0'}
                    )
        return urlopen(response).read().decode('utf-8')
    except urllib.error.URLError as e:
        print(f"Failed to fetch {url}: {e}")
        return ""

def convert_time(time_str, time_offset):
    if time_str[-1] == 'm':
        time_str = time_str[:-2] + ' ' + time_str[-2:]
    date_time = datetime.strptime("1/1/2000 " + time_str, "%d/%m/%Y %H:%M")
    adjusted_time = date_time + timedelta(hours=time_offset)
    return adjusted_time.strftime("%H:%M")

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def handle_request():
    today = request.args.get('today') if request.method == 'GET' else request.form.get('today')
    time_offset = request.args.get('time_offset') if request.method == 'GET' else request.form.get('time_offset')

    print("today", today, type(today))
    print(livesoccertv_url + 'schedules/' + today)
    content = fetch_url(livesoccertv_url + 'schedules/' + today)

    times = []
    links = []
    matches = []
    
    x1 = content.find('class="sortable_comp"')
    x_end = content.find('table>', x1)
    time_code = "H:MM" if content.find('H:MM', x1 + 1) > 0 else "h:MMtt"
    
    while x1 > -1:
        x2 = content.find("competitions", x1)
        x3 = content.find('"', x2 + 1)
        competition = content[x2 + 13:x3 - 1]
        x1 = content.find('class="sortable_comp"', x3)
        if (x1 < 0):
            x1 = x_end
        
        if competition in leagues:
            x4 = content.find(time_code, x3 + 1)
            while x4 > -1 and x4 < x1:
                x5 = content.find('>', x4 + 1)
                x6 = content.find('<', x5 + 1)
                match_time = content[x5 + 1:x6]
                times.append(convert_time(match_time, time_offset))
                
                x7 = content.find("/match/", x4 + 1)
                x8 = content.find('"', x7 + 1)
                match_link = content[x7:x8 - 1]
                links.append(match_link)
                
                x9 = content.find('"', x8 + 1)
                x10 = content.find('"', x9 + 1)
                match_name = content[x9 + 1:x10]
                matches.append(match_name)
                
                x4 = content.find(time_code, x10 + 1)
        x1 = content.find('class="sortable_comp"', x3)
    
    sorted_indexes = sorted(range(len(times)), key=lambda k: times[k])
    
    saved_times = [times[i] for i in sorted_indexes]
    saved_links = [links[i] for i in sorted_indexes]
    saved_matches = [matches[i] for i in sorted_indexes]
    
    for i in range(len(saved_times)):
        if saved_times[i][:2] == '18':
            saved_times[i] = 'I' + saved_times[i][1:]
    
    channel_list = []
    for link in saved_links:
        content = fetch_url(livesoccertv_url + link)
        channels = []
      
        x1 = content.find('International Coverage')
        x1 = content.find('/channels/', x1)
        x3 = content.find('Content disclaimer')
    
        while x1 > -1 and x1 < x3:
            x2 = content.find('"', x1 + 10)
            channel = content[x1 + 10:x2 - 1]
            if channel not in channels:
                channels.append(channel)
            x1 = content.find('/channels/', x2 + 1)
    
        channel_list.append(channels)
    
    return json.dumps([saved_times, saved_matches, channel_list])
