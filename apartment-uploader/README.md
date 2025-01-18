# apartment-uploader

A python script that query the sqlite3 apartment database to get the top apartments. The output is the
top.json, this file will be upload to the FTP server.

## requirements

- Python 3.13

## How to run

```bash

# setting log dir to the current directory
export APARTMENT_UPLOADER_LOG_DIR=./

python main.py \
    --sqlite-db /path/to/your/sqlite3.db \
    --ftp-user your_ftp_username \
    --ftp-password your_ftp_password \
    --ftp-filename apartment_data.json \
    --ftp-server ftp.yourserver.com
```

## How is this related to depabarato.com

Depabarato.com web site uses a top.json file that contains all apartments that must be shown in the website.
This application produces the top.json file for the website.