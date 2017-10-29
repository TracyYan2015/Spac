#!/usr/bin/python
import logging
logging.basicConfig(level=logging.DEBUG, filename='TestLogging.log', filemode='w')

def main():
    logging.info('first line')
    logging.info('second line')

if __name__ == '__main__':
    main()