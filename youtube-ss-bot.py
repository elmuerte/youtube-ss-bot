#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Mastodon bot which posts arbitrary screenshot of a youtube movie with a link to it
# For this to work you must have the youtube file downloaded locally.

import pathlib, json, random, math
from tempfile import NamedTemporaryFile
from mastodon import Mastodon
from moviepy.editor import *
from imageio import imwrite

configFile = sys.argv[1]
if not pathlib.Path(configFile).exists():
	print("Config file not found:", configFile)
	sys.exit(1)

basepath = pathlib.Path(configFile).parent.resolve()
config = json.load(open(configFile))
if not "format" in config:
	config["format"] = "jpg"
if not "format-args" in config:
	config["format-args"] = {}

entry = random.choice(config["videos"])
video = VideoFileClip(str(basepath / entry["file"]))

offset = random.random() * video.duration

msg = "";
if "message" in entry:
	msg = entry["message"]
if "url" in entry:
	msg = msg + "\n" + entry["url"].format(math.floor(offset))

try:
	tmp = NamedTemporaryFile(delete=False, suffix="."+config["format"])
	tmp.close()
	frame = video.get_frame(offset).astype("uint8")
	imwrite(tmp.name, frame, format=config["format"], **config["format-args"])

	mastodon = Mastodon(
		access_token = basepath / config["token"],
		api_base_url = config["api"]
	)
	media = mastodon.media_post(tmp.name)
	mastodon.status_post(msg, media_ids=media)
finally:
	os.unlink(tmp.name)
	#print(tmp.name)
