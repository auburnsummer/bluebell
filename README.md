I'm still working on this, will do a proper readme later

But if you want to try and use this now...

1.  install the requirements. I think it's sanic, scrapy, and dateparser.
2.  run something like `scrapy crawl WorkshopListing -a game_id=GAME_ID -o out.json`
3.  or: run `python main.py` and then go to `localhost:8000/GAME_ID/levels`
4.  (you get the GAME_ID from the steam workshop URL for the game)

How do you download the levels? I haven't done that yet, but it will work via automating
steamcmd.
