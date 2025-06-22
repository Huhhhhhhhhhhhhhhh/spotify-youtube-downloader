import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import yt_dlp
import sys

# --- Setup Stuff ---
# IMPORTANT: Grab your Spotify API credentials from:
# https://developer.spotify.com/dashboard/
SPOTIPY_CLIENT_ID = 'YOUR_SPOTIPY_CLIENT_ID' # Your Spotify Client ID goes here
SPOTIPY_CLIENT_SECRET = 'YOUR_SPOTIPY_CLIENT_SECRET' # And your secret key here



def get_spotify_track_info(track_url):
    """
    Pulls artist and song title from a Spotify track URL.
    Returns (artist, title) or (None, None) if something goes wrong.
    """
    if SPOTIPY_CLIENT_ID == 'YOUR_SPOTIPY_CLIENT_ID' or SPOTIPY_CLIENT_SECRET == 'YOUR_SPOTIPY_CLIENT_SECRET':
        print("\nERROR: Seriously, put your Spotify credentials in the script!")
        print("Go to Spotify Developer Dashboard to get them.")
        return None, None

    try:
        sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID,
                                                                   client_secret=SPOTIPY_CLIENT_SECRET))

        track = sp.track(track_url)
        artist_name = track['artists'][0]['name']
        track_title = track['name']
        print(f"\nFound it on Spotify:")
        print(f"  Artist: {artist_name}")
        print(f"  Title: {track_title}")
        return artist_name, track_title

    except spotipy.exceptions.SpotifyException as e:
        print(f"\nOops, Spotify connection issue: {e}")
        print("Double-check your Spotify credentials and the song link.")
    except Exception as e:
        print(f"\nSomething unexpected happened with Spotify: {e}")
    return None, None

def download_youtube_audio(search_query, output_dir='downloads'):
    """
    Searches YouTube and snags the audio.
    Saves to 'downloads' folder.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Made a new folder for downloads: {output_dir}")


    ydl_opts = {
        'format': 'bestaudio/best', #best audio quality
        'postprocessors': [{
            'key': 'FFmpegExtractAudio', # Use FFmpeg to get just the audio
            'preferredcodec': 'mp3', 
            'preferredquality': '192',   # Decent quality
        }],
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'), # Location of file
        'noplaylist': True, 
        'default_search': 'ytsearch', # Search YouTube by default
        'verbose': False, # Keep yt-dlp quiet
        'quiet': True, # Really quiet
        'print_json': True, 
        'logtostderr': False, # Don't log to standard error
    }

    print(f"\nLooking up '{search_query}' on YouTube to download audio...")

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # This searches and downloads the first hit
            info = ydl.extract_info(search_query, download=True)
            # To check what was downloaded
            if info and 'entries' in info and len(info['entries']) > 0:
                downloaded_file = ydl.prepare_filename(info['entries'][0])
                downloaded_file = os.path.splitext(downloaded_file)[0] + '.mp3' # Fix extension
                print(f"\nFinished downloading: {downloaded_file}")
            elif info and 'filepath' in info: # For single video downloads
                 downloaded_file = info['filepath']
                 downloaded_file = os.path.splitext(downloaded_file)[0] + '.mp3' # Fix extension
                 print(f"\nFinished downloading: {downloaded_file}")
            else:
                print("Couldn't find good audio or download failed.")

    except yt_dlp.utils.DownloadError as e:
        print(f"\nUh oh, YouTube download error: {e}")
        print("Might be region locked, video removed, or some other glitch.")
    except Exception as e:
        print(f"\nUnexpected error during YouTube download: {e}")



def main():
    """
    The main logic. Handles arguments and kicks off the download.
    """
    print("--- Spotify to YouTube Audio Downloader ---")
    print("How to use: python your_script_name.py <spotify_track_url>")

    if len(sys.argv) < 2:
        print("\nNeed a Spotify track URL, mate!")
        sys.exit(1) # Exit with an error

    spotify_url = sys.argv[1]

    if not spotify_url.startswith("https://open.spotify.com/track/"):
        print("\nThat doesn't look like a valid Spotify track URL. Make sure it's a direct song link.")
        sys.exit(1)

    artist, title = get_spotify_track_info(spotify_url)

    if artist and title:
        # Build the search query for YouTube
        youtube_search_query = f"{title} {artist} official audio"
        download_youtube_audio(youtube_search_query)
    else:
        print("\nCouldn't get Spotify info. Can't download without it. Exiting.")
        sys.exit(1)

if __name__ == "__main__":
    main()
