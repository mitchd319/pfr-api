import os, time, requests
from bs4 import BeautifulSoup as bs
import requests
from . config import PARSER

''' This class exists to interact with PFR through a centralized object.
    Such a design enables me to collect and aggregate data, as well have fine control
    over the interaction to resolve problems such as rate limiting, which PFR recently implemented.
'''
class PFRWebsite(object):
    def __init__(self):
        self.pfr_rate_limiter = RateLimiter(refresh_time_seconds=60, allowed_calls_per_refresh_time=10)

    def get_soup_from_website(self, url):
        time.sleep(self.pfr_rate_limiter.get_delay_time())
        r = requests.get(url)
        return bs(r.content, PARSER)
    
    def get_soup_from_file(self, f):
        with open(f,'r', encoding='utf-8') as file:
            text = file.read()
        return bs(text, PARSER)


'''
This class is responsible for limiting the number of times a website is called,
according to configurable rules.
@refresh_time_seconds: The number of seconds until your rate refreshes (ex 20 calls per 60 seconds).
@allowed_calls_per_refresh_time: The number of calls you allowed per configured refresh time.
'''
class RateLimiter:
    def __init__(self, refresh_time_seconds, allowed_calls_per_refresh_time):
        self.refresh_time_seconds = refresh_time_seconds
        self.allowed_calls_per_refresh_time = allowed_calls_per_refresh_time
        self.buffer = []
    
    def get_delay_time(self):
        current_time = time.time()
        
        # Clear any items older than the refresh time
        self.buffer = [call_time for call_time in self.buffer if current_time - call_time <= self.refresh_time_seconds]
        if len(self.buffer) >= self.allowed_calls_per_refresh_time:
            oldest_call_time = self.buffer[0]
            delay_time = max(0, oldest_call_time + self.refresh_time_seconds - current_time)
            print(f'Rate Limiter: Continuing in {delay_time} seconds.')
            return delay_time
        
        self.buffer.append(current_time)
        return 0


'''Globals'''
# I created a class PFRWebsite to implement RateLimiting -- I am calling the website all over the place, so
# I needed a centralized location to limit my calls.
pfr_website_singleton = PFRWebsite()