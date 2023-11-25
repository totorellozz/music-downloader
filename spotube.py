import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from googleapiclient.discovery import build
from pytube import YouTube
from moviepy.editor import *
import os
import certifi
import re
import sys
import http.client
from termcolor import colored
import time
from pick import pick
from datetime import datetime
from config1 import spotify_client_id, spotify_client_secret, options, path

os.environ['SSL_CERT_FILE'] = certifi.where()

spotify_link = input(colored("Spotify playlist link: ", "blue"))
failed = []

title = 'Choose which API to use: '
selected, index = pick(options, title, indicator='==>', default_index=0)

if selected == 'exit':
    exit()

youtube_api_key = selected


def main():
    playlist = sp.playlist(playlist_id)
    playlist_name = playlist['name']
    try:
        current_time_folder = datetime.now().strftime(f"Download Of {playlist_name} %d:%m:%Y at %H.%M.%S")
        save_path = os.path.join(path, current_time_folder)
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        tracks = get_spotify_playlist_tracks(spotify_playlist_id)
        failed = []
        total_time_for_tracks = 0
        num = 0
        start_time = time.time()
        track_a = len(tracks)

        for track in tracks:
            num = num + 1
            print(colored(f"Song number: {num}", "yellow"))
            track_start_time = time.time()
            youtube_url = search_youtube(track)
            if youtube_url:
                print(colored(f"Attempting to download and convert {track}", "blue"))

                track_info = track.split(" ")
                song_name = " ".join(track_info[:-1])
                author = track_info[-1]

                mp3_file = download_video_as_mp3(youtube_url, save_path, song_name, author)
                if mp3_file:
                    print(colored(f"Saved MP3 file: {mp3_file}", "green"))
                    print(colored('\n-------------------------------------------------------------------------------------------------------------------------',"cyan"))
                else:
                    print(colored(f"Failed to download {track}, moving to next.", "red"))
                    failed.append(track)
                    print(colored('\n-------------------------------------------------------------------------------------------------------------------------',"cyan"))

            track_end_time = time.time()
            track_time = track_end_time - track_start_time
            total_time_for_tracks += track_time
            print(colored(f"Time for {track}: {track_time:.2f} seconds", "cyan"))


        if tracks:
            average_time_per_track = total_time_for_tracks / track_a
            print(colored(f"Average time per track: {average_time_per_track:.2f} seconds", "cyan"))

        if failed:
            print(colored("Failed to download the following tracks:", "yellow"))
            for fail in failed:
                print(colored(fail, "yellow"))

    except KeyboardInterrupt:
        print(colored("\nOperation cancelled by user", "red"))
        sys.exit()

    end_time = time.time()
    total_elapsed_time = end_time - start_time
    print(colored(f"Total time: {total_elapsed_time:.2f} seconds and there were {track_a} tracks", "cyan"))


def get_spotify_playlist_id(spotify_link):
    pattern = r'(spotify:playlist:|https://open\.spotify\.com/playlist/)([a-zA-Z0-9]+)'

    match = re.search(pattern, spotify_link)

    if match:
        return match.group(2)
    else:
        return colored("Invalid Spotify link", "red")


def download_video_as_mp3(url, save_path, song_name, author):
    try:
        yt = YouTube(url)
        video = yt.streams.filter(only_audio=True).first()

        base_filename = f"{song_name} - {author}".replace("/", "_")
        mp4_filename = base_filename + ".mp4"
        mp3_filename = base_filename + ".mp3"

        out_file = video.download(output_path=save_path, filename=mp4_filename)

        mp4_path = os.path.join(save_path, mp4_filename)
        mp3_path = os.path.join(save_path, mp3_filename)

        new_file = AudioFileClip(mp4_path)
        new_file.write_audiofile(mp3_path)

        os.remove(mp4_path)
        return mp3_path

    except http.client.IncompleteRead as e:
        print(colored(f"Error downloading song from {url}: {e}", "red"))
        return None


playlist_id = get_spotify_playlist_id(spotify_link)
spotify_playlist_id = playlist_id

client_credentials_manager = SpotifyClientCredentials(client_id=spotify_client_id, client_secret=spotify_client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
youtube = build('youtube', 'v3', developerKey=youtube_api_key)


def get_spotify_playlist_tracks(playlist_id):
    results = sp.playlist_tracks(playlist_id)
    tracks = []
    for item in results['items']:
        track = item['track']
        tracks.append(f"{track['name']} {track['artists'][0]['name']}")
    return tracks


def search_youtube(query):
    try:
        request = youtube.search().list(part="snippet", maxResults=1, q=query)
        response = request.execute()
        if response['items']:
            return f"https://www.youtube.com/watch?v={response['items'][0]['id']['videoId']}"
        return None
    except Exception as e:
        print(colored(f"An error occurred: {e}", "red"))
        return None


main()
