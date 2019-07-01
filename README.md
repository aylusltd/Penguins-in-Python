# Penguins-in-Python
## What is this?
A completely opensource, cross-platform game for kids. You control a penguin (or pretty much any avatar, you can just replace it) with the keyboard.

Try to avoid monsters and catch fish. It's not very hard.

You can harvest trees and rocks for some simple crafting.

## Why is it?
I'm an engineer. I like to share what I do with my kids. I thought others might like to too. Some day, I'd like to commission some artists to draw some pictures (either sprites or backgrounds), but right now the art is pretty much all from my kids. There's two images I found on Google under Commercial Reuse with Modifications (Tux the linux penguin and the virus monsters). If you own either of those images and don't want me to use them, please let me know at github@ayl.us. I'm happy to remove them if they are not actually open-source. Though please update your meta-data. You had to try pretty hard to get them into the Google results with that license.

I think it would be cool for my kids to see their art alongside professional artists work. But I think making video games is cool.

## What is it not?
A particulary fast, well-built game. It's meant primarily for ease of modification and legibility, not efficiency. It's also a side project I rarely work on that's grown much bigger than I anticipated, so it's not very well organized. I've opened it up with some issues though, and am trying to get some more eyes on it.

## So how do you play?
Move tux with the arrows. Avoid the monsters. Throw spears at them if you must, but resources are limited. You throw spears with the WAXD keys (w to throw a spear north, d east, a west, and x south).

You can place walls, make bricks, and go fishing too... A more thorough guide to come.

### Key Bindings
* p - Place a wall: Requires a wall in your inventory.
* r - Spear: Convert 1 Rock and 1 wood into 1 spear.
* b - Brick: Convert 2 Rock in your inventory to brick.
* h - Harvest: Collects whatever resource you're standing on. Trees give wood, rocks give Rock.
* f - Fish: Enters fishing mode. Click a neighboring square with a fish to collect it.
* l - Wall: Build a wall in your inventory. Requires 5 brick.


## Requirements
Should work on Mac, Windows, or Linux. Occassionally tested on Mac and Ubuntu. Not really on Windows. Good luck, though.
1. Python 3.5+

## Setup
I run in a virtual environment, and don't have a packaged binary yet, so good luck. J/k it's actually pretty easy:

From your terminal:
1. Clone the repo   
`git clone git@github.com:aylusltd/Penguins-in-Python.git`
2. Navigate into the folder   
`cd Penguins-in-Python`
3. Install VirtualEnv   
Instructions [here](https://virtualenv.pypa.io/en/latest/)
4. Create VirtualEnv   
`python3 -m virtualenv env`
5. Activate VirtualEnv   
`source env/bin/activate`
6. Install dependencies   
`pip install -r requirements.txt`
7. Launch game   
`python app.py`