from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
import query
import pyechonest
import pylast


app = Flask(__name__)
app.config.from_object(__name__)

#app.config['PROPAGATE_EXCEPTIONS'] = True

@app.route('/')
def show_home():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_playlist():
    artist = request.form['artist']
    track = request.form['track']
    diversity = request.form['diversity']
    tracks = int(request.form['tracks'])
    try:
        tuples = query.do_everything(artist, track, int(tracks), int(diversity))
    except pyechonest.util.EchoNestAPIError:
        return render_template('index.html', error="Slow down! Maximum number of EchoNest API Requests exceeded.")
    except pylast.WSError:
        return render_template('index.html', error="Your artist was not found.")
    except IndexError:
        return render_template('index.html', error="Your track was not found.")
    #print artist
    #print track
    #print bpm
    #print diversity
    #print tracks
    playlist_id = 'test'
    #print tuples
    return render_template('playlist.html', playlist_id=playlist_id, tuples=tuples)

if __name__ == '__main__':
    app.run(debug=True)
    #app.run()
