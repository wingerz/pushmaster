# hack for python 2.6
import sys

if sys.version_info[:2] >= (2, 6):
	import logging
	logging.logMultiprocessing = False
