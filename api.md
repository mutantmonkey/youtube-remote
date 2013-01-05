# YouTube Leanback API

<https://www.youtube.com/api/lounge/pairing/get_lounge_token?screen_id=123>

## `_sc` verbs:
* addVideo - add video to queue
    * videoId
* setVideo - play video immediately
    * videoId
    * currentTime
* pause - pause video (will not unpause)
* play - play video (unpauses)
* seekTo - seek to position
    * newTime
