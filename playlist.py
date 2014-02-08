from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
import query
import pyechonest


app = Flask(__name__)
app.config.from_object(__name__)

app.config['PROPAGATE_EXCEPTIONS'] = True

@app.route('/')
def show_home():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_playlist():
    artist = request.args.get('artist')
    track = request.args.get('track')
    #try:
    tuples = query.do_everything(artist, track)
    #except EchoNestAPIError as e: # doesn't work fuck
    #    return render_template('ratelimit.html')
    bpm = request.args.get('bpm')
    diversity = request.args.get('diversity')
    tracks = request.args.get('tracks')
    playlist_id = 'test'
    #print tuples

    return render_template('playlist.html', playlist_id=playlist_id, tuples=tuples)

if __name__ == '__main__':
    app.run(debug=True)
