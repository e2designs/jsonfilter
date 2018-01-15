
Used for filtering through a nested JSON file.

usage: jsontool.py [-h] [-f FILENAME] [-v] [-o OUTFILE] [-i INDENT]
                   [-k KEYFILTER] [-d DATAFILTER]

A json parser with filters

optional arguments:
  -h, --help            show this help message and exit
  -f FILENAME, --filename FILENAME
                        The Json file to parse
  -v, --verbosity       Increase verbosity of console log
  -o OUTFILE, --outfile OUTFILE
                        File to output to
  -i INDENT, --indent INDENT
                        Number of spaces to indent
  -k KEYFILTER, --keyfilter KEYFILTER
                        Key filter for the json output separated by
                        "."page.module.element.note, use partial string or *
                        for all
  -d DATAFILTER, --datafilter DATAFILTER
                        Data Value filter of the key:value pair. NOTE:
                        keyfiltering occurs first.

