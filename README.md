# stonks read backend
This repository contains details for [stonksread.com](https://www.stonksread.com) backend

## Application overview
1. The python script uses the praw reddit stream function to get comments and submissions.  
2. Then the text in the comments and submissions are run through SPACY model to get nouns and entities
3. The nouns and entities are compared against ticket symbols from [NASDAQ FTP server](http://www.nasdaqtrader.com/trader.aspx?id=symboldirdefs) which is locally cached at `symbols_directory`
4. If symbols match, the data is tagged with ticket symbol
5. Get the number of posts by the author and append to the data
6. Update author posts data
7. Push data to deepstream server
8. Optionally write the data to a file for later use

The backend uses the following systems
1. [deepstream open realtime server](https://deepstream.io/) - To stream data to react frontend using websockets
2. redis - currently only used to store number of posts by a user
3. python client using praw - to get data from reddit
4. spacy - currently only used to extract ticker symbols

## Installation
1. Install deepstream by following instructions [here](https://deepstream.io/tutorials/getting-started/javascript/)
2. Setup install python3 and virtualenv. Then install the dependencies
   ```
    virtualenv -p python3 venv
    source venv/bin/activate
    pip install -r requirements.txt
   ```

2. Update credentials
   ```
    cp env.sh.sample .env.sh
    chmod 0755 *.sh
   ```
3. Install Redis. [instructions](https://redis.io/topics/quickstart)
   ```
   # Your linux distribution may have binaries. Eg on Ubuntu run this command
   sudo apt install redis-server
   ```
4. Install spacy model
   ```
   python -m spacy download en_core_web_sm
   ```
5. Update `BASE_DIR` in wsb_comments.sh
6. Test
   ```
   ./wsb_comments.sh
   # you should see files generated in <BASE_DIR>/data directory
   ```
7. If your OS supports systemmd, install the service to automatically start and restart incase of errors
   ```
   sudo cp wsb_comments.service /etc/systemd/system
   ```
8. Start the streaming client
   ```
   sudo systemctl restart wsb_comments.service
   ```
9. If you are saving the comments/submissions, it's probably a good idea to compress them to save disk space. 
   a. To compress first update `BASE_DIR` in compress.sh
   b. Install compress into crontab [instructions](https://help.ubuntu.com/community/CronHowto)
   

To start/stop/restart using the following commands
```
sudo systemctl start wsb_comments.service
sudo systemctl stop wsb_comments.service
sudo systemctl restart wsb_comments.service

```

TODO
1. Create ansible playbook to install everything
2. Add parent comment/submission ticker symbol to the data 

