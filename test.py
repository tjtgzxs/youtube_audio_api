

import datetime
import json
import multiprocessing
import os.path
import time
from functools import reduce
from typing import List

import wget

from youtube_audio_api import API, TrackType
from youtube_audio_api import TrackOrder, OrderField, OrderDirection

CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_PATH = CURRENT_PATH + "/download/"

import secret

api = API(secret.channel_id, secret.authorization, secret.cookie)

def download_tracks(track_ids: List[str]):
    for track_id in track_ids:

        tmp_fname = DOWNLOAD_PATH + track_id + "." + str(
            reduce(lambda x, y: x + y, [c for c in "l" + track_id if c.islower()]))
        fname = tmp_fname + ".mp3"
        if os.path.exists(fname):
            print("downloaded " + fname)
            continue

        while True:
            try:
                resp = api.get_tracks([track_id])
                tracks = resp.get("tracks")
                if tracks is not None and len(tracks) > 0:
                    for track in tracks:
                        track_id = track.get("trackId")

                        tmp_fname = DOWNLOAD_PATH + track_id + "." + str(
                            reduce(lambda x, y: x + y, [c for c in "l" + track_id if c.islower()]))
                        fname = tmp_fname + ".mp3"
                        if os.path.exists(fname):
                            print("downloaded " + fname)
                            continue

                        track_url = track.get("streamingAudioUrl")
                        print("downloading " + tmp_fname)
                        wget.download(track_url, out=tmp_fname)
                        os.rename(tmp_fname, fname)
                        print("downloaded " + fname)
                break
            except Exception as e:
                print(e)

def track_list_gen():
    page_token = None
    while True:
        resp = api.list_tracks(track_type_in=[TrackType.MUSIC, TrackType.SOUNDEFFECT],
                               track_order=TrackOrder(orderField=OrderField.TRACK_TITLE,
                                                      orderDirection=OrderDirection.ASC),
                               page_token=page_token, page_size=50)

        page_token = resp.get("pageInfo", {}).get("nextPageToken")
        total_size = int(resp.get("pageInfo", {}).get("totalSizeInfo", {}).get("size", 0))
        print("total_size=", total_size, "  page_token=", page_token)

        tracks = resp.get("tracks")
        if tracks is not None and len(tracks) > 0:
            yield tracks
        if page_token is None or page_token == "" or total_size <= 0:
            break

def main():
    print(api)
if __name__ == '__main__':
    # print(CURRENT_PATH)
    list=track_list_gen()
    for tracks in list:
        track_ids = [t["trackId"] for t in tracks]
        download_tracks(track_ids)
        break

