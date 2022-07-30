from parser.proxy import rotate







def main():
    '''You also can put your proxies
    step variable depends on your internet speed and also on a proxies number that you have
    >>> rotate(url=<mysite>, proxies=<myproxieslist>, step=<myfavoritenumber>)'''
    rotate(url='https://www.google.com/', step=200)
    
    
if __name__ == '__main__':
    main()