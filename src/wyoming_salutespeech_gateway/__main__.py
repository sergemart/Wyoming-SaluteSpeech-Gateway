__package__ = 'wyoming_salutespeech_gateway'

import logging
from . import app


def main():
    """ Prepare the app context and start the app """
    app.parse_arguments()
    app.setup_custom_logger('root')
    app.start()


""" Entrypoint """
if __name__ == "__main__":
    main()
