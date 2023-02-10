# YouTube Screenshot Mastodon Bot

This script is a Mastodon bot which posts random screenshots of video. It is not directly related to YouTube or videos hosted there. The bot expects the videos to be on the system the script runs on, and it can include a link to the hosted video with a timestamp added to the URL from where the screenshot was taken.

The script requires a configuration file, and is expected to be executed as a scheduled task (e.g. a cron job): `youtube-ss-bot.py <config.json>`

The Mastodon accounts https://botsin.space/@twinsen and https://botsin.space/@anachronox get their screenshot posts from this script.

Note that videos are not downloaded, you must have them on your local system for this script. You probably want to use something like `yt-dlp` you get the best video stream, in case you do not have a local copy.

## Configuration

```json
{
   "token":"token.secret",
   "api":"https://botsin.space/",
   "format":"jpg",
   "format-args":{
      "quality": 80
   },
   "videos":[
      {
         "file":"anachronox-part1-SvRomr2hnZg.webm",
         "url":"https://youtu.be/SvRomr2hnZg?t={0}",
      },
      {
         "file":"anachronox-part2-4Va1Wjmcabk.webm",
         "url":"https://youtu.be/4Va1Wjmcabk?t={0}"
      },
      {
         "file":"anachronox-part3-y3jBKsaC8Wg.webm",
         "url":"https://youtu.be/y3jBKsaC8Wg?t={0}"
      }
   ]
}
```

`token` is the filename which contains the Mastodon application access token.

`api` is the URI to the Mastodon server to contact.

`format` defines the output format of the screenshot (defaults to `jpg`). The `format-args` object defines additional, format specific, arguments to pass to [imageio](https://imageio.readthedocs.io/en/stable/_autosummary/imageio.v2.imwrite.html). For example. for JPEG the default quality is 75, depending on the video you might want to increase it as is done in the above example.

`videos` is an array of video items. Each entry contains at least a `file` reference.

`file` the filename, in the same directory as the config file, from where to pick a rand frame from.

When `url` is define a link is added to the post. The `{0}` is replaced with the second timestamp in the video from where the screenshot was taken.

Additionally you can specify a `message` value, which is an additional message added (above the link).

### Modes

By default the mode is `random` which means it picks a random file and makes a screenshot from a random point in time.

#### Cycle

If you set the mode to `cycle` the videos will be visited sequentially over a given cycle time (by default 1 year). It is basically a progress for a given time.

```json
{
	...
	"mode": "cycle",
	"cycle": "P1Y",
	...
}
```

The `cycle` value should be an ISO8601 Duration.

At first run it will create a `state.json` file containing the durations of the used files, total duration, current progress, but most importantly: the epoch.

```json
{
   "epoch":1672531200,
   "position":0.09234982496242213,
   "durations":{
      "somefile.mkv":5165.91
   },
   "total-duration":5165.91
}
```

The epoch defines when the cycle started. The epoch is a UNIX timestamp. You can create the `state.json` file before the first run and set the desired epoch.

## Installation

The following python libraries are used and should be installed:
- [Mastodon.py](https://github.com/halcy/Mastodon.py)
- [moviepy](https://zulko.github.io/moviepy/)
- [imageio](https://imageio.readthedocs.io)

## Supported video formats

The Python library [Moviepy](https://zulko.github.io/moviepy/) is used to extract frames from the videos.

## Supported screenshot formats

The Python ImageIO library is used to create the screenshot file. So all formats it supports (and for which support is installed) can be used. In most cases JPEG is probably your best option.
