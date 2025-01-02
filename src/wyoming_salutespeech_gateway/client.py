__package__ = 'wyoming_salutespeech_gateway'

import certifi
import requests
from uuid import uuid4
from . import app, ca_cert


# region =============================================== Subroutines

def _get_auth_token() -> str:
	"""Get authentication token"""

	# Check if the token expired
	if not app.check_if_token_expired():
		app.LOGGER.debug(f"Access token is still valid, using the stored one.")
		return app.token

	# If the token is expired proceed to get a new one
	app.LOGGER.debug(f"Access token is expired, getting a new one.")
	url = app.cli_args.sber_auth_url
	payload = 'scope=SALUTE_SPEECH_PERS'
	headers = {
	  'Content-Type': 'application/x-www-form-urlencoded',
	  'Accept': 'application/json',
	  'RqUID': str( uuid4() ),
	  'Authorization': f'Basic {app.cli_args.auth_key}'
	}
	response = requests.request("POST", url, headers=headers, data=payload)

	if response.status_code == 200:
		app.token = response.json().get('access_token')
		app.token_expiration_time = response.json().get('expires_at')
		app.LOGGER.debug(f'Access token is successfully received.')
		return app.token
	else:
		app.LOGGER.debug(f"Failed to get an access token: response status code: {response.status_code}, response text: '{response.text}'.")
		return ''


# endregion
# region =============================================== Interface

def setup_ca_cert() -> None:
	"""Place custom CA certificate in the app's certificate storage"""

	try:
		app.LOGGER.debug('Checking SSL connection to the SberSpeech service.')
		requests.get(app.cli_args.sber_auth_url)
		app.LOGGER.debug('SSL connection OK, required CA certificate is presented in the Certifi store.')
	except requests.exceptions.SSLError:
		app.LOGGER.debug('SSL error, it seems there is no required CA certificate in the Certifi store. Adding one.')
		with open(certifi.where(), 'ab') as certifi_ca_store:
			certifi_ca_store.write( ca_cert.get() )
	return


def recognize(audio: bytes, language: str) -> str:
	"""Recognize the speech"""

	headers = {
	  	#'Content-Type': 'audio/mpeg',
		'Content-Type': 'audio/x-pcm;bit=16;rate=16000',
	  	'Accept': 'application/json',
	  	'RqUID': str( uuid4() ),
		'Authorization': f'Bearer {_get_auth_token()}'
	}
	params = {
		'language': language,
		'model': app.cli_args.salutespeech_model,
		'sample_rate': 16000
	}

	# Reuse HTTP(S) session if possible
	if not app.client_http_session:
		app.LOGGER.debug("Creating a new HTTP(S) session with the cloud service.")
		app.client_http_session = requests.Session()
	else:
		app.LOGGER.debug("Reusing the existing HTTP(S) session with the cloud service.")

	response = app.client_http_session.request("POST", app.cli_args.salutespeech_url, headers=headers, params=params, data=audio)
	app.LOGGER.debug(f"Response JSON: {str(response.json())}.")

	if response.status_code == 200:
		app.LOGGER.debug("Audio uploaded successfully")
		return response.json().get('result')[0]
	else:
		app.LOGGER.debug(f"Failed to upload audio: response status code: {response.status_code}, response text: '{response.text}'.")
		return ''


# endregion
