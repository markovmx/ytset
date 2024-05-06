from moviepy.editor import AudioFileClip, ImageClip, CompositeVideoClip
from pydub import AudioSegment
from PIL import Image
from datetime import timedelta
import os


def concatenate_tracks(folder_path):
    mp3_files = [f for f in os.listdir(folder_path) if f.endswith('.mp3')]
    mp3_files.sort()

    result = AudioSegment.empty()
    tracklist = []

    start_time = 0
    for file in mp3_files:
        track = AudioSegment.from_mp3(os.path.join(folder_path, file))
        result += track
        track_duration = track.duration_seconds

        parts = file.split(" - ", 1)

        track_artist = parts[0].split(".")[1].strip()
        track_title = parts[1].rstrip('.mp3')

        track_title = file.split(" - ", 1)[1].rstrip('.mp3')
        tracklist.append((timedelta(seconds=start_time), f'{
                         track_artist} - {track_title}'))
        start_time += track_duration

    return result, tracklist


def find_cover_image(assets_dir):
    # Look for image files (cover.png or cover.jpg) in the assets directory
    for file in os.listdir(assets_dir):
        if file.lower() in ['cover.png', 'cover.jpg', 'cover.jpeg'] and file.lower().endswith(('png', 'jpg', 'jpeg')):
            return os.path.join(assets_dir, file)
    return None


def resize_image(image_path, output_path):
    # Open the image
    image = Image.open(image_path)

    # Resize the image to YouTube resolution (1920x1080)
    image = image.resize((1920, 1080))

    # Save the resized image
    image.save(output_path)


def create_tracklist(tracklist, output_dir):
    tracklist_file_path = os.path.join(output_dir, 'tracklist.txt')
    with open(tracklist_file_path, 'w') as f:
        for start_time, title in tracklist:
            formatted_time = str(start_time).split(
                '.', 1)[0]  # Format time (remove milliseconds)
            f.write(f"{formatted_time} {title}\n")
    print("Tracklist created and saved to:", tracklist_file_path)


def main():
    # Check if output directory exists, if not, create it
    output_dir = 'output'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Check if assets directory exists
    assets_dir = 'assets'
    if not os.path.exists(assets_dir):
        print("Error: 'assets' directory not found.")
        return

    # Concatenate audio tracks and export as out.mp3
    audio_folder_path = os.path.join(assets_dir, 'audio')
    if not os.path.exists(audio_folder_path):
        print("Error: 'audio' folder not found in the 'assets' directory.")
        return
    output_audio_path = os.path.join(output_dir, 'audio.mp3')
    output_audio, tracklist = concatenate_tracks(audio_folder_path)
    output_audio.export(output_audio_path, format='mp3')

    # Find cover image
    cover_image_path = find_cover_image(assets_dir)
    if cover_image_path:
        # Resize the cover image and save it to the output directory
        output_image_path = os.path.join(output_dir, 'cover.jpg')
        resize_image(cover_image_path, output_image_path)
        print("Image resized and saved to:", output_image_path)
    else:
        print("Error: No cover image found in the 'assets' directory.")
        return

    # Create tracklist file
    create_tracklist(tracklist, output_dir)

    # Check if output image exists
    if os.path.exists(output_image_path):
        # Load the image
        image_clip = ImageClip(output_image_path)

        # Load the audio
        audio_clip = AudioFileClip(output_audio_path)

        # Set the duration of the video to match the audio duration
        video_duration = audio_clip.duration

        # Set the duration of the image clip to match the audio duration
        image_clip = image_clip.set_duration(video_duration)

        # Combine the image and audio to create the video
        final_clip = CompositeVideoClip([image_clip.set_audio(audio_clip)])

        # Write the video to a file
        output_video_path = os.path.join(output_dir, 'video.mp4')
        final_clip.write_videofile(output_video_path, codec="libx264", fps=24)
        print("Video created and saved to:", output_video_path)
    else:
        print("Error: Output image not found.")


if __name__ == "__main__":
    main()
