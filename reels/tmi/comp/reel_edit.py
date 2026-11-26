"""Three Mile Island reels (1080x1920), no channel branding. usage: VW=1080 VH=1920 python3 reel_edit.py PART OUT.mp4 | frames PREFIX t..."""
import sys, os, json, re
assert os.environ.get('VW') == '1080', 'run with VW=1080 VH=1920'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import *
import fx3, fx5
from fx5 import AMBER, GREEN, RED, WHITE, GREY, CREAM
N = int(sys.argv[1]); PD = f'{ROOT}/p{N}'
WORDS = json.load(open(f'{PD}/vo/vo.mp3.words.json'))
def S(word, near, tol=1.5):
    n = lambda x: re.sub(r'[^a-z0-9]', '', x.lower())
    for x in WORDS:
        if x['s'] >= near - tol and n(x['w']) == n(word): return x['s']
    raise SystemExit(f'word not found {word} {near}')
M = lambda n: f'media/{n}'
NRC = 'U.S. Nuclear Regulatory Commission'
TOWERS, UNIT2 = M('Three_Mile_Island_Nuclear_Generating_Station.jpg'), M('Three_Mile_Island_Nuclear_Generating_Station_Unit_2.jpg')
PLANT79, HBG79, CORE, CLEAN = M('Three_Mile_Island_(color)-2.jpg'), M('Harrisburg_Int_Airport_with_Pennsylvania_ANG_aircraft_1979.jpg'), M('Graphic_TMI-2_Core_End-State_Configuration.png'), M('TMI_cleanup-2.jpg')
def V(t0, path, tag, ss=0.0, g='seventies', **k): return Shot(t0, ('vid', path), grade=g, src_tag=tag, ss=ss, **k)
def IMG(t0, path, tag, kb=((0.5, 0.5, 1.0), (0.5, 0.5, 1.12)), g='seventies', **k): return Shot(t0, ('img', path), grade=g, src_tag=tag, kb=kb, **k)
def X(**k): return k
def DARK(at, a=0.6): return O.dark(at, amount=a)
def LAB(text, at, col=CREAM, y=330, size=58): return O.label(text, W // 2, y, at, anchor='mm', color=col, size=size)
def BIGT(text, at, sub=None, col=AMBER): return O.punch(text, at, color=[col], size=150, y=760, f='bebas', sub=sub, shake=False)

if N == 1:
    END = 67.9; TITLE = 'THREE MILE ISLAND  ·  PART 1'
    TILES = [('FEEDWATER\nPUMPS TRIP', S('stop', 23.0), AMBER), ('TURBINE\nTRIP', S('turbine', 23.6) + 0.4, AMBER), ('REACTOR\nTRIP', S('reactor', 25.5) + 0.4, RED),
             ('PRESSURIZER\nLEVEL', None, AMBER), ('RELIEF\nVALVE', None, GREEN), ('STEAM GEN\nLEVEL LOW', S('turbine', 23.6) + 1.0, AMBER),
             ('COOLANT\nTEMP', None, AMBER), ('RADIATION\nMONITOR', None, RED), ('DRAIN TANK\nPRESSURE', None, AMBER)]
    T = [IMG(0.0, UNIT2, 'Photo: Wikimedia Commons (CC BY-SA 3.0)', kb=((0.5, 0.5, 1.3), (0.5, 0.5, 1.15)), ov=[DARK(0.0, 0.72),
             X(k='lamp', at=0.2, label='RELIEF VALVE', state='CLOSED', color=GREEN, y=820, truth=(S('lying', 6.4) + 0.1, 'IT WAS OPEN'))]),
         IMG(7.66, TOWERS, 'Photo: Wikimedia Commons (CC BY-SA 3.0)', trans='glitch', kb=((0.55, 0.5, 1.0), (0.5, 0.5, 1.2)),
             ov=[DARK(7.7, 0.3), LAB('THE MOST SERIOUS ACCIDENT IN\nU.S. NUCLEAR POWER HISTORY', 8.4, AMBER, size=52)]),
         IMG(13.60, HBG79, 'U.S. Air National Guard photo, 1979', trans='zoom', ov=[DARK(13.6, 0.45), BIGT('MARCH 28, 1979', 13.7, sub='4:00 A.M.')]),
         IMG(16.46, PLANT79, 'Three Mile Island, 1979 · public domain', kb=((0.5, 0.5, 1.0), (0.45, 0.5, 1.25)), ov=[LAB('THREE MILE ISLAND · PENNSYLVANIA', 16.7, CREAM, size=50)]),
         IMG(19.26, PLANT79, 'Three Mile Island, 1979 · public domain', trans='push', kb=((0.5, 0.5, 1.3), (0.5, 0.5, 1.4)), ov=[DARK(19.3, 0.75), LAB('IT STARTS SMALL', 19.4, AMBER, y=230, size=56),
             X(k='annun', at=19.3, tiles=TILES, xy=(60, 420), th=130)]),
         V(27.20, 'real/nrc_reactor_v.mp4', 'Animation: ' + NRC, ss=11.0, g='none', trans='zoom', ov=[LAB('PRESSURE RISES · VALVE OPENS', 27.6, AMBER, y=300, size=52),
             LAB('WHEN PRESSURE DROPS, IT SHOULD CLOSE', S('drops', 33.2) - 0.2, CREAM, y=1560, size=46)]),
         IMG(35.42, PLANT79, 'Three Mile Island, 1979 · public domain', trans='glitch', kb=((0.5, 0.5, 1.4), (0.5, 0.5, 1.5)), ov=[DARK(35.4, 0.8), X(k='valve', at=35.4, x=W // 2, y=900, open_at=35.0, stuck=S('stuck', 36.3) - 0.1, s=1.1)]),
         IMG(37.48, PLANT79, 'Three Mile Island, 1979 · public domain', trans='flash', kb=((0.5, 0.5, 1.5), (0.5, 0.5, 1.6)), ov=[DARK(37.5, 0.82), LAB('WHAT THE CONTROL ROOM SHOWED', 37.6, CREAM, y=300, size=50),
             X(k='lamp', at=37.5, label='RELIEF VALVE', state='CLOSED', color=GREEN, y=860)]),
         IMG(40.98, PLANT79, 'Three Mile Island, 1979 · public domain', trans='push', kb=((0.5, 0.5, 1.6), (0.5, 0.5, 1.7)), ov=[DARK(41.0, 0.8), X(k='valve', at=41.0, x=W // 2, y=1000, open_at=40.0, s=1.0), LAB('WHAT WAS REALLY HAPPENING', 41.1, RED, y=240, size=52), O.punch('NOBODY KNOWS.', S('nobody', 44.6), color=[WHITE], size=130, y=1550, f='bebas', shake=False)]),
         IMG(46.02, TOWERS, 'Photo: Wikimedia Commons (CC BY-SA 3.0)', trans='glitch', kb=((0.5, 0.5, 1.3), (0.5, 0.5, 1.4)), ov=[DARK(46.0, 0.82), LAB('THE WORST MOVE OF ALL', 46.2, RED, y=300, size=56),
             X(k='level', at=46.1, label='PRESSURIZER LEVEL', box=(W // 2 - 140, 520, 280, 560), keys=[(46.1, 0.55), (49.5, 0.92)], note=(S('too', 49.8), 'LOOKS TOO FULL', AMBER)),
             O.stamp('EMERGENCY WATER CUT BACK', S('cut', 51.3), x=W // 2, y=900, size=74)]),
         V(53.38, 'real/nrc_reactor_v.mp4', 'Animation: ' + NRC, ss=19.0, g='none', trans='push', ov=[LAB('THE WATER LEVEL FALLS', 53.6, AMBER, y=300, size=56)]),
         IMG(56.94, PLANT79, 'Three Mile Island, 1979 · public domain', trans='flash', kb=((0.5, 0.5, 1.6), (0.5, 0.5, 1.7)), ov=[DARK(57.0, 0.82), X(k='thermo', at=57.0, dur=1.7)]),
         IMG(58.92, CORE, 'Graphic: ' + NRC, mode='portrait', g='none', trans='zoom', kb=((0.5, 0.45, 1.0), (0.5, 0.5, 1.35)), ov=[LAB('PART OF THE CORE MELTED', 59.6, RED, y=300, size=60)]),
         IMG(62.30, CLEAN, 'TMI cleanup, 1979 · public domain', trans='glitch', kb=((0.5, 0.5, 1.0), (0.5, 0.45, 1.25)), ov=[DARK(62.3, 0.55), BIGT('PART 2', 62.4, sub='why the outside world panicked', col=AMBER),
             O.label('FOLLOW', W // 2, 1040, S('Follow', 65.7), anchor='mm', color=WHITE, size=80)])]

NRCP = 'Photo: U.S. Nuclear Regulatory Commission'
def NP(n): return M(f'nrc_{n}.png')
if N == 2:
    END = 70.9; TITLE = 'THREE MILE ISLAND  ·  PART 2'
    T = [IMG(0.0, NP('controlroom_crowd'), NRCP, kb=((0.5, 0.5, 1.35), (0.45, 0.5, 1.15)), ov=[DARK(0.0, 0.62), X(k='timer', at=0.3, to=8400, dur=5.2, y=760, label='VALVE STUCK OPEN')]),
         IMG(6.28, NP('controlroom_mockup'), 'Photo: U.S. NRC (control room mockup)', trans='glitch', kb=((0.5, 0.5, 1.0), (0.4, 0.5, 1.2)), ov=[DARK(6.3, 0.35), LAB('NEVER TRAINED FOR THIS', 6.9, RED, y=330, size=60)]),
         IMG(9.76, NP('plant_aerial'), NRCP, trans='zoom', kb=((0.5, 0.5, 1.0), (0.5, 0.5, 1.2)), ov=[DARK(9.8, 0.4), BIGT('PART 2', 9.9, sub='blind in the control room')]),
         IMG(12.60, NP('pipes_valve'), NRCP, trans='push', kb=((0.5, 0.45, 1.0), (0.5, 0.4, 1.25)), ov=[LAB('THE STUCK VALVE', 12.8, AMBER, y=330, size=58)]),
         IMG(14.56, NP('controlroom_bw'), NRCP, trans='glitch', kb=((0.5, 0.5, 1.4), (0.5, 0.5, 1.5)), ov=[DARK(14.6, 0.82), X(k='valve', at=14.6, x=W // 2, y=1000, open_at=14.0, s=1.0),
             O.counter(S('two', 16.8), 0, 220, 1.4, label='GALLONS OF WATER A MINUTE', x=W // 2, y=360, size=170, color=AMBER)]),
         IMG(20.62, NP('controlroom_bw'), NRCP, trans='push', kb=((0.75, 0.5, 1.0), (0.7, 0.5, 1.2)), ov=[DARK(20.6, 0.4), LAB('ANOTHER HIDDEN PROBLEM', 20.8, AMBER, y=330, size=56)]),
         IMG(23.22, NP('controlroom_crowd'), NRCP, trans='glitch', kb=((0.5, 0.5, 1.5), (0.5, 0.5, 1.6)), ov=[DARK(23.2, 0.82), X(k='lamp', at=23.3, label='EMERGENCY FEEDWATER VALVES', state='CLOSED', color=RED, y=820),
             LAB('SHOULD HAVE BEEN OPEN', S('open', 26.7) - 0.1, AMBER, y=330, size=54), X(k='mtag', at=S('tag', 31.6) - 0.6, x=W // 2, y=820)]),
         IMG(32.80, NP('controlroom_crowd'), NRCP, trans='push', kb=((0.3, 0.5, 1.2), (0.35, 0.5, 1.35)), ov=[DARK(32.8, 0.45), LAB('SOMETHING ELSE', 33.0, AMBER, y=330, size=58)]),
         IMG(34.36, NP('controlroom_bw'), NRCP, trans='glitch', kb=((0.5, 0.5, 1.6), (0.5, 0.5, 1.7)), ov=[DARK(34.4, 0.85), X(k='nogauge', at=34.4)]),
         IMG(39.74, NP('controlroom_bw'), NRCP, trans='push', kb=((0.3, 0.5, 1.6), (0.3, 0.5, 1.7)), ov=[DARK(39.8, 0.85),
             X(k='level', at=39.8, label='PRESSURIZER LEVEL', box=(W // 2 - 140, 520, 280, 560), keys=[(39.8, 0.5), (43.6, 0.95)], note=(S('full', 45.6) - 0.2, '"IT\'S FULL"', AMBER))]),
         V(46.78, 'real/nrc_reactor_v.mp4', 'Animation: U.S. NRC', ss=21.0, g='none', trans='flash', ov=[O.punch("IT WASN'T.", 46.9, color=[RED], size=150, y=330, f='bebas', shake=True)]),
         IMG(47.96, NP('reactor_top_cleanup'), NRCP, trans='glitch', kb=((0.5, 0.5, 1.1), (0.52, 0.48, 1.25)), ov=[DARK(48.0, 0.45), LAB('COOLANT PUMPS START SHAKING', 48.3, AMBER, y=330, size=54)]),
         IMG(50.62, NP('controlroom_crowd'), NRCP, trans='push', kb=((0.5, 0.5, 1.4), (0.5, 0.5, 1.5)), ov=[DARK(50.6, 0.82),
             X(k='annun', at=50.6, tiles=[('COOLANT PUMP\nA OFF', 50.9, RED), ('COOLANT PUMP\nB OFF', 51.3, RED), ('COOLANT PUMP\nC OFF', 51.7, RED), ('COOLANT PUMP\nD OFF', 52.1, RED)], cols=2, xy=(120, 520), th=150)]),
         V(52.38, 'real/nrc_reactor_v.mp4', 'Animation: U.S. NRC', ss=25.0, g='none', trans='push', ov=[LAB('LESS AND LESS COOLING', 52.6, RED, y=300, size=56)]),
         IMG(54.76, NP('officials_table'), NRCP, trans='glitch', kb=((0.5, 0.5, 1.0), (0.5, 0.5, 1.15)), ov=[DARK(54.8, 0.4), O.stamp('NOT IN TRAINING', S('training', 56.0), x=W // 2, y=560, size=84),
             O.stamp('NOT IN PROCEDURES', S('procedures', 58.6), x=W // 2, y=900, size=84)]),
         IMG(59.98, NP('core_endstate'), 'Graphic: U.S. NRC', mode='portrait', g='none', trans='zoom', kb=((0.5, 0.45, 1.0), (0.5, 0.5, 1.3)), ov=[LAB('THE DAMAGE WAS DONE', 60.3, RED, y=300, size=60)]),
         IMG(63.28, NP('core_camera_1984'), 'Image: U.S. NRC (camera inside TMI-2 reactor)', trans='glitch', kb=((0.5, 0.5, 1.0), (0.5, 0.5, 1.2)), ov=[DARK(63.3, 0.45),
             BIGT('PART 3', 63.4, sub='how much really melted?', col=AMBER), O.label('FOLLOW', W // 2, 1040, S('Follow', 68.5), anchor='mm', color=WHITE, size=80)])]

if N == 3:
    END = 68.2; TITLE = 'THREE MILE ISLAND  ·  PART 3'
    CORE_ = NP('core_endstate')
    T = [IMG(0.0, NP('phones'), NRCP, kb=((0.5, 0.5, 1.3), (0.5, 0.5, 1.15)), ov=[DARK(0.0, 0.7), X(k='meter', at=0.2, y=820)]),
         IMG(6.26, CORE_, 'Graphic: U.S. NRC', mode='portrait', g='none', trans='glitch', kb=((0.5, 0.6, 1.5), (0.5, 0.6, 1.75)), ov=[LAB('MELTED FUEL', 6.6, RED, y=300, size=70)]),
         IMG(9.36, NP('meeting_room'), NRCP, trans='push', kb=((0.5, 0.5, 1.0), (0.5, 0.5, 1.15)), ov=[DARK(9.4, 0.55), O.punch('NOBODY REALIZED.', 9.5, color=[WHITE], size=120, y=760, f='bebas', shake=False)]),
         IMG(11.08, NP('plant_color'), NRCP, trans='zoom', kb=((0.5, 0.5, 1.0), (0.5, 0.5, 1.2)), ov=[DARK(11.1, 0.4), BIGT('PART 3', 11.2, sub='the hidden meltdown')]),
         IMG(13.88, NP('nrc_team_trailer'), NRCP, trans='push', kb=((0.5, 0.5, 1.0), (0.45, 0.5, 1.2)), ov=[LAB('"DAMAGED." BUT HOW BADLY?', 14.2, AMBER, y=330, size=56)]),
         IMG(16.64, NP('site_aerial_bw'), NRCP, kb=((0.5, 0.5, 1.0), (0.5, 0.5, 1.2)), ov=[DARK(16.7, 0.4), LAB('NO WAY TO SEE INSIDE', 16.9, RED, y=330, size=60)]),
         IMG(19.24, NP('worker_suit'), NRCP, trans='glitch', kb=((0.5, 0.5, 1.0), (0.55, 0.5, 1.2)), ov=[LAB('TOO CONTAMINATED TO ENTER', 19.5, AMBER, y=330, size=54)]),
         IMG(23.46, NP('basement_water'), NRCP, trans='push', kb=((0.5, 0.5, 1.0), (0.5, 0.55, 1.2)), ov=[DARK(23.5, 0.45), BIGT('JULY 1980', S('July', 27.3) - 0.2, sub='the first two engineers go in')]),
         IMG(29.26, NP('core_camera_1984'), 'Image: U.S. NRC (camera inside TMI-2 reactor)', trans='glitch', kb=((0.5, 0.5, 1.0), (0.5, 0.5, 1.25)), ov=[X(k='camhud', at=29.3)]),
         IMG(31.98, NP('debris_camera'), 'Image: U.S. NRC (camera inside TMI-2 reactor)', trans='flash', kb=((0.5, 0.5, 1.0), (0.5, 0.45, 1.3)), ov=[X(k='camhud', at=32.0)]),
         IMG(33.98, CORE_, 'Graphic: U.S. NRC', mode='portrait', g='none', trans='zoom', kb=((0.5, 0.46, 1.9), (0.5, 0.46, 2.1)), ov=[LAB('EMPTY SPACE', 34.3, RED, y=300, size=70)]),
         IMG(37.32, CORE_, 'Graphic: U.S. NRC', mode='portrait', g='none', kb=((0.5, 0.52, 1.9), (0.5, 0.54, 2.1)), ov=[LAB('A BED OF RUBBLE', 37.6, AMBER, y=300, size=66)]),
         V(40.82, 'real/nrc_reactor_v.mp4', 'Animation: U.S. NRC', ss=27.0, g='none', trans='glitch', ov=[LAB('IT GOT WORSE', 41.0, RED, y=300, size=64)]),
         IMG(42.34, CORE_, 'Graphic: U.S. NRC', mode='portrait', g='none', trans='push', kb=((0.5, 0.66, 1.5), (0.5, 0.72, 1.8)),
             ov=[DARK(42.4, 0.4), O.counter(S('nineteen', 44.6) - 0.1, 0, 19, 1.2, label='METRIC TONS OF MELTED DEBRIS', x=W // 2, y=300, size=200, color=RED)]),
         IMG(51.02, NP('defueling_camera'), 'Image: U.S. NRC (camera inside TMI-2 reactor)', trans='flash', kb=((0.5, 0.5, 1.0), (0.5, 0.5, 1.2)), ov=[DARK(51.0, 0.3), O.punch('A REAL MELTDOWN', 51.1, color=[RED], size=120, y=760, f='bebas')]),
         IMG(53.82, NP('reactor_top_cleanup'), NRCP, trans='push', kb=((0.5, 0.5, 1.0), (0.5, 0.5, 1.2)), ov=[DARK(53.9, 0.45), BIGT('1985', S('1985', 55.4) - 0.2, sub='the lid finally comes off')]),
         IMG(58.4, NP('defueling_camera'), 'Image: U.S. NRC (camera inside TMI-2 reactor)', trans='glitch', kb=((0.5, 0.5, 1.2), (0.5, 0.5, 1.4)), ov=[X(k='camhud', at=58.4, label='DEFUELING CAMERA')]),
         IMG(61.92, NP('map_5_10_miles'), 'Map: U.S. NRC', trans='glitch', kb=((0.5, 0.5, 1.0), (0.5, 0.5, 1.2)), ov=[DARK(62.0, 0.5), BIGT('PART 4', 62.1, sub='families told to leave', col=AMBER),
             O.label('FOLLOW', W // 2, 1040, S('Follow', 66.0), anchor='mm', color=WHITE, size=80)])]

if N == 4:
    END = 74.7; TITLE = 'THREE MILE ISLAND  ·  PART 4'
    MAP = NP('map_5_10_miles'); MKB = ((0.5, 0.55, 1.0), (0.5, 0.55, 1.12)); MC = (W // 2, int(H * 0.5))
    T = [IMG(0.0, MAP, 'Map: U.S. NRC', kb=MKB, ov=[DARK(0.0, 0.35), X(k='rings', at=0.3, c=MC, r=330, label='5 MILES'),
             X(k='eas', at=0.6, y=250, head='GOVERNOR\'S ADVISORY', text='PREGNANT WOMEN & PRESCHOOL CHILDREN\nWITHIN 5 MILES: LEAVE THE AREA')]),
         IMG(8.24, NP('plant_aerial'), NRCP, trans='zoom', kb=((0.5, 0.5, 1.0), (0.5, 0.5, 1.2)), ov=[DARK(8.3, 0.4), BIGT('PART 4', 8.4, sub='friday morning')]),
         IMG(10.88, NP('site_from_air'), NRCP, trans='push', kb=((0.5, 0.45, 1.0), (0.5, 0.5, 1.15)), ov=[DARK(10.9, 0.4), BIGT('MARCH 30, 1979', 11.0, sub='two days into the accident')]),
         IMG(15.80, NP('press_crowd'), NRCP, trans='glitch', kb=((0.5, 0.5, 1.0), (0.5, 0.45, 1.2)), ov=[LAB('WHAT DO WE BELIEVE?', 16.2, AMBER, y=330, size=60)]),
         IMG(19.72, NP('denton_press'), NRCP, trans='push', kb=((0.5, 0.45, 1.0), (0.45, 0.45, 1.15)), ov=[LAB('THE COMPANY SAYS ONE THING...', 19.9, CREAM, y=330, size=50)]),
         IMG(21.58, NP('officials_table'), NRCP, trans='push', kb=((0.5, 0.5, 1.0), (0.5, 0.5, 1.15)), ov=[LAB('...OFFICIALS SAY ANOTHER', 21.7, CREAM, y=330, size=50)]),
         IMG(22.98, NP('plant_color'), NRCP, trans='glitch', kb=((0.5, 0.45, 1.1), (0.5, 0.4, 1.3)), ov=[DARK(23.0, 0.35), LAB('ANOTHER RELEASE OF\nRADIOACTIVE GAS', 23.4, RED, y=330, size=56)]),
         IMG(28.22, NP('site_aerial_bw'), NRCP, trans='push', kb=((0.5, 0.5, 1.1), (0.5, 0.5, 1.25)), ov=[DARK(28.3, 0.5), LAB('GOV. DICK THORNBURGH DECIDES', 28.5, AMBER, y=330, size=52)]),
         IMG(31.14, MAP, 'Map: U.S. NRC', trans='zoom', kb=MKB, ov=[DARK(31.2, 0.35), X(k='rings', at=31.2, c=MC, r=330, label='5 MILES'),
             X(k='eas', at=31.4, y=250, head='GOVERNOR\'S ADVISORY', text='EVERYONE WITHIN 5 MILES:\nSTAY INDOORS')]),
         IMG(34.78, MAP, 'Map: U.S. NRC', kb=((0.5, 0.55, 1.12), (0.5, 0.55, 1.22)), ov=[DARK(34.8, 0.35), X(k='rings', at=34.8, c=MC, r=360, label='5 MILES'),
             X(k='eas', at=35.0, y=250, head='GOVERNOR\'S ADVISORY', text='PREGNANT WOMEN & PRESCHOOL CHILDREN:\nLEAVE THE AREA')]),
         IMG(40.48, NP('site_aerial_bw'), NRCP, trans='glitch', kb=((0.5, 0.5, 1.25), (0.5, 0.5, 1.4)), ov=[DARK(40.5, 0.45), O.punch("THAT'S ALL IT TAKES.", 40.6, color=[WHITE], size=110, y=760, f='bebas', shake=False)]),
         IMG(41.76, MAP, 'Map: U.S. NRC', trans='push', kb=((0.5, 0.55, 1.0), (0.5, 0.55, 0.9 + 0.2)), ov=[DARK(41.8, 0.4), X(k='exodus', at=41.8, c=MC), X(k='rings', at=41.8, c=MC, r=330, label='5 MILES')]),
         IMG(45.12, MAP, 'Map: U.S. NRC', kb=((0.5, 0.55, 1.1), (0.5, 0.55, 1.0)), ov=[DARK(45.2, 0.45), X(k='exodus', at=45.2, c=MC), LAB('THOUSANDS LEAVE HOME', 45.4, AMBER, y=330, size=60)]),
         IMG(49.56, NP('plant_color'), NRCP, trans='flash', kb=((0.5, 0.5, 1.2), (0.5, 0.5, 1.3)), ov=[DARK(49.6, 0.5), O.punch('THE TWIST', 49.7, color=[AMBER], size=150, y=760, f='bebas')]),
         IMG(51.14, NP('plant_aerial'), NRCP, trans='push', kb=((0.5, 0.5, 1.3), (0.5, 0.5, 1.4)), ov=[DARK(51.2, 0.82), X(k='dose', at=S('one', 57.2) - 0.3, at2=S('six', 60.6) - 0.3)]),
         IMG(61.58, NP('press_crowd'), NRCP, trans='glitch', kb=((0.5, 0.5, 1.15), (0.5, 0.5, 1.3)), ov=[DARK(61.6, 0.45), LAB('THE FEAR WAS BIGGER\nTHAN THE DANGER', 61.8, AMBER, y=330, size=56)]),
         V(65.12, 'real/nrc_reactor_v.mp4', 'Animation: U.S. NRC', ss=28.0, g='none', trans='push', ov=[LAB('BUT INSIDE THE REACTOR...', 65.3, RED, y=300, size=56)]),
         IMG(68.68, NP('core_endstate'), 'Graphic: U.S. NRC', mode='portrait', g='none', trans='glitch', kb=((0.5, 0.58, 1.3), (0.5, 0.58, 1.45)), ov=[DARK(68.7, 0.55),
             BIGT('PART 5', 68.8, sub='the bubble', col=AMBER), O.label('FOLLOW', W // 2, 1040, S('Follow', 72.2), anchor='mm', color=WHITE, size=80)])]

def captions(img, t, fi, sh):
    """New caption style: big cream Oswald words, current word boxed in amber; radiation badge + part title; amber progress bar."""
    cur = None
    for i in range(0, len(WORDS), 3):
        g = WORDS[i:i + 3]
        if g[0]['s'] - 0.05 <= t <= g[-1]['e'] + 0.25: cur = g
    d = ImageDraw.Draw(img)
    if cur:
        f = font('oswald', 88); sp = 24; words = [x['w'].upper() for x in cur]; widths = [f.getlength(w) for w in words]
        tot = sum(widths) + sp * (len(words) - 1)
        while tot > W - 100: f = font('oswald', f.size - 6); widths = [f.getlength(w) for w in words]; tot = sum(widths) + sp * (len(words) - 1)
        x = (W - tot) / 2; y = int(H * 0.66)
        for w, wd, x0 in zip(words, widths, [x + sum(widths[:j]) + sp * j for j in range(len(words))]):
            on = any(c['w'].upper() == w and c['s'] <= t for c in cur) and t <= max(c['e'] for c in cur if c['w'].upper() == w) + 0.15
            if on: d.rectangle([x0 - 10, y + 6, x0 + wd + 10, y + f.size * 1.18], fill=AMBER)
            d.text((x0, y), w, font=f, fill=(20, 16, 10) if on else CREAM, stroke_width=0 if on else 6, stroke_fill=(0, 0, 0))
    # badge: radiation trefoil + part title
    fb = font('oswald', 36); tw = fb.getlength(TITLE); bx = (W - tw) / 2 + 30
    d.rectangle([bx - 90, 110, bx + tw + 24, 178], fill=(16, 14, 10))
    d.ellipse([bx - 78, 116, bx - 22, 172], fill=AMBER); fx5.trefoil(d, bx - 50, 144, 24, (16, 14, 10)); d.ellipse([bx - 57, 137, bx - 43, 151], fill=AMBER); d.ellipse([bx - 54, 140, bx - 46, 148], fill=(16, 14, 10))
    d.text((bx, 144), TITLE, font=fb, fill=AMBER, anchor='lm')
    d.rectangle([0, H - 14, int(W * t / END), H], fill=AMBER)
    return img

if __name__ == '__main__':
    if sys.argv[2] == 'frames':
        for tt in map(float, sys.argv[4:]): render(T, END, f'{sys.argv[3]}_{tt:05.1f}.mp4', tt, tt + 1 / 30, post=captions)
    else:
        render(T, END, sys.argv[2], float(os.environ.get('T0', 0)), float(os.environ.get('T1', END)), log=True, post=captions)
