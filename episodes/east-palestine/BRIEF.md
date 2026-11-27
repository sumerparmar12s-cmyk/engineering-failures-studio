# Episode brief — East Palestine, Ohio train derailment (Feb 3, 2023)

Channel: **Wrecklore** (faceless, English, US audience, high-RPM countries). Target length ≈ 6–8 min (8+ min allows mid-roll ads).

## The creator's requirements (must follow)
1. **Hook like Dhruv Rathee** (adapted for a US audience, no face): open on a shocking, contradictory claim; pose the central question in the first 20 s; promise ("In this video we'll find out…"); hold the biggest reveal for later.
   - Core twist: officials said the "vent and burn" of 5 vinyl-chloride tank cars was necessary to prevent an explosion; the NTSB later found it was unnecessary and that the experts who knew (Oxy Vinyls) were not heard by decision makers. **Verify every fact against the NTSB final report (RRD23MR005) before scripting.**
2. **Storytelling style:** pattern interrupts every 40–60 s ("But wait…", "Now here's where it gets interesting…"), second-person ("Imagine you live two blocks from the tracks…"), simple analogies, Myth vs Fact segment, on-screen **fact-check cards with source** (NTSB/EPA document pages, highlighted).
3. **Pro editing (Dhruv Rathee level):** fast, purposeful cuts; pauses where the narration STOPS and a real sound/footage plays alone (e.g. evacuation sirens, fire roar, then silence), then narration resumes; screen blackouts / flash cuts for reveals; zooms on documents; lower-third source tags.
4. **Visuals:** real public-domain footage and photos first (NTSB photos/videos, EPA, U.S. government sources; check the PUBLIC DOMAIN mark on DVIDS/agency pages); 3D animation (train, hot bearing, derailment, tank cars, vent-and-burn plume) with **frame-by-frame glitch check** (see production notes); clean colorful graphics. No AI-generated video (no generator available). No news-channel footage, no copyrighted images.
5. **Sound:** suspense music in suspense sections, emotional at the end; sound effects present but **never over the voice** — target voice ≥ +10 dB above music+SFX (measure). Where a sound must be heard (siren, fire, train horn), stop the narration for that moment.
6. **Thumbnail:** realistic (real photo base, e.g. the vent-and-burn smoke column), reference-style typography (brown serif top word with dashes + big red serif word + ribbon) or bold disaster style; clear subject; one real evidence inset.
7. **Description:** hook paragraph ending in a question → "From … to … this is the full story of …" → catchy chapter titles → short image/music credits → CTA question. **No mention of AI voice.** Remind the creator to tick "Altered or synthetic content: Yes" in Studio if a realistic 3D reconstruction is used.
8. Deliver: 720p + 1080p MP4, thumbnail, title, description, tags, hashtags.

## Production notes from the UPS 2976 episode (reuse)
- Pipeline: `episodes/ups-2976/` — `script.md`, `fix_words.py` (align captions to script), `three3d/` + `render3d.js` (three.js via SwiftShader, deterministic `renderAt(t)`), `shots.py`, `prep_moves.py`, skill `render.py` / `assemble.py`, then `alimiter` on the final audio.
- 3D glitch fixes: `logarithmicDepthBuffer: true`; layered ground surfaces must be ≥0.35 m apart; near plane 0.5 for large scenes; verify every clip with the frame-difference spike check (no spikes > 3× neighbours).
- Mix: SCALE map in shots.py (loud SFX ×0.3–0.45, others ×0.5, music ×0.6); measure voice-to-background with the aligned least-squares method; aim ≥ +10 dB.
- Voice: Kokoro `am_michael`, speed 1.05; pronunciation map in the TTS script; plain "FAA"/"NTSB" read fine.
- Music: FreePD CC0 mirror on archive.org (`freepd`); avoid tracks whose tags show an ISRC; avoid titles that suggest covers of film scores.
