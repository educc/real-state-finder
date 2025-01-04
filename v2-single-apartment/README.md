# v2-single-apartment

This program downloads the data from nexoinmobiliario, all the data downloaded is saved into ```nexo_cache``` folder so
the next time you run the program it will use the cache data. Remove the ```nexo_cache``` folder to download the data
again.

## Requirements

- Python 3.12
- Install requirements.txt

## How to run

```bash

python main.py

```

## nexo_web

This program run a website to show the data downloaded from nexoinmobiliario, it uses the cache data from the
```nexo_cache``` folder.

```bash

python nexo_web.py

```