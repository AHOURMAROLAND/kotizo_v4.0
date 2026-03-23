import logging
import json
from datetime import datetime

class KotizoJSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
        }
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        return json.dumps(log_data)

def get_logger(name='kotizo'):
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(KotizoJSONFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
    return logger