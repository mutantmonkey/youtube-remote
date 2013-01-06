#!/usr/bin/python3

import config
import json
import requests
import urllib.parse


class YouTubeRemote(object):
    token = ""
    rid = 2
    sid = ""
    gsessionid = ""
    seq = 0

    def __init__(self, remote_id, remote_app, remote_name):
        self.remote_id = remote_id
        self.remote_app = remote_app
        self.remote_name = remote_name

    def pair(self, pairing_code):
        pairing_code.replace(" ", "")

        r = requests.post("https://www.youtube.com/api/lounge/pairing/get_screen",
                data={'pairing_code': pairing_code}, headers={
                    'User-Agent': "Apache-HttpClient/UNAVAILABLE (java 1.4)",
                })
        data = json.loads(r.text)
        self.load_token(data)
        return data

    def load_token(self, data):
        self.token = data['screen']['loungeToken']

    def connect(self):
        r = requests.get('http://www.youtube.com/api/lounge/bc/test?VER=8&TYPE=xmlhttp')

        data = self._send('http://www.youtube.com/api/lounge/bc/bind?RID=1&VER=8&CVER=1&id={remote_id}&device=REMOTE_CONTROL&app={remote_app}&name={remote_name}'.\
                format(remote_id=self.remote_id, remote_app=self.remote_app,
                    remote_name=urllib.parse.quote(self.remote_name)))
        self.sid = data[0][1][1]
        self.gsessionid = data[1][1][1]

    def _send(self, url, data=None):
        r = requests.post(url, data=data, headers={
            'X-YouTube-LoungeId-Token': self.token,
            'User-Agent': "YouTubeRemote",
            })
        data = "\n".join(r.text.splitlines()[1:])
        data = json.loads(data)
        return data

    def do(self, data):
        apidata = {
            'count': 1,
        }

        for k, v in data.items():
            apidata['req{0}_{1}'.format(self.seq, k)] = v

        #self.rid += 1
        result = self._send("http://www.youtube.com/api/lounge/bc/bind?RID={rid}&SID={sid}&VER=8&CVER=1&gsessionid={gsessionid}".\
                format(sid=self.sid, gsessionid=self.gsessionid, rid=self.rid),
                data=apidata)
        self.seq += 1

        return result

    def queue(self, video_id):
        self.do({
            '_sc': 'addVideo',
            'videoId': video_id,
        })

    def set(self, video_id):
        self.queue(video_id)
        self.do({
            '_sc': 'setVideo',
            'currentTime': 0,
            'videoId': video_id,
        })

    def play(self):
        self.do({'_sc': 'play'})

    def pause(self):
        self.do({'_sc': 'pause'})


def get_videoid(url):
    parsed = urllib.parse.urlparse(url)
    if parsed.netloc == 'youtu.be':
        return path.lstrip('/')
    elif parsed.netloc.endswith('youtube.com'):
        qs = urllib.parse.parse_qs(parsed.query)
        if 'v' in qs:
            return qs['v'][0]
        else:
            parts = parsed.path.split('/')
            return parts[-1]
    else:
        return url


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
            description="Command-line YouTube Leanback remote")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--play', help="Play a video immediately")
    group.add_argument('--queue', nargs='*',
            help="Add a video to the queue")
    group.add_argument('--pause', action="store_true",
            help="Pause the current video")
    group.add_argument('--unpause', action="store_true",
            help="Unpause the current video")
    args = parser.parse_args()

    remote = YouTubeRemote(config.REMOTE_ID, config.REMOTE_APP,
            config.REMOTE_NAME)

    try:
        data = json.load(open('screen.json'))
        remote.load_token(data)
    except IOError:
        data = remote.pair(input("Pairing code: "))
        with open('screen.json', 'w') as f:
            f.write(json.dumps(data))

    remote.connect()

    if args.play:
        remote.set(get_videoid(args.play))
    if args.queue:
        for video in args.queue:
            remote.queue(get_videoid(video))
    if args.pause:
        remote.pause()
    if args.unpause:
        remote.play()
