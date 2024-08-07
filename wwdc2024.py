#!myenv/bin/python

import sys
import requests
import yt_dlp
import os

def merge_video_subtitle(video_file, subtitle_file, subtitle_ko_file, output_path):
    import subprocess
    # ffmpeg -i input.mp4 -i input.srt -c copy -c:s mov_text output.mp4

    if subtitle_ko_file:
        command = [
            'ffmpeg',
            '-v', 'info',
            '-i', video_file,
            '-i', subtitle_ko_file,
            '-i', subtitle_file,
            '-c:v', 'copy',
            '-c:a', 'copy',
            '-c:s', 'mov_text',  # Use mov_text codec for subtitles
            '-metadata:s:s:0', 'language=kor',
            '-metadata:s:s:1', 'language=eng',
            output_path,
            '-y'
        ]
    else:
        command = [
            'ffmpeg',
            '-v', 'info',
            '-i', video_file,
            '-i', subtitle_file,
            '-c:v', 'copy',
            '-c:a', 'copy',
            '-c:s', 'mov_text',  # Use mov_text codec for subtitles
            '-metadata:s:s:0', 'language=eng',
            output_path
        ]
    subprocess.run(command, check=True)
    print(f"Subtitled video saved to: {output_path}")

def translation_subtitle_to_ko(openai_key, subtitle_path):
    import translate

    translated_subtitle = translate.translate(subtitle_path, openai_key)

    # add _ko to subtitle filename
    translated_subtitle_path = subtitle_path.replace('.srt', '_ko.srt')

    with open(translated_subtitle_path, 'w', encoding='utf-8') as file:
        file.write(translated_subtitle)
    
    return translated_subtitle_path
   
# opts is nullable
def main(video_path, subtitle_path, output_path, openai_key):
    try:
        # expand tilde in path
        video_path = os.path.expanduser(video_path)
        subtitle_path = os.path.expanduser(subtitle_path)
        output_path = os.path.expanduser(output_path)
        subtitle_ko_path = translation_subtitle_to_ko(openai_key, subtitle_path)
        # print video_path, subtitle_path, subtitle_ko_path, output_path
        print(f"Video: {video_path}")
        print(f"Subtitle: {subtitle_path}")
        print(f"Subtitle(KO): {subtitle_ko_path}")
        print(f"Output: {output_path}")

        merge_video_subtitle(video_path, subtitle_path, subtitle_ko_path)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Arguments
    # --video or --subtitle for download only video or subtitle
    # --openai_key=YOUR_OPENAI_KEY for openai key
    import argparse
    parser = argparse.ArgumentParser(description='Download WWDC video and subtitle')
    parser.add_argument('--input_video', type=str, help='Input video filename')
    parser.add_argument('--output_video', type=str, help='Output filename')
    parser.add_argument('--input_subtitle', type=str, help='Input subtitle filename')
    parser.add_argument('--openai_key', type=str, help='OpenAI API key or export environment variable WWDC_TRANSLATE_OPENAI_KEY')
    args = parser.parse_args()
    openai_key = args.openai_key
    if not openai_key:
        # get openai key from environment variable
        openai_key = os.getenv('WWDC_TRANSLATE_OPENAI_KEY')
        print(f"OpenAI(environment: WWDC_TRANSLATE_OPENAI_KEY) key: {openai_key}")
    main(args.input_video, args.input_subtitle, args.output_video, openai_key)

