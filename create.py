import spotify

def create_playlist(tracks):
    config = spotify.Config()
    session = spotify.Session(config=config)

    # login with remembered
    session.relogin()

    session.process_events()

    sp_tracks = []

    # get spotify tracks
    for t in tracks:
        print t
        search = session.search('artist:%s title:%s' % (t[0], t[1]))
        search.load()
        if search.tracks:
            sp_tracks.append(search.tracks[0])

    container = session.playlist_container
    container.load()
    session.process_events()

    pl = container.add_new_playlist('Untitled - %s' % t[0][1])
    session.process_events()

    pl.add_tracks(sp_tracks)
    session.process_events()
    session.process_events()
    session.process_events()
    session.process_events()
    session.process_events()
    session.process_events()
    session.process_events()
    session.process_events()
    session.process_events()
    session.process_events()
    session.process_events()
    session.process_events()
    session.process_events()
    session.process_events()
    session.process_events()
    session.process_events()
    session.process_events()
    session.process_events()
    session.process_events()
    session.process_events()

    return pl.link