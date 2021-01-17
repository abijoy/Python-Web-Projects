from bs4 import BeautifulSoup
from requests import get
from requests.exceptions import RequestException
from contextlib import closing


headers = {
	"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.79 Safari/537.36"
}

def make_url_metro(song_title, artist_name):
	return 'http://www.metrolyrics.com/' + song_title.replace(' ', '-') + '-lyrics-' + artist_name.replace(' ', '-')

def make_url_az(song_title, artist_name):
	return f'https://www.azlyrics.com/lyrics/{artist_name}/{song_title}.html'

def simple_get(url):
	try:
		with closing(get(url, headers=headers)) as resp:
			# print(resp.status_code, resp.history)
			if resp.status_code == 200:
				if not resp.history:
					return resp.content
				elif resp.history[0].status_code == 301:
					return resp.content
				else:
					print('Redirection -> 302: lyrics not found!')
					return None
			else:
				print('Err -> 404: lyrics not found!')
				return None

	except RequestException:
		print('Internet connection is needed to download the lyrics')
		return None


def lyricsFinderMetro(song_title, artist_name):
	url = make_url_metro(song_title.strip(), artist_name.strip())
	raw_html = simple_get(url)
	if raw_html is None:
		print('lyrics Not Found.')
		return None

	html = BeautifulSoup(raw_html, 'html.parser')
	
	lyrics = ''

	for p in html.select('p'):
		s = [str(i) for i in p.contents]
		s = ''.join(s)
		s = s.replace('<br/>', '<br><br>')
		if p.has_attr('class') and p['class'][0] == 'verse':
			lyrics += '<p style="font-size:120%;color:#17A589">{}</p>'.format(s)
			if p.findAll('br'):
				lyrics += '<br>'

	return lyrics


def lyricsFinderAz(song_title, artist_name):
	song_title = song_title.replace("'", "")
	song_title = ''.join(song_title.strip().lower().split())
	artist_name = ''.join(artist_name.strip().lower().split())
	print(song_title, artist_name)
	url = make_url_az(song_title, artist_name)
	raw_html = simple_get(url)
	if raw_html is None:
		print('lyrics Not Found.')
		return None

	html = BeautifulSoup(raw_html, 'html.parser')

	lyrics = ''
	for div in html.select('div'):
		if not div.has_attr('class'):
			lyrics = str(div)

	return lyrics







