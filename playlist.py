from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
import query


app = Flask(__name__)
app.config.from_object(__name__)

@app.route('/')
def show_home():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_playlist():
    artist = request.args.get('artist')
    bpm = request.args.get('bpm')
    diversity = request.args.get('diversity')
    tracks = request.args.get('tracks')

    return render_template('playlist.html', playlist_id=playlist_id)

if __name__ == '__main__':
    app.run()
