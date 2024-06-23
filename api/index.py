from sudachipy import tokenizer
from sudachipy import dictionary
from flask import Flask, request, jsonify
from flask_cors import CORS
from utils import katakana_to_hiragana_convert
from youtube_transcript_api import YouTubeTranscriptApi

# 创建分词器
tokenizer_obj = dictionary.Dictionary().create()
mode = tokenizer.Tokenizer.SplitMode.C


# 定义分词函数
def tokenize_to_json(text):
    """
    对给定文本进行分词,并将分词结果以 JSON 格式返回
    包含单词surface、发音read、词性pos等信息
    """
    nodes = tokenizer_obj.tokenize(text, mode)
    tokens = []
    for node in nodes:
        print(node.surface(), node.reading_form(), node.part_of_speech())
        token = {
            'surface': node.surface(),
            'kana': katakana_to_hiragana_convert(node.reading_form()),
        }
        tokens.append(token)
    return tokens


app = Flask(__name__)
CORS(app)


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'



@app.route('/translate_subtitles', methods=['GET'])
def tokenize():
    vid = request.args.get('video_id')
    if not vid:
        return jsonify({'error': 'Missing text parameter'}), 400
    print(vid)
    try:
        srt = YouTubeTranscriptApi.get_transcript(vid, languages=['ja'])
        print(srt)
        # 添加翻译后的字段
        for item in srt:
            item['token'] = tokenize_to_json(item['text'])
        return srt
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.debug = False
    app.run()
