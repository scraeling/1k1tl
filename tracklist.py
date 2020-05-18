from bs4 import BeautifulSoup as bs
from datetime import timedelta
import re
import requests

HEADER = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:76.0) Gecko/20100101 Firefox/76.0'}

def search_sets(input: str):
    url = "https://www.1001tracklists.com/search/result.php"
    payload = {
        'main_search': input,
        'search_selection': 9,
    }
    response = requests.post(url, data = payload, headers = HEADER)
    results = bs(response.content, 'lxml')

    set_list = []
    sets = results.findAll('article', limit=10)
    for item in sets:
        set_list.append(parse_search_result(item))
    return set_list

def parse_search_result(set_item):
    title = set_item.find('a')
    return {
        'link': 'https://www.1001tracklists.com' + title.attrs['href'],
        'name': title.contents[0],
        'duration': set_item.find('div', attrs = {'title': 'play time'}).find('span').contents[0].strip().replace('h', 'h '),
        'playable': {
            'yt': True if set_item.findAll('i', 'fa-youtube-play') else False,
            'sc': True if set_item.findAll('i', 'fa-soundcloud') else False
        }
    }

def parse_tracklist(search_result: {}):
    response = requests.get(search_result['link'], headers = HEADER)
    tracklist_page = bs(response.content, 'lxml')

    tracklist = []
    items = tracklist_page.findAll('tr', 'tlpItem')
    for track in items:
        track_title = track.find('div', attrs = {'itemprop': 'tracks'})
        time = track.find('div', 'cueValueField').contents[0].strip()

        if '-' in time:
            time = None
        else:
            time = to_time_delta(time)

        tracklist.append({
            'name': track_title.find('meta', attrs = {'itemprop': 'name'})['content'],
            'time': time
        })

    search_result['tracklist'] = tracklist
    return search_result

def find_track_at(time: timedelta, search_result: {}):
    prev_track = {'time': timedelta(-1)}
    for track in search_result['tracklist']:
        if time >= prev_track['time'] and time < track['time']:
            return prev_track
        prev_track = track

def to_time_delta(time: []):
    time = [int(t) for t in time.split(':')]
    if len(time) == 3:
        time = timedelta(hours=time[0], minutes=time[1], seconds=time[2])
    elif len(time) == 2:
        time = timedelta(minutes=time[0], seconds=time[1])
    elif len(time) == 1:
        time = timedelta(seconds=time[0])
    return time

#sets = search_sets('armin')
#p = parse_tracklist(sets[0])
#find_track_at(timedelta(seconds=1001), p)