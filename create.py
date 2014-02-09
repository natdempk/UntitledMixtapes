import spotify
import time

def create_playlist(tracks):
    config = spotify.Config()
    config.user_agent = 'Untitled Mixtapes'
    session = spotify.Session(config=config)

    # login with remembered
    session.relogin()
    session.process_events()

    sp_tracks = []

    # get spotify tracks
    for t in tracks:
        print t
        search = session.search('artist:%s title:%s' % (t[0], t[1]))
        session.process_events()
        search.load()
        session.process_events()

        while not search.is_loaded:
            pass
        #time.sleep(0.5)
        if search.tracks:
            print tracks
            sp_tracks.append(search.tracks[0].link.uri.split(':')[2])

    print sp_tracks
    return sp_tracks