import logging

logging.basicConfig(
  level=logging.DEBUG, # Global debug level
  format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', # Format of the logger
)

logger = logging.getLogger('sysmind')

# Log a basic message about the logging system
logger.info('Logging set to DEBUG.')
