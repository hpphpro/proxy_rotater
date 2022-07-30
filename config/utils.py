from bs4 import BeautifulSoup as BS

import asyncio 

from parser import Requester


def event_loop(f):
    def decorator(*args, **kwargs):
        try:
            asyncio.get_running_loop()
        except RuntimeError: 
            return asyncio.run(f(*args, **kwargs))
        
        return f(*args, **kwargs)
    
    return decorator
    
@event_loop
async def get_useragents():
    api = (
        'https://developers.whatismybrowser.com/useragents/explore/operating_system_name/windows/',
        'https://developers.whatismybrowser.com/useragents/explore/operating_system_name/linux/',
        'https://developers.whatismybrowser.com/useragents/explore/operating_system_name/android/',
        'https://developers.whatismybrowser.com/useragents/explore/operating_system_name/macos/',
        'https://developers.whatismybrowser.com/useragents/explore/operating_system_name/fire-os/',
        'https://developers.whatismybrowser.com/useragents/explore/operating_system_name/android/',
        'https://developers.whatismybrowser.com/useragents/explore/operating_system_name/ios/',
        'https://developers.whatismybrowser.com/useragents/explore/operating_system_name/mac-os-x/',
        'https://developers.whatismybrowser.com/useragents/explore/operating_system_name/symbian/',
        'https://developers.whatismybrowser.com/useragents/explore/operating_system_name/chrome-os/',
    )
    
    async for api_response in Requester().get_data(api):
        for response in api_response:
            soup = BS(response, 'lxml')
            items = soup.select('table > tbody > tr')
            for item in items:
                user_agent = item.select_one('a.code')
                if user_agent:
                    with open('user_agents_list.txt', 'a', encoding='utf-8') as file:
                        file.write(user_agent.text + '\n')