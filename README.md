# What is this?

[![](https://img.shields.io/docker/image-size/auburnsummer/bluebell)](https://hub.docker.com/r/auburnsummer/bluebell) [![](https://img.shields.io/github/license/auburnsummer/bluebell)](LICENSE)

This has two things:

- A Steam Workshop scraper (using [Scrapy][2])
- A Steam Workshop downloader (using [SteamCMD][1])

It's wrapped up in a web server with a simple API.

**By itself it does not provide a complete solution.**:

- It is very slow, because I do no caching or anything along those lines.
- There are no rate limits or other protections.

My use case for this is that I have another server which periodically syncs data from Steam Workshop using this
as a microservice. I know, microservices are terrible etc etc, but I think this is one of those cases where encapsulating
the weird proprietary platform in a microservice is probably a good idea.

So in my use-case, the end-user is never going to directly download from here. That's why I haven't bothered making the
performance any good.

# Quickstart

## environment variables

`STEAM_USER` = steam username
`STEAM_PASSWORD` = steam password

define these with `export` before you start

also you should install steamcmd, and log in at least once to remove the Steam Guard check

also you need bsdtar installed !!!!

## Docker container

The docker container probably doesn't work!! plz don't use it for now


## Scraping

Let's say we want to browse the workshop items for [Project Arrythmia][3]. From the URL,
the game ID of Project Arrythmia is `440310`. The endpoint `/<game_id>/levels` will trigger the scraper. For instance, if
you are running the Docker container on your local machine, you could go to `localhost:8000/440310/levels`.

It will take a while, but you will get back a JSON response with the item IDs for Project Arrythmia.

Notes:

- It always tries to scrape the entire Workshop for the game. This means that for things with _lots_ of workshop items,
  this will probably not finish. I guess I could implement pagination, but my use-case didn't need it so I haven't done that.
- There's a field called `iid`, which is just a concatenation of the game ID, ID, and last updated date.

## Downloading

I want to download the level [Alacrit][4], which has an `id` of `1959058900`. The endpoint for downloading is
`/<game_id>/<item_id>`. So I could go to `localhost:8000/440310/1959058900` and it would download.

By the way, this is also pretty slow. I think it's probably possible to stream the download as SteamCMD is downloading it,
but my use-case didn't need that so I didn't implement it. I wonder if there's a pattern here?

# Contributing

I don't think this is any use beyond my extremely narrow use-case that I made it for.

However, I am accepting pull requests. Note that the code for this is pretty damn messy. Ahhhhhh

# Copyright

(c) auburnsummer 2020

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

[1]: https://developer.valvesoftware.com/wiki/SteamCMD
[2]: https://scrapy.org/
[3]: https://steamcommunity.com/app/440310/workshop/
[4]: https://steamcommunity.com/sharedfiles/filedetails/?id=1959058900
