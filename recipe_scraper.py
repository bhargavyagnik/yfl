import os
import concurrent.futures
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from api_keys import DEVELOPER_KEY

ctr = 0
# Channel ID of the target channel
CHANNEL_ID = "UCe2JAC5FUfbxLCfAvBWmNJA"

MAX_WORKERS = 1

# Function to process video data and write to CSV
def process_video(video_data):
  video_id = video_data['id']['videoId']
  title = video_data['snippet']['title']
  url = f"https://www.youtube.com/watch?v={video_id}"
  description = video_data['snippet'].get('description', '')  # Handle missing descriptions

  # Write data to CSV row
  with open("channel_data.csv", "a", encoding="utf-8") as csvfile:
    csvfile.write(f"{title},{url},{description}\n")

# Function to get video list from a YouTube channel
def get_channel_videos(channel_id, page_token=None):
  global ctr
  youtube = build('youtube', 'v3', developerKey=DEVELOPER_KEY)

  # Request video list for the channel
  request = youtube.search().list(
      part="snippet",
      channelId=channel_id,
      maxResults=50,
      type="video",
      order="date",
      pageToken=page_token
  )
  response = request.execute()

  # Extract video data from the response
  videos = response.get("items", [])

  # Loop through videos and process them
  for video in videos:
    process_video(video)

  # Check for next page token and call recursively if available
  next_page_token = response.get("nextPageToken", None)
  if next_page_token:
    ctr+=50
    print(ctr)
    get_channel_videos(channel_id, next_page_token)

# Main function to orchestrate the process
def main():
  # Check if CSV file exists and create it if not
  if not os.path.exists("captions.csv"):
    with open("captions.csv", "w", encoding="utf-8") as csvfile:
      csvfile.write("title,url,caption_url\n")

  # Use concurrent.futures to parallelize video processing
  with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    get_channel_videos(CHANNEL_ID)

if __name__ == "__main__":
  main()
