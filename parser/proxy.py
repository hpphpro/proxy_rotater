from bs4 import BeautifulSoup as BS

import base64
import re 

from parser import Requester
from config.utils import event_loop
from config.logger import logger


class Proxy:
    '''A sites with free proxy'''
    @staticmethod
    async def __hidemy(url='https://hidemy.name/ru/proxy-list/'):
        logger.info(f'fetching proxies from {url}...')
        response = await anext(Requester().get_data([url]))
        if response[0]:
            soup = BS(response[0], 'lxml')
            pagination = int(soup.select('div.pagination a')[-2].text)
            
            hidemy_urls = [f'https://hidemy.name/ru/proxy-list/?start={page}#list' for page in range(0, (pagination*64) + 64, 64)]
            proxies = set()
            async for urls_response in Requester().get_data(hidemy_urls):
                for response in urls_response:
                    if response:
                        soup = BS(response, 'lxml')
                        items = soup.select('div.table_block > table > tbody > tr')
                        for item in items:
                            ip = item.select('td')
                            if ip:
                                ip = ip[0].text
                            port = item.select('td')
                            if port:
                                port = port[1].text
                            proxies.add(f'http://{ip}:{port}')
            
            return proxies
        logger.error(f'failed to fetch proxies from {url}')
    
    @staticmethod
    async def __advanced(url='https://advanced.name/freeproxy'):
        logger.info(f'fetching proxies from {url}...')
        response = await anext(Requester().get_data([url]))
        if response[0]:
            soup = BS(response[0], 'lxml')
            pagination = int(soup.select('ul.pagination a')[-2].text)
            advanced_urls = [f'https://advanced.name/freeproxy?page={page}' for page in range(1, pagination + 1)]
            proxies = set()
            async for urls_response in Requester().get_data(advanced_urls):
                for response in urls_response:
                    if response:
                        soup = BS(response, 'lxml')
                        items = soup.select('table[id="table_proxies"] > tbody > tr')
                        for item in items:
                            ip = item.select_one('td[data-ip]')
                            if ip: 
                                ip = base64.b64decode(ip.get('data-ip')).decode()
                                
                            port = item.select_one('td[data-port]')
                            if port: 
                                port = base64.b64decode(port.get('data-port')).decode()

                            proxies.add(f'http://{ip}:{port}')
                        
            return proxies
        logger.error(f'failed to fetch proxies from {url}')
    
    @staticmethod
    async def __fpl(url='https://free-proxy-list.net/'):
        logger.info(f'fetching proxies from {url}...')
        response = await anext(Requester().get_data([url]))
        if response[0]:
            soup = BS(response[0], 'lxml')
            items = soup.select_one('textarea.form-control').text.split()
            proxies = set()
            for item in items:
                if item.count('.') == 3:
                    proxies.add(f'http://{item}')
                    
            return proxies
        logger.error(f'failed to fetch proxies from {url}')
    
    @staticmethod
    async def __htmlweb(url='https://htmlweb.ru/analiz/proxy_list.php&p=1?perpage=20'):
        logger.info(f'fetching proxies from {url}...')
        response = await anext(Requester().get_data([url]))
        if response[0]:
            soup = BS(response[0], 'lxml')
            pagination = int(soup.select_one('a[rel="last"]').text)
            htmlweb_urls = [f'https://htmlweb.ru/analiz/proxy_list.php&p={p}?perpage=20' for p in range(1, pagination + 1)]
            proxies = set()
            async for urls_response in Requester().get_data(htmlweb_urls):
                for response in urls_response:
                    if response:
                        soup = BS(response, 'lxml')
                        items = items = soup.select('tr > td')
                        for item in items:
                            if (proxy := re.search(r'\d{1,}.\d{1,}.\d{1,}:\d{1,}', item.text)):
                                proxies.add(f'http://{proxy.group()}')
                        
            return proxies
        logger.error(f'failed to fetch proxies from {url}')
        
    
    @classmethod
    async def get_proxies(cls):
        logger.info(f'Collecting proxies...')
        hidemy_set = await cls.__hidemy()
        advanced_set = await cls.__advanced()
        fpl_set = await cls.__fpl()
        htmlweb = await cls.__htmlweb()
        proxies = set()
        if hidemy_set:
            proxies = proxies | hidemy_set
        if advanced_set:
            proxies = proxies | advanced_set
        if fpl_set:
            proxies = proxies | fpl_set
        if htmlweb:
            proxies = proxies | htmlweb
            
        if not proxies:
            raise Exception('There is no free proxy, try to put yours instead')
        
        return proxies
    
     
@event_loop            
async def rotate(url, proxies: list|dict|set|tuple=None, timeout: float=20.0, step=100):
    if not proxies:
        proxies = await Proxy.get_proxies()
        
    if not isinstance(proxies, (list, set, tuple, dict)):
        raise TypeError(f'A proxies should be a list, set, tuple or a dict object, not {type(proxies).__name__}')

    return await Requester(step=step).rotate_proxies(url, proxies, timeout)
