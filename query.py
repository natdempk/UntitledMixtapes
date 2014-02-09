#import spotimeta as sm
import pylast
import random
from pyechonest import config, artist, song

config.ECHO_NEST_API_KEY = "***REMOVED***"

def get_artist_num(song_max):
	if song_max == 12:
		return 10
	elif song_max == 14:
		return 8
	else:
		return 13

def do_everything(artist_name="Anamanaguchi", song_name="Endless Fantasy", song_max=8, diversity=0):

    similar_artist_num = get_artist_num(song_max)
    if diversity:
        similar_artist_num /= 2

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


    artistgrab = network.get_artist(artist_name) # get artist name from last.fm
    similar = artistgrab.get_similar()[0:similar_artist_num] # get similar artists
    similar_artists = []
    # get a specified number of similar artists
    [similar_artists.append(similar[i][0].get_name()) for i in range(len(similar))]
    similar_artist_num = len(similar_artists)

    if diversity: # get more kinda similar artists to mix in
        k_artistgrab = network.get_artist(similar_artists[0])
        k_similar = k_artistgrab.get_similar()[0:similar_artist_num]
        k_similar_artists = []
        [k_similar_artists.append(k_similar[i][0].get_name()) for i in range(len(similar))]
        k_similar_artist_num = len(k_similar_artists)

    #for i in range(similar_artist_num):
    #    if i < len(similar):
    #        similar_artists.append(similar[i][0].get_name())
    #    else:
    #        similar_artist_num = len(similar_artists)
    #        break

    the_song = song.search(title=song_name, artist=artist_name)[0] # get requested song
    the_song_info = the_song.get_audio_summary() # get echonest song info

    sim_songs = []
    k_sim_songs = []

    for i in range(similar_artist_num): # for each similar artist
        a = artist.Artist(similar_artists[i]) # get artist info from echonest
        l = a.get_songs() # get songs for artist
        if l:
            #for j in range(song_max):
                #sim_songs.append(l[random.randint(0, len(l)-1)])
            # add a number of random songs
            [sim_songs.append(l[random.randint(0, len(l)-1)]) for j in range(song_max)]
        if diversity:
            d = artist.Artist(k_similar_artists[i])
            m = d.get_songs()
            if m:
                [k_sim_songs.append(m[random.randint(0, len(m)-1)]) for j in range(song_max)]

    the_artist = artist.Artist(artist_name)
    the_songs = the_artist.get_songs()[:5]
    first_song = the_songs[random.randint(0, len(the_songs)-1)]

    seen = set()
    seen_add = seen.add
    sim_songs = [ x for x in sim_songs if x not in seen and not seen_add(x)]

    sim_songs_info = []

    for i in range(len(sim_songs)): # for similar songs
        sim_songs_info.append(sim_songs[i].get_audio_summary()) # get audio info
        sim_songs_info[i]['song_handle'] = sim_songs[i]

    # filter to songs with similar energy
    sim_songs_info = filter(lambda k: k[u'energy'] < the_song_info[u'energy']+.3 and
    				      k[u'energy'] > the_song_info[u'energy']-.3, sim_songs_info)

    # sort songs by tempo
    sim_songs_info = sorted(sim_songs_info, key=lambda k: k[u'tempo'])

    # divide into slower and faster songs
    slow_songs = sorted(sim_songs_info[:len(sim_songs_info)/2],
                        key=lambda k: k[u'duration'])
    fast_songs = sorted(sim_songs_info[len(sim_songs_info)/2:],
                        key=lambda k: k[u'duration'])

    # do the same for
    if diversity:
        k_seen = set()
        k_seen_add = k_seen.add
        k_sim_songs = [x for x in k_sim_songs if x not in seen and not k_seen_add(x)]

        k_sim_songs_info = []

        for i in range(len(k_sim_songs)):
            k_sim_songs_info.append(k_sim_songs[i].get_audio_summary())
            k_sim_songs_info[i]['song_handle'] = k_sim_songs[i]

        # filter to songs with similar energy
        k_sim_songs_info = filter(lambda k: k[u'energy'] < the_song_info[u'energy']+.3 and
                              k[u'energy'] > the_song_info[u'energy']-.3, k_sim_songs_info)

        # sort songs by tempo
        k_sim_songs_info = sorted(k_sim_songs_info, key=lambda k: k[u'tempo'])

        # divide into slower and faster songs
        k_slow_songs = sorted(k_sim_songs_info[:len(k_sim_songs_info)/2],
                            key=lambda k: k[u'duration'])
        k_fast_songs = sorted(k_sim_songs_info[len(k_sim_songs_info)/2:],
                            key=lambda k: k[u'duration'])


    total_info = []
    counter = 0


    if diversity:
        lists = [fast_songs, slow_songs, k_fast_songs, k_slow_songs]
        for i in range(song_max):
            cur_list = lists[i%4]
            flag = True
            while flag == True:
                flag = False
                info = cur_list[random.randint(0, len(cur_list)-1)]
                for j in range(len(total_info)):
                    if info['song_handle'].artist_name == total_info[j]['song_handle'].artist_name:
                        counter += 1
                        if counter < 100:
                            flag = True
            total_info.append(info)
    else:
        for i in range(song_max/2):
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

    total_res = [[first_song, the_artist]]

    for i in range(len(total_info)):
        total_res.append([total_info[i]['song_handle'].title,
                          total_info[i]['song_handle'].artist_name])

    return total_res

