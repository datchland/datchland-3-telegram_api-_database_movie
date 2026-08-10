import requests

def get_movie_info_by_id(movie_id):
    url = f'https://moviesapi.ir/api/v1/movies/{movie_id}'
    response = requests.get(url)
    if response.status_code != 200:
        return 'ERROR'
    data = response.json()
    return {
        'title':       data['title'],
        'country':     data['country'],
        'director':    data['director'],
        'year':        data['year'],
        'imdb_rating': data['imdb_rating'],
    }


def get_movie_info_by_name(movie_name):
    url = f'https://moviesapi.ir/api/v1/movies'
    response = requests.get(url, params={'q': movie_name})
    if response.status_code != 200:
        return 'ERROR'
    data = response.json()
    results = data.get('data', [])
    if not results:
        return 'EMPTY'

    return results

def get_popular_movies():
    url = 'https://moviesapi.ir/api/v1/movies'
    response = requests.get(url)
    if response.status_code != 200:
        return 'ERROR'
    data = response.json()
    results = data.get('data', [])
    if not results:
        return 'EMPTY'
    return results 
