# v2-single-apartment

This program creates an excel or sqlite3 file that contains the cheapest
apartment for every project and bedrooms combination found in lima using nexoinmobiliario website.

If you use the param `--use-cache` all the data downloaded is saved into ```nexo_cache``` folder so
the next time you run the program it will use the cache data. Remove the ```nexo_cache``` folder to download the data
again.

## Requirements

- Python 3.12
- Install requirements.txt

## How to run

Parameters

```bash

#usage: main.py [-h] [-o {all,sqlite3,excel}] [-od OUTPUT_DIR] [--use-cache] [--test]
#
#Process some integers.
#
#options:
#  -h, --help            show this help message and exit
#  -o {all,sqlite3,excel}, --output {all,sqlite3,excel}
#                        Output format (default: excel)
#  -od OUTPUT_DIR, --output-dir OUTPUT_DIR
#                        Directory to save the output files
#  --use-cache           When true, the html scrapped are saved to re-use next run.
#  --test                Only process one single record to finish quickly and check if everything works as expected


python main.py

```

## How to test

This runs one single record of data downloaded from nexoinmobiliario to finish quickly and check if everything works as
expected.

```bash
python main.py -o all --use-cache --test
```

## nexo_web

This program run a website to show the data downloaded from nexoinmobiliario, it uses the cache data from the
```nexo_cache``` folder.

```bash

python nexo_web.py

```