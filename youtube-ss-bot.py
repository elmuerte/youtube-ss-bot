#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2023 Michiel Hendriks
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Mastodon bot which posts arbitrary screenshot of a youtube movie with a link to it
# For this to work you must have the youtube file downloaded locally.

import pathlib, json, random, math, isodate
from datetime import datetime, timedelta
from tempfile import NamedTemporaryFile
from mastodon import Mastodon
from moviepy.editor import *
from imageio import imwrite

print(datetime.now())

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

def mode_random():
	entry = random.choice(config["videos"])
	video = VideoFileClip(str(basepath / entry["file"]))
	offset = random.random() * video.duration
	return (entry, video, offset)

def create_cycle_state():
	print("Initializing state")
	state = {}
	state["epoch"] = datetime.now().timestamp()
	state["position"] = 0
	state["total-duration"] = 0
	state["durations"] = {}
	return state;

def state_ensure_durations(state):
	if not "durations" in state:
		state["durations"] = {}
	total = 0.0
	for entry in config["videos"]:
		if not entry["file"] in state["durations"]:
			with VideoFileClip(str(basepath / entry["file"])) as video:
				state["durations"][entry["file"]] = video.duration
				total += video.duration
		else:
			total += state["durations"][entry["file"]]
	state["total-duration"] = total

def mode_cycle():
	stateFile = basepath / "state.json"
	isnew = False
	if pathlib.Path(stateFile).is_file():
		state = json.load(open(stateFile))
	else:
		state = create_cycle_state()
		isnew = True
	state_ensure_durations(state)
	if not isnew:
		if not "cycle" in config:
			config["cycle"] = "P1Y"
		cycle = isodate.parse_duration(config["cycle"])
		enddate = datetime.fromtimestamp(state["epoch"]) + cycle
		state["position"] = (datetime.now().timestamp() - state["epoch"]) / (enddate.timestamp() - state["epoch"])
	json.dump(state, open(stateFile, "w"))
	offset = state["position"] * state["total-duration"]
	entry = None
	for e in config["videos"]:
		dur = state["durations"][e["file"]]
		if dur < offset:
			offset -= dur
		else:
			entry = e
			break
	return (e, VideoFileClip(str(basepath / entry["file"])), offset)

if not "mode" in config or config["mode"] == "random":
	(entry, video, offset) = mode_random()
elif config["mode"] == "cycle":
	(entry, video, offset) = mode_cycle()

print("Posting frame from", entry["file"], offset)

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
	result = mastodon.status_post(msg, media_ids=media)
	print(result.url)
finally:
	os.unlink(tmp.name)
	#print(tmp.name)
