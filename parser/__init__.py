import asyncio, aiohttp

from config import HEADERS
from config.logger import logger





class Requester:
    '''Getting data from urls and also check's the proxy'''
    __instance = None
    
    def __new__(cls, step: int=None, *args, **kwargs):
        '''A singleton class'''
        if not cls.__instance:
            cls.__instance = super(Requester, cls).__new__(cls, *args, **kwargs)
        return cls.__instance
    
    def __init__(self, step: int=20):
        self.step = step
    
 
    async def check_proxy(self, url, session, proxy):
        try:
            async with session.get(url, proxy=proxy) as response:
                if response.status == 200:
                    return proxy
        except Exception:
            logger.info(f'Useless proxy: {proxy} for url: {url}')
                
  
    async def fetch_data(self, url, session):
        retries = 1

        while retries < 6:
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.read()
                    break
            except Exception:
                retries += 1
                await asyncio.sleep(3)
                
        if retries == 6:
            raise Exception('Max connections retries exceeded')
    
   
    async def collect_tasks(self, urls, session):
        step = self.step if len(urls) >= self.step else len(urls)
        tasks = set()
        for index in range(0, len(urls), step):
            for url in urls[index:step+index]:
                tasks.add(asyncio.create_task(self.fetch_data(url, session)))
            yield await asyncio.gather(*tasks)
            tasks.clear()
            
          
    async def collect_proxies(self, url, session, proxies):
        proxies = [f'http://{proxy.strip()}' if not proxy.startswith('http://') else proxy.strip() for proxy in proxies]
        step = self.step if len(proxies) >= self.step else len(proxies)
        tasks = set()
        for index in range(0, len(proxies), step):
            for proxy in proxies[index:step+index]:
                tasks.add(asyncio.create_task(self.check_proxy(url, session, proxy)))
            yield await asyncio.gather(*tasks)
            tasks.clear()
            
  
    async def rotate_proxies(self, url, proxies, timeout=5):
        timeout = aiohttp.ClientTimeout(total=float(timeout))
        async with aiohttp.ClientSession(headers=HEADERS, timeout=timeout) as session:
            async for proxies in self.collect_proxies(url, session, proxies):
                for proxy in proxies:
                    if proxy:
                        with open('best_match_proxies.txt', 'a', encoding='utf-8') as file:
                            file.write(proxy + '\n')

    async def get_data(self, urls):
        async with aiohttp.ClientSession(headers=HEADERS) as session:
            async for response in self.collect_tasks(urls, session):
                yield response

