import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, filename='bot_health.log',
                    format='%(asctime)s - %(levelname)s - %(message)s')

class GuardianMonitor:
    def __init__(self, max_load=5):
        self.max_load = max_load
        self.current_load = 0

    def validate_imports(self, bot_name):
        try:
            __import__(bot_name)
            logging.info(f'{bot_name} imported successfully.')
        except ImportError as e:
            logging.error(f'Failed to import {bot_name}: {str(e)}')

    def throttle_load(self):
        if self.current_load >= self.max_load:
            logging.warning('Max load reached, throttling...')
            time.sleep(5)  # Throttle for 5 seconds
        else:
            self.current_load += 1

    def health_check(self, bot_names):
        for bot in bot_names:
            self.validate_imports(bot)
            self.throttle_load()
            self.current_load -= 1  # Decrement load after processing

# Example usage
if __name__ == '__main__':
    monitor = GuardianMonitor(max_load=5)
    bot_list = ['bot_one', 'bot_two', 'bot_three']  # Replace with actual bot names
    monitor.health_check(bot_list)