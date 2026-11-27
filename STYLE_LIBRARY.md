# Style library: map-explainer reels (learned from reference videos)

The user sends reference reels from a Facebook page that posts map/explainer comedy videos (one post a week).
For every reference: study the technique, save it here, then make ORIGINAL videos on different topics.
Never copy the script, topic, characters or assets of a reference. Everything we publish is self-made
(procedural maps from Natural Earth outlines, cairo-drawn cartoons) or public domain.

## Shared formula (all references so far)
- Hook in the first 3 s, shown on the map: "This is X. And this is Y." then a surprising fact about them.
- A question the viewer has never thought about ("how did this happen?") followed by "Let's break it down" type turn.
- Concrete, small examples with numbers (26 vs 1, 2.5 miles, 2 cents an acre).
- Comedy beats every 8 to 12 s: imagined line from a country or leader ("X, probably: ..."),
  a meme-like reaction, a cartoon reacting, and a light "sounds like a story for tourists" style aside.
- A twist near the end and a punchline last line. No follow/like/comment asks.
- Something changes on screen every 1 to 2 s. Small, quiet subtitles at the bottom (not big karaoke captions).
- Length: 40 to 80 s for this format (the user allows about 1 min).

## Reference 1: US Congress explainer (ref2, 114 s)
- Opens on a news date ("On November 3, Americans voted...") and a common confusion ("you heard these titles in movies").
- Satellite map flights, then flat "blueprint blue" infographic scenes with building cut-outs, people pictograms, big yellow counters.
- Org-chart that grows step by step; New York vs Wyoming comparison with population chips.
- Movie stills as cards (we must NOT use copyrighted stills).

## Reference 2: St Martin border legend (ref3/ref4, 81 s)
- Hook: two countries highlighted (blue/red fills with white outline, rectangular colored name tags), then "they share a land border... in the Caribbean".
- 3D globe/tilted satellite camera with slow drifts, rotation and push-ins; flight between continents.
- Parchment "legend" title card; vintage flat map for history; little cartoon characters (period clothes) as stickers.
- Comedy: flags shouting "mine mine mine" (seagull meme), knife/fight gag, wine vs gin walking race along a dotted path,
  laughing emoji faces for "a story they tell tourists", cartoon hands pointing at the border (arguing).
- Ending ties legend to the real treaty and a modern date (2023 agreement).

## Our tools (built in this repo)
- reels/pointroberts/comp/world3d.py: self-drawn 3D tilted map engine (procedural textures from Natural Earth outlines,
  pinhole camera with pitch/heading, haze + sky, local high-res texture blend, forward projection for overlays).
- reels/alaska/comp/mapart.py: flat procedural map (top-down).
- reels/alaska/comp/toons.py, reels/pointroberts/comp/toons2.py: cairo cartoons (Tsar, Seward, Queen Victoria, Polk,
  people, bubbles, coin, money bag, fridge, nugget, derrick, receipt, bus, car, gas pump, package, passport, palm).
- Music: FreePD comedy folder (Kevin MacLeod / Bryan Teoh "Public Domain" album tags only).

## Made so far in this style
- Alaska "giant fridge" (flat map, 40 s). Point Roberts (3D tilted, 61 s).

## To improve next
- Fly-in between continent and close-up looks blurry mid-way: add an intermediate texture level or cut with a whoosh.
- Use a vintage/parchment map scene for history segments (from ref 2) and a blueprint infographic scene (from ref 1).
- Rotate techniques: each new video takes its main look from a different reference.
