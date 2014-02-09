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
        track_ids = query.do_everything(artist, track, int(tracks), int(diversity))
    except pyechonest.util.EchoNestAPIError:
        return render_template('index.html', error="Slow down! Maximum number of EchoNest API Requests exceeded.")
    except pylast.WSError:
        return render_template('index.html', error="Your artist was not found.")
    except IndexError:
        return render_template('index.html', error="Your track was not found.")
    except ValueError:
        return render_template('index.html', error="Your track was not found.")
    except:
        return render_template('index.html', error="An unknown error has occurred. Try again later.")

    #print(pairs)
    #track_ids = create.create_playlist(pairs)
    track_ids2 = [t.split(':')[2] for t in track_ids]
    embed_string = ",".join(track_ids2)
    #print track_ids
    #print embed_string
    return render_template('playlist.html', embed_string=embed_string, artist=artist, track=track)

if __name__ == '__main__':
    #app.run(debug=True)
    app.run()
