import logging, sys

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s: %(message)s"
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format=LOG_FORMAT) 