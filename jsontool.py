#!/usr/bin/env python

"""
Improved mjson.tool for python
"""

import sys
import json
import argparse
import logging

def main():
    jsoncall = json_tool()
    jsoncall.import_file()
    jsoncall.export_file()

class json_tool(object):
    """
    :Description: A Json filtering tool. Will take in a file or STDIN

    """

    def __init__(self):
        """
        :Description: Inits the json_tool class.
        """
        self.inputdata = {}
        self.outputdata = {}
        self.args = get_args()
        self.logger = self.set_logger(self.args.verbosity)
        self.logger.info(u'Args:{}'.format(self.args))

        if self.args.filename:
            self.infile = open(self.args.filename, 'r')
        else:
            self.infile = sys.stdin

        if self.args.outfile:
            self.outfile = open(self.args.outfile, 'w')
        else:
            self.outfile = sys.stdout

    def set_logger(self, level):
        """
        Setup for logging level
        """
        if level > 4:
            level = 4

        levels = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG']
        logger = logging.Logger('json_tool')
        handler = logging.StreamHandler()
        handler.setLevel(levels[level])
        logger.addHandler(handler)
        logger.info('Logger initilized')
        return logger

    def import_file(self):
        """
        Imports the json file or stdin as a dictionary.
        """
        self.inputdata = json.load(self.infile)
        self.outputdata = self.inputdata
        self.logger.info('Json file Loaded')
        self.logger.debug(u'JSON:{d}'.format(d=self.inputdata))

    def filter_keys(self):
        """
        Function for filtering on the keys of the json entry
        """
        filters = self.args.keyfilter.split('.')
        self.logger.info(u'Filtering with:{f}'.format(f=filters))
        data = self.inputdata
        newdata = {}
        for key, value in data.items():
            self.logger.info(u'\nProcessing Key:{k}'.format(k=key))
            returned_data = dict_key_filter(key, value, filters, self.logger)
            if bool(returned_data):
                newdata[key] = returned_data
            self.logger.info(u'Data After filter:{d}'.format(d=newdata))
        self.outputdata = newdata

    def filter_values(self):
        """
        Function for filtering on the values of the json entry
        """
        dfilter = self.args.datafilter
        self.logger.info(u'Filtering values with:{f}'.format(f=dfilter))
        data = self.outputdata
        newdata = {}
        for key, value in data.items():
            self.logger.info(u'\nProcessing Key:{k}, value:{v}'.format(k=key,
                                                                      v=value))
            returned_data = dict_value_filter(key, value, dfilter, self.logger)
            if bool(returned_data):
                newdata[key] = returned_data
            self.logger.info(u'Data after filter:{d}'.format(d=newdata))

        self.outputdata = newdata

    def export_file(self):
        """
        Calls the filters and exports the filtered data in json format.
        """
        if self.args.keyfilter:
            self.filter_keys()
        if self.args.datafilter:
            self.filter_values()
        json.dump(self.outputdata, self.outfile, indent=self.args.indent)
        self.outfile.write('\n')

def dict_key_filter(key, data, filters, logger):
    """
    Manager for filtering on the keys in a dictionary. Will loop for every level
    of fliter provided. e.g. filters=['one', 'two', three'] will result in 3
    loops of the dictionary.

    :param key:     Dictionary key string.
    :param data:    The data assinged to the key.
    :param filters: List of filters.
    :param logger:  Logger instance to use.

    :return dict:   Dictionary filtered on keys.
    """
    logger.info(u'Dict_key_filter key:{k}, filters:{f}'.format(k=key, f=filters))
    logger.info(u'Data:{d}'.format(d=data))
    remain_filters = []
    if filters:
        curfilter = filters[0]
    else:
        logger.info('No more filters to process')
        return data
    if len(filters) > 1:
        remain_filters = filters[1:]

    newdata = {}
    if curfilter == '*':
        logger.info('Setting filter to empty string')
        curfilter = ''

    logger.info(u'Filtering on {f}'.format(f=curfilter))
    if curfilter in key:
        logger.info('Setting new data to empty dictionary')
        if isinstance(data, dict) and remain_filters:
            logger.info('Processing next level dictionary')
            for nextkey, nextdata in data.items():
                logger.info(u'\nProcessing nextkey: {k}'.format(k=nextkey))
                returned_data = dict_key_filter(nextkey, nextdata, remain_filters,
                                                logger)
                logger.info(u'NextKey returned: {d}'.format(d=newdata))
                if bool(returned_data):
                    newdata[nextkey] = returned_data
        else:
            newdata[key] = data
            logger.info('Nothing more to process')
    logger.info(u'Returning data:{d}'.format(d=newdata))
    return newdata

def dict_value_filter(key, data, dfilter, logger):
    """
    Returns all entries where the value of the object is equal to the data
    filter.

    :param key:     Dictionary key string.
    :param data:    The data assinged to the key.
    :param dfilter: data filter
    :param logger:  Logger instance to use.

    :return dict:   Dictionary filtered on values.
    """

    logger.info(u'dict_value_filter:{l}'.format(l=locals()))
    newdata = {}
    if isinstance(data, dict):
        for nextkey, nextdata in data.items():
            returned_data = dict_value_filter(nextkey, nextdata, dfilter,
                                              logger)
            if bool(returned_data):
                newdata[nextkey] = returned_data
    elif isinstance(data, list):
        logger.info('Processing List:{}'.format(data))

        for item in data:
            logger.info(u'Process list:{}'.format(data))
            if isinstance(item, dict):
                logger.info('Found a dictionary:{}'.format(item))
                logger.info('Calling dict_value_filter:{k},{d},{f}'
                            ''.format(k=key,d=item, f=dfilter))
                returned_data = dict_value_filter(key, item, dfilter, logger)
                if bool(returned_data):
                    newdata = returned_data
    elif dfilter in unicode(data):
        newdata = data
    else:
        logger.info(u'Skipping data entry:{d}'.format(d=data))

    return newdata

def get_args():
    """
    Argument parser for this module
    """
    parser = argparse.ArgumentParser(description='A json parser with filters')
    parser.add_argument('-f', '--filename', help='The Json file to parse')
    parser.add_argument('-v', '--verbosity', action='count', default=0,
                        help='Increase verbosity of console log')
    parser.add_argument('-o', '--outfile', type=str, help='File to output to')
    parser.add_argument('-i', '--indent', type=int, default=4,
                        help='Number of spaces to indent')
    parser.add_argument('-k', '--keyfilter',
                        help=('Key filter for the json output separated by "."'
                              'page.module.element.note, use partial string'
                              ' or * for all'))
    parser.add_argument('-d', '--datafilter', type=str,
                        help=('Data Value filter of the key:value pair. '
                              'NOTE: keyfiltering occurs first.'))
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    main()
