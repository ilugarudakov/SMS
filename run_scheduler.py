from server import Scheduler
from logger import logger

if __name__ == '__main__':

    logger.info('scheduler starting')
    try: Scheduler.start()
    except Exception as e: logger.error(f'Cant start sheduler! {e}')
