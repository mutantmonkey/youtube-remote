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

    def __init__(self, remote_id, remote_app, remote_name, token):
        self.token = token

        r = requests.get('http://www.youtube.com/api/lounge/bc/test?VER=8&TYPE=xmlhttp')

        data = self._send('http://www.youtube.com/api/lounge/bc/bind?RID=1&VER=8&CVER=1&id={remote_id}&device=REMOTE_CONTROL&app={remote_app}&name={remote_name}'.\
                format(remote_id=remote_id, remote_app=remote_app,
                    remote_name=urllib.parse.quote(remote_name)))
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


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
            description="Command-line YouTube Leanback remote")
    parser.add_argument('--play', help="Play a video immediately")
    parser.add_argument('--queue', nargs='*',
            help="Add a video to the queue")
    parser.add_argument('--pause', action="store_true",
            help="Pause the current video")
    parser.add_argument('--unpause', action="store_true",
            help="Unpause the current video")
    args = parser.parse_args()

    remote = YouTubeRemote(config.REMOTE_ID, config.REMOTE_APP,
            config.REMOTE_NAME, config.TOKEN)

    if args.play:
        remote.set(args.play)
    if args.queue:
        for video in args.queue:
            remote.queue(video)
    if args.pause:
        remote.pause()
    if args.unpause:
        remote.play()
