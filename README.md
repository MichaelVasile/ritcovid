# RIT COVID-19 Tracker Discord Bot

The RIT COVID-19 Tracker is a Python-based Discord bot that uses the [BeautifulSoup library](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) to scrape data from [RIT's COVID-19 Dashboard](https://rit.edu/ready/dashboard).

## What can it do?

In it's current iteration, the bot can:
- Get the current RIT COVID-19 alert level
- Send alerts to specified Discord channels when the alert level changes
- Get current statistics from the RIT COVID-19 Dashboard

## Things we're working on

This was thrown together in my free time, so it is kind of janky right now. For a version 2.0, I'm looking to:
- Make it more efficient in scraping data
- Have actual data persistence using sqlite3
- Use Matplotlib to create graphs
- Be able to be dynamically bound to specific channels without having to rely on environment variables

## Interested in contributing or adding this to your server?

Reach out to me via Discord (Vaseline#1107) or through email [michaelvasile17@gmail.com](mailto:michaelvasile17@gmail.com).

## Project members
- [Michael Vasile](https://github.com/michaelvasile) (Project Lead)
- [Shantanav Saurav](https://github.com/shantanav)
- [~~aon mikl thomp~~](https://github.com/orthos)
- [Aaron Thompson](https://github.com/amikht)