from flask import Blueprint, jsonify, request
from fer import FER, Video
import pandas as pd
import requests
import os
VideoModel_bp = Blueprint("VideoModelBluePrint", __name__)

@VideoModel_bp.route('/VideoModel', methods=['POST'])
def VideoModelAnalysis():
    # Assuming the video file URL is sent as a POST request
    data = request.json 
    # Extract the video link from the JSON data
    video_link = data.get('Video')

    if not video_link:
        return jsonify({"error": "Video link not provided"}), 400

    # Define the local filename to save the video
    local_filename = "downloaded_video.mp4"

    # Download the video and save it locally
    response = requests.get(video_link, stream=True)
    if response.status_code == 200:
        with open(local_filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192): 
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
    else:
        return jsonify({"error": "Unable to download video"}), 500

    # Check if the video is downloaded
    assert os.path.exists(local_filename), "Video file not found locally"

    # Now you can use the downloaded video
    video = Video(local_filename)
    emotion_detector = FER(mtcnn=True)

    # Analyze the video and store the results
    result = video.analyze(emotion_detector, display=False)

    emotions_df = video.to_pandas(result)

    # Predict whether a candidate shows interest in a topic or not
    positive_emotions = sum(emotions_df.happy) + sum(emotions_df.surprise) + sum(emotions_df.neutral)
    negative_emotions = sum(emotions_df.angry) + sum(emotions_df.disgust) + sum(emotions_df.fear) + sum(emotions_df.sad)

    # Calculate confidence score
    confidence_score = (positive_emotions / (positive_emotions + negative_emotions)) * 100

    # Determine the dominant emotion
    emotion_totals = {
        'angry': emotions_df['angry'].sum(),
        'disgust': emotions_df['disgust'].sum(),
        'fear': emotions_df['fear'].sum(),
        'happy': emotions_df['happy'].sum(),
        'sad': emotions_df['sad'].sum(),
        'surprise': emotions_df['surprise'].sum(),
        'neutral': emotions_df['neutral'].sum()
    }
    dominant_emotion = max(emotion_totals, key=emotion_totals.get)

    # Determine candidate's interest level
    if positive_emotions > negative_emotions:
        interest_level = "High"
    elif positive_emotions < negative_emotions:
        interest_level = "Low"
    else:
        interest_level = "Neutral"

    # Prepare response data
    response_data = {
        "video_link": video_link,
        "confidence_score": confidence_score,
        "dominant_emotion": dominant_emotion,
        "interest_level": interest_level
    }

    # Return the response as JSON
    return jsonify(response_data), 200
