# Style library: map-explainer reels (learned from reference videos)

## USER VERDICT (most important, Nov 2026)
- LIKED: Point Roberts reel (reels/pointroberts): 3D tilted procedural map, cars/bus moving on routes, relaxed pace, Kokoro am_michael voice.
- DISLIKED: Manhattan-for-nutmeg (engine v2): too fast, parchment vector map not liked, Chatterbox voice sounded "AI". Do NOT use that style/voice.
- DISLIKED: Paul Revere reel (too many names/places, story hard to follow, cluttered labels). Lesson: ONE simple geographic
  surprise per video, max 2-3 places, 1-2 characters, every sentence shown clearly on the map. History is OK only as a short "why".
- Default from now on: Point Roberts engine (world3d.py) + Kokoro am_michael, pace only slightly faster than Point Roberts,
  natural pauses, moving vehicles/props on the map, clean (not blurry) zooms.

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

## Reference 3: Louisiana Purchase (ref5, 101 s)
- Hook = paradox: "sent diplomats to buy one city... ended up buying the whole territory for almost the same price". Then "But let's start from the beginning."
- Vintage parchment world map (beige land, teal-grey sea), flat bold territory fills (red/blue/teal/orange) with thick black outlines, big serif names ON the territory. Vector = always crisp.
- Very fast camera: a move every 1 to 2 s, quick zoom/pan with ease, holds are short; flights between continents.
- 3D toy-figurine characters (pawn bodies, big heads, soft light + contact shadows); some AI-rendered realistic scenes (beach soldiers).
- Props: money stacks, FOR SALE -> SOLD sign, coin "4c/acre", lightning along a river border, thought bubble, portrait cut-out.
- Natural human-like voice (ElevenLabs-like).

## Engine v2 (reels/nutmeg/comp)
- vmap.py: crisp vector parchment map at full resolution (Natural Earth 10m land, LOD cache, Web-Mercator camera with rotation + perspective tilt + haze, coastal ripple lines, territory fills with black outlines).
- props3d.py: pseudo-3D figurines (Dutch merchant, Stuyvesant peg leg, King Charles II, redcoat) + nutmeg, ship, scroll, latte.
- edit.py: SHOTS list anchored to narration words, 0.6 s snappy moves, long jumps "fly" (zoom dips out and back in), motion blur by camera speed.
- cb_vo.py: Chatterbox TTS (CPU, natural voice), ~4x slower than real time.

## Reference 4: Joan of Arc / Hundred Years' War (ref6, 89 s)  <- user says: copy THIS editing/graphics/sfx feel
Script formula (write every new script like this):
1. HOOK (0-10 s): "Just imagine [extreme situation lasting/at scale]... and no one could stop it, until [mystery person] appeared."
   + an open loop about the ending: "But her own story didn't end very well." (viewer must stay to learn the ending)
2. Big date card ("1337") -> a ruler's inner thought said out loud in first person ("why not just become King of France too?")
   -> a one-word deadpan reply from the other side ("Um, no.") -> "And that's how X began."
3. Short punchy beats of 2-4 s. Mix narration with VOICED character lines (different voice, acted: shouted, sarcastic).
4. Modern/gamer slang and anachronisms for comedy: strategy-game UI overlay with chat ("bro your mom plays better",
   "truce maybe?" "lol no", "GG for France"), "looks like GG for X".
5. Rise of the hero with a stat card (name banner + icons), gear-up (armor, horse, banner), victories marked on the map with
   serif campaign labels + years and curved arrows, a glowing pulse where the hero appears.
6. Villain line voiced ("We need to do something about this bloody girl!"), then trial/ending with a 4th-wall joke
   ("...and not liking this video").
Visuals: satellite map with bold red/blue fills, counters that tick ("104 years" -> "116 years"), small figurines on the map,
props (burning stake, lanterns etc.), hands/arrows animations, scene cuts to illustrated backgrounds.
Sound: whoosh on every move, sword clashes, hooves, crowd, shouts, comic stings on jokes, voiced character lines.

## How to reuse (rotate per video)
- Always: strong "Just imagine..." or paradox hook + open loop; voiced character lines in other Kokoro voices
  (British characters: bm_george / bm_lewis; American: am_adam; narrator am_michael); one game-UI chat gag;
  counters; moving riders/vehicles along routes on the Point-Roberts-style map; whoosh on moves; comic stings.

## USER RULES (Nov 28, 2026) - apply to every map video
- Map must look 3D: countries RAISED/extruded above the base map (side walls + shadow), popping up when named.
- Every country that is named gets its NATIONAL FLAG textured on its map shape (USA -> US flag on the US shape, South Korea -> Korean flag, etc.).
- Uniforms, vehicles and characters must match the country and era of the script.
- Prefer 3D-looking art over flat 2D. No blur anywhere. Text must never overlap other text/objects.
- Timeline/pacing clean and professional; length 40-65 s; story kept simple.
- Workflow: first send STILL FRAMES (photos) of the planned look for approval, only then render the video.
- Arrows: always contrast with the territory under them (never red on red). Use team colours that differ from fills
  (aggressor = yellow/orange, UN/allies = cyan/blue) + white outline + dark shadow.
- Battles in the script must show armies: tanks, soldiers in correct national uniforms, ships, explosions, shaded/3D look.
