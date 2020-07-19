import requests
import json
import pyttsx3
import speech_recognition as sr
import re
import threading
import time


API_KEY = "tdhk7wMBV3Gw"
PROJECT_TOKEN = "tOHayEcR7Xvg"
RUN_TOKEN = "tTTKCPS2Fg3U"


class Data:
	''' Constructor '''
	def __init__(self, api_key, project_token):
		self.api_key = api_key
		self.project_token = project_token
		self.params = {
			"api_key": self.api_key
		}
		self.data = self.get_data()

	def get_data(self):
		''' 
		Gets data from the last run
		'''
		response = requests.get(f'https://www.parsehub.com/api/v2/projects/{self.project_token}/last_ready_run/data', params=self.params)
		data = json.loads(response.text)
		return data

	def get_total_cases(self):
		'''
		Retrieves the number of cases in total (active and non-active)
		'''
		data = self.data['total']

		for content in data:
			if content['name'] == "Coronavirus Cases:":
				return content['value']

	def get_total_deaths(self):
		'''
		Retrieves how many people died due to COVID-19
		'''
		data = self.data['total']

		for content in data:
			if content['name'] == "Deaths:":
				return content['value']

		return "0"

	def get_recovered(self):
		'''
		Retrieves information about how many people recovered 
		'''
		data = self.data['total']

		for content in data:
			if content['name'] == "Recovered:":
				return content['value']

	def get_country_data(self, country):
		'''
		Gets country data 
		'''
		data = self.data["country"]

		for content in data:
			if content['name'].lower() == country.lower():
				return content

		return "0"

	def get_list_of_countries(self):
		'''
		Gets a list of the countries
		'''
		countries = []
		for country in self.data['country']:
			countries.append(country['name'].lower())

		return countries

	def update_data(self):
		'''
		Updates data
		'''
		response = requests.post(f'https://www.parsehub.com/api/v2/projects/{self.project_token}/run', params=self.params)

		def poll():
			time.sleep(0.1)
			old_data = self.data
			while True:
				new_data = self.get_data()
				if new_data != old_data:
					self.data = new_data
					print("Data updated!")
					break
				time.sleep(5)


		t = threading.Thread(target=poll)
		t.start()


def speak(text):
	''' Announces Speech '''

	# Change the ID here in order to get a different voice
	voice_id = "com.apple.speech.synthesis.voice.samantha"

	engine = pyttsx3.init()
	engine.setProperty('voice', voice_id)
	engine.say(text)
	engine.runAndWait()


def get_audio():
	'''Listens for Audio'''
	r = sr.Recognizer()
	with sr.Microphone() as source:
		audio = r.listen(source)
		said = ""

		try:
			said = r.recognize_google(audio)
		except Exception as e:
			print("No audio was heard. Speak again.")

	return said.lower()


def main():
	data = Data(API_KEY, PROJECT_TOKEN)
	END_PHRASE = "exit"
	country_list = data.get_list_of_countries()

	# Information about worldwide and nationwide statistics
	TOTAL_PATTERNS = {
					re.compile("[\w\s]* total [\w\s]* cases"):data.get_total_cases,
					re.compile("[\w\s]* total cases"): data.get_total_cases,
                    re.compile("[\w\s]* total [\w\s]* deaths"): data.get_total_deaths,
                    re.compile("[\w\s]* total deaths"): data.get_total_deaths,
                    re.compile("[\w\s]* total [\w\s]* recovered"): data.get_recovered,
                    re.compile("[\w\s]* total recoveries"):data.get_recovered
					}

	COUNTRY_PATTERNS = {
					re.compile("[\w\s]* cases [\w\s]*"): lambda country: data.get_country_data(country)['total_cases'],
                    re.compile("[\w\s]* deaths [\w\s]*"): lambda country: data.get_country_data(country)['total_deaths'],
                    re.compile("[\w\s]* have died [\w\s]*"): lambda country: data.get_country_data(country)['total_deaths'],
                    re.compile("[\w\s]* recovered [\w\s]*"): lambda country: data.get_country_data(country)['total_recovered'],
                    re.compile("[\w\s]* new cases [\w\s]*"): lambda country: data.get_country_data(country)['new_cases'],
                    re.compile("[\w\s]* died [\w\s]*"): lambda country: data.get_country_data(country)['new_deaths'],
                    re.compile("[\w\s]* have died recently [\w\s]*"): lambda country: data.get_country_data(country)['new_deaths'],
                    re.compile("[\w\s]* population[\w\s]*"): lambda country: data.get_country_data(country)['population'],
                    re.compile("[\w\s]* active cases [\w\s]*"): lambda country: data.get_country_data(country)['active_cases']
					}

	UPDATE_COMMAND = "update"
	WAKE = "hey corona"

	while True:
		print("Listening...")
		text = get_audio()
		if text.count(WAKE) > 0:
			print(text)
			result = None
			'''
			General Questions and FAQ's 
			'''
			
			# Symptoms
			if 'symptoms' in text:
				speak("The symptoms of COVID-19 include, but is not limited to: fever or chills, cough, shortness of breath or difficulty breathing, fatigue, muscle or body aches, headache, new loss of taste or smell, sore throat, congestion or runny nose, nausea or vomiting, and or diarrhea.")
				speak("Would you like me to repeat that?")
				text = get_audio()
				if text == "yes":
					result = "The symptoms of COVID-19 include, but is not limited to: fever or chills, cough, shortness of breath or difficulty breathing, fatigue, muscle or body aches, headache, new loss of taste or smell, sore throat, congestion or runny nose, nausea or vomiting, and/or diarrhea. Serious symptoms include: Trouble breathing, Persisten pain or pressure in the chest, New confusion, Inability to wake or stay awake, Bluish lips or face. Call your medical provider for any other symptoms that are severe or concerning to you."	
					break
				elif text == "no":
					result = "Ok"
					break

			# Flu and Corona at the same time
			if 'flu and corona' in text:
				speak("Yes. It is possible to test positive for flu (as well as other respiratory infections) and COVID-19 at the same time.")
				break

			# Hobbies to pick up during quarantine
			if 'hobbies' in text or 'things' in text:
				speak("Some things to do during quarantine are: Yoga, Try to make a tidy work place if you're working from home, talk with friends through video conferencing, meditate, try new recipes, take virtual trip at home, and more.")
				break

			# How the virus spreads
			if "spread" in text or "transmit" in text:
				speak("The virus that causes COVID-19 spreads mainly from person to person, typically through respiratory droplets from coughing, sneezing, or talking.")
				break

			# Reason for COVID-19's name
			if "why is it being called coronavirus disease 2019" in text:
				speak("On February 11, 2020 the World Health Organization announced an official name for the disease that is causing the 2019 novel coronavirus outbreak, first identified in Wuhan China. The new name of this disease is coronavirus disease 2019, abbreviated as COVID-19. In COVID-19, ‘CO’ stands for ‘corona,’ ‘VI’ for ‘virus,’ and ‘D’ for disease. Formerly, this disease was referred to as “2019 novel coronavirus” or “2019-nCoV”. There are many types of human coronaviruses including some that commonly cause mild upper-respiratory tract illnesses. COVID-19 is a new disease, caused by a novel (or new) coronavirus that has not previously been seen in humans.")
				break

			# Origin for coronavirus
			if "origin" in text:
				speak("Coronavirus or COVID-19 orginated in Wuhan, China.")
				break
					
			# Vaccine availability
			if "vaccine" in text:
				speak("There is currently no vaccine to prevent coronavirus disease 2019 (COVID-19). The best way to prevent illness is to avoid being exposed to this virus. The virus is thought to spread mainly from person-to-person.")
				break

			# Difference between Coronavirus and COVID-19
			if "difference" in text:
				speak("Coronavirus is the virus that infects you, and COVID-19 is the name for the disease caused by COVID-19.")
				break

			# Cleaning    
			if "how to clean" in text or "routine clean" in text:     
				speak("Routine cleaning is the everyday cleaning practices that businesses and communities normally use to maintain a healthy environment. Surfaces frequently touched by multiple people, such as door handles, bathroom surfaces, and handrails, should be cleaned with soap and water or another detergent at least daily when facilities are in use. More frequent cleaning and disinfection may be required based on level of use. For example, certain surfaces and objects in public spaces, such as shopping carts and point of sale keypads, should be cleaned and disinfected before each use. Cleaning removes dirt and impurities, including germs, from surfaces. Cleaning alone does not kill germs, but it reduces the number of germs on a surface. For more information, see CDC's website.")     
				break     

			# Cleaning methods    
			if "kinds of disinfectants and cleaners" in text or "types of disinfectants and cleaners" in text:     
				speak("You can remove the virus from surfaces or break apart the virus with: Soap and water, Alcohol-based hand sanitizers containing at least 60 percent alcohol, Bleach solutions and bleach-based cleaners, Hydrogen peroxide and hydrogen-peroxide based cleaners. For more information, see CDC's website.")     
				break     

			# Effectiveness for alternative disinfection methods    
			if "effective are alternative disinfection" in text:     
				speak("The efficacy of these disinfection methods against the virus that causes COVID-19 is not known.EPA does not routinely review the safety or efficacy of pesticidal devices, such as UV lights, LED lights, or ultrasonic devices. Therefore, EPA cannot confirm whether, or under what circumstances, such products might be effective against the spread of COVID-19. For more information, see CDC's website.")     
				break

			# Location
			if "where are you" in text:
				speak("I am everywhere and nowhere.")
				break

			# Creator
			if "who made you" in text or "created you" in text:
				speak("I have been created by Srikar Kusumanchi")
				break

			if text == "hey corona":
				speak("Yes?")

			if "help" in text:
				speak("Would you like some help?")
				text = get_audio()
				if text == "yes":
					print("Hi, my name is Corona. To use me, say hey corona and whatever command you would like me to answer that's related to the coronavirus or COVID-19. To update the information, say hey corona update. To exit the program, say hey corona exit. Type 'voice.py' in a terminal window to figure out the different voices on your PC, so you can change the voice of the assistant.")
					speak("Hi my name is Corona. To use me, say hey corona and whatever command you would like me to answer that's related to the coronavirus or COVID-19. To update the information, say hey corona update. To exit the program, say hey corona exit.")
					continue
				elif text == "no":
					continue

			for pattern, func in COUNTRY_PATTERNS.items():
				if pattern.match(text):
					words = set(text.split(" "))
					for country in country_list:
						if country in words:
							result = func(country)
							break

			for pattern, func in TOTAL_PATTERNS.items():
				if pattern.match(text):
					result = func()
					break

			# Updates Data
			if text == WAKE + " " +UPDATE_COMMAND:
				result = "Data is being updated. This may take a moment!"
				data.update_data()

			if result:
				speak(result)

			if text.find(END_PHRASE) != -1:  # stop loop
				print("Exited!")
				break

main()