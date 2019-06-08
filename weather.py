import requests
from keys import OWM_API_KEY,OWM_API_URL

API_KEY = OWM_API_KEY
API_URL = OWM_API_URL


def query_api(city):
	try:
		print(API_URL.format(city, API_KEY))
		data = requests.get(API_URL.format(city, API_KEY)).json()
	except Exception as exc:
		print(exc)
		data = None
	return data