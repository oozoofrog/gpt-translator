#!myenv/bin/python
import openai
import os

def parse_srt(srt):
    # SRT subtitle Format
    # 1 // index
    # 00:00:00,000 --> 00:00:02,000 {attributes}
    # Hello, World!
    # {empty line}

    # get index with regex
    import re
    # index pattern for only number whole string
    index_pattern = re.compile(r"(^\d+$)")
    # number array of index
    indexes = []
    # dictionary for subtitle
    subtitles = {}
    for subtitle in srt.split("\n\n"):
        lines = subtitle.split("\n")
        # remove '' in lines
        lines = list(filter(lambda x: x != '', lines))
        # if lines is empty, continue
        if len(lines) == 0:
            continue
        index = 0
        for line in lines:
            match = index_pattern.match(line)
            if match is None:
                continue
            index = int(match.group(1))
            indexes.append(index)
        # joine lines for subtitles
        subtitles[index] = "\n".join(lines)
    return indexes, subtitles

def base_prompt(subtitle_str, chunk_subtitles):
    messages = [
        {"role": "system", "content": f"You are Professional video subtitle translator. Translate the following English subtitles to Korean."},
        {"role": "assistant", "content": f"full SRT subtitle is \n{subtitle_str}"},
        {"role": "user", "content": 
            f"""
            Please translate next subtitles to Korean.
            Keep the SRT format intact, and provide only the translated subtitles with no additional text.
            Do not use markdown. just plain text for SRT subtitle format.
            {chunk_subtitles}
            """
        }
    ]
    return messages

def translate(subtitle_file_path, openapi_key):
    # open sample.srt.txt file
    with open(subtitle_file_path, "r") as file:
        subtitle_str = file.read()

    indexes, subtitles = parse_srt(subtitle_str)

    client = openai.OpenAI(api_key=openapi_key)

    translated_subtitles = []

    # windowed indexes by 12 from indexes
    for i in range(0, len(indexes), 12):
        partial_indexes = indexes[i:i+12]
        partial_subtitles = {index: subtitles[index] for index in partial_indexes}
        chunk_subtitles = '\n\n'.join(partial_subtitles.values())

        messages = base_prompt(subtitle_str, chunk_subtitles=chunk_subtitles)
        chat_completion = client.chat.completions.create(
            messages=messages,
            model="gpt-4o",
        )
        choices = chat_completion.choices
        choice = choices[0]
        content = choice.message.content
        translated_subtitles.append(content)
        print(f'translated subtitles: \n{content}')
    return '\n\n'.join(translated_subtitles)
    
#main
if __name__ == "__main__":
    import argparse

    # subtitle file path
    parser = argparse.ArgumentParser(description='Translate English subtitle to Korean')
    parser.add_argument('--input', type=str, help='subtitle file path')
    parser.add_argument('--openai_key', type=str, help='OpenAI API KEY')

    args = parser.parse_args()

    # tilde expansion
    subtitle_file_path = os.path.expanduser(args.input)

    result = translate(subtitle_file_path, args.openai_key)
    print(result)