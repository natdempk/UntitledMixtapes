#import spotimeta as sm
import pylast
import random
from pyechonest import config, artist, song

config.ECHO_NEST_API_KEY = "***REMOVED***"

def do_everything(artist_name, song_name, song_max=8, diversity=0):

    similar_artist_num = 13
    song_max -= 2

    '''
    search = sm.search_artist("The XX")
    print search['result'][0]['href']
    '''

    API_KEY = "***REMOVED***"
    API_SECRET = "***REMOVED***"

    network = pylast.LastFMNetwork(api_key = API_KEY, api_secret =
        API_SECRET, username="natdempk",
                    password_hash = "***REMOVED***")


    artistgrab = network.get_artist(artist_name)
    similar = artistgrab.get_similar()[0:similar_artist_num]
    similar_artists = []
    if diversity: # get more similar artists
        kinda_similar_artists = artistgrab.get_similar()[0:similar_artist_num]


    for i in range(similar_artist_num):
        if i < len(similar):
            similar_artists.append(similar[i][0].get_name())
        else:
            similar_artist_num = len(similar_artists)
            break

    the_song = song.search(title=song_name, artist=artist_name)[0]
    the_song_info = the_song.get_audio_summary()

    sim_songs = []

    for i in range(similar_artist_num):
        a = artist.Artist(similar_artists[i])
        l = a.get_songs()
        if l != []:
            for j in range(song_max):
                sim_songs.append(l[random.randint(0, len(l)-1)])

    seen = set()
    seen_add = seen.add
    sim_songs = [ x for x in sim_songs if x not in seen and not seen_add(x)]

    sim_songs_ids = []
    '''
    for i in range(len(sim_songs)):
        sim_songs_ids.append(song.search(title=sim_songs[i])[0].id)
    '''
    sim_songs_info = []

    for i in range(len(sim_songs)):
        sim_songs_info.append(sim_songs[i].get_audio_summary())
        sim_songs_info[i]['song_handle'] = sim_songs[i]

    sim_songs_info = filter(lambda k: k[u'energy'] < the_song_info[u'energy']+.3 and
    				      k[u'energy'] > the_song_info[u'energy']-.3, sim_songs_info)

    sim_songs_info = sorted(sim_songs_info, key=lambda k: k[u'tempo'])

    slow_songs = sorted(sim_songs_info[:len(sim_songs_info)/2],
                        key=lambda k: k[u'duration'])
    fast_songs = sorted(sim_songs_info[len(sim_songs_info)/2:],
                        key=lambda k: k[u'duration'])

    total_info = []

    counter = 0

    for i in range(4):
        flag = True
        while flag == True:
            flag = False
            info = fast_songs[random.randint(0, len(fast_songs)-1)]
            for j in range(len(total_info)):
                if info['song_handle'].artist_name == total_info[j]['song_handle'].artist_name:
                    counter += 1
                    if counter < 100:
                        flag = True
        total_info.append(info)
        flag = True
        while flag == True:
            flag = False
            info = slow_songs[random.randint(0, len(slow_songs)-1)]
            for j in range(len(total_info)):
                if info['song_handle'].artist_name == total_info[j]['song_handle'].artist_name:
                    counter += 1
                    if counter < 100:
                        flag = True
        total_info.append(info)

    total_res = []

    for i in range(len(total_info)):
        total_res.append([total_info[i]['song_handle'].title,
                          total_info[i]['song_handle'].artist_name])

    return total_res

