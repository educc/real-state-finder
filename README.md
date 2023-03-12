# What it is
A really simple scraping tool to extract data from a web page that contains real state data.

# HOW TO RUN
- Step 1: View source from this page and look for these variable 'search_data'.

https://nexoinmobiliario.pe/busqueda/venta-de-departamentos-en-lima-lima-1501

- Step 2: Paste as json in the "data/search_data.json" file.
- Step 3: run in the console 
```sh
#minimal, apartments from Lima
scala-cli run .

#full args
scala-cli run . -- --url https://nexoinmobiliario.pe/busqueda/venta-de-departamentos-en-arequipa-4
```
