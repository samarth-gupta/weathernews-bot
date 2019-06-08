import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "weatherbot_secret.json"

import dialogflow_v2 as dialogflow
dialogflow_session_client = dialogflow.SessionsClient()
PROJECT_ID = "weatherbot-pmfbbh"

from weather import query_api

from gnewsclient import gnewsclient
client = gnewsclient.NewsClient()

from pymongo import MongoClient



def get_news(parameters):
	client.topic = parameters.get('news_type')
	client.language = parameters.get('language')
	country = parameters.get('geo-country')
	state = parameters.get('geo-state')
	city = parameters.get('geo-city')
	if country != None:
		client.location = country
	elif state != None:
		client.location = state
	elif city != None:
		client.location = city
	else:
		client.location = ''
	client.max_results = 5

	# print('Client:',client.topic,' | ',client.language,' | ',client.location)

	return client.get_news()

def get_weather(data):
	result = ''
	weather = data.get('weather',[{}])[0]
	wmain = weather.get('main')
	wdesc = weather.get('description')
	result += 'Weather Details\nMain: '+str(wmain)+'\nDescription: '+str(wdesc)
	main = data.get('main')
	temp = main.get('temp')
	temp_min = main.get('temp_min')
	temp_max = main.get('temp_max')
	result += '\nTemperature (C): '+str(temp)+'\nMinimum Temperature: '+str(temp_min)+'\nMaximum Temperature: '+str(temp_max)
	humidity = data.get('main').get('humidity')
	result += '\nHumidity: '+str(humidity);

	imgcode = weather.get('icon')
	img = 'http://openweathermap.org/img/w/'+imgcode+'.png'

	return str(result),img


def detect_intent_from_text(text, session_id, language_code='en'):
	session = dialogflow_session_client.session_path(PROJECT_ID, session_id)
	text_input = dialogflow.types.TextInput(text=text, language_code=language_code)
	query_input = dialogflow.types.QueryInput(text=text_input)
	response = dialogflow_session_client.detect_intent(session=session, query_input=query_input)
	return response.query_result

def fetch_reply(msg, session_id):
	response = detect_intent_from_text(msg,session_id)
	params = dict(response.parameters)
	params['msg']=msg
	params['intent']=response.intent.display_name

	dbclient = MongoClient('mongodb+srv://test:test@cluster0-z3gwz.mongodb.net/test?retryWrites=true&w=majority')
	db = dbclient.get_database('user_logs_db')
	records = db.user_logs


	news_type = params.get('news_type')
	city = params.get('geo-city')

	if news_type != None and news_type != '' and response.intent.display_name == 'get_news':

		news = get_news(params)

		if news == None or news == []:
			return 'Please try again later',''

		news_str = "Here are the news results:\n"

		for row in news:
			news_str += "\n\n{}\n{}".format(row['title'],row['link'])

		if records.find_one(params) == None:
			records.insert_one(params)

		return news_str,''

	if city != None and city != '' and response.intent.display_name == 'get_weather':

		data = query_api(city)

		if data['cod'] == '400':
			return 'Please try again later',''

		if records.find_one(params) == None:
			records.insert_one(params)

		return get_weather(data)

	return response.fulfillment_text,''