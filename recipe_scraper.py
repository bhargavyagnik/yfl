import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from api_keys import DEVELOPER_KEY
import csv

CHANNEL_ID = "UCe2JAC5FUfbxLCfAvBWmNJA"

# Replace with your own API key
API_KEY = DEVELOPER_KEY


def get_channel_videos(api_key, channel_id):
    youtube = build('youtube', 'v3', developerKey=api_key)
    
    try:
        # Get uploads playlist ID
        channel_response = youtube.channels().list(
            part='contentDetails',
            id=channel_id
        ).execute()
        
        uploads_playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        
        videos = []
        next_page_token = None
        
        while True:
            playlist_response = youtube.playlistItems().list(
                part='snippet',
                playlistId=uploads_playlist_id,
                maxResults=50,
                pageToken=next_page_token
            ).execute()
            
            for item in playlist_response['items']:
                video = {
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'],
                    'url': f"https://www.youtube.com/watch?v={item['snippet']['resourceId']['videoId']}"
                }
                videos.append(video)
            
            next_page_token = playlist_response.get('nextPageToken')
            if not next_page_token:
                break
        
        return videos
    
    except HttpError as e:
        print(f'An HTTP error {e.resp.status} occurred:\n{e.content}')
        return None

def save_to_csv(videos, filename='channel_data.csv'):
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['title', 'description', 'url'])
        writer.writeheader()
        for video in videos:
            writer.writerow(video)
    print(f"Data has been saved to {filename}")

def main():
    videos = get_channel_videos(API_KEY, CHANNEL_ID)
    
    if videos:
        save_to_csv(videos)
        print(f"Saved data for {len(videos)} videos to channel_data.csv")
    else:
        print("No videos were fetched. Check your API key and channel ID.")

if __name__ == '__main__':
    main()