#!/usr/bin/env python3
"""Beat 2 'The Fall' (58s) — cinematic preset, motion-in-still. python3 build_beat2.py > beat2_fall.json"""
import json
D=58.0
def cam(t0,t1,s,cx,cy,ease="smooth",**k):
    c={"t0":t0,"t1":t1,"ease":ease,"scale":s,"cx":cx,"cy":cy}; c.update(k); return c
glow=lambda pos,r,col,st,fl=0,p=0,hz=0:{"type":"glow","pos":pos,"r":r,"color":col,"strength":st,"pulse":p,"pulse_hz":hz,"flicker":fl}
scenes=[
 {"id":"A","image":"stills/B2_S01A.png","start":0,"camera":cam(0,7.65,[1.0,1.22],[1280,1000],[720,780],"pow:1.4",shake={"t0":6.4,"t1":7.4,"amp":9,"hz":9}),
  "fx":[glow([2240,480],520,[170,200,255],.6,1.3),glow([360,600],480,[170,200,255],.5,1.1)]},
 {"id":"B","image":"stills/B2_S01B.png","start":7.65,"camera":cam(7.65,11.2,[1.0,1.18],[1280,1450],[720,760],"smooth",shake={"t0":7.65,"t1":10.7,"amp":5,"hz":7}),
  "fx":[{"type":"sway","box":[1300,120,2560,720],"amp":10,"freq":1.6},glow([1300,300],500,[170,200,255],.45,1.2)]},
 {"id":"C","image":"stills/B2_S02A.png","start":11.2,"camera":cam(11.2,16.4,[1.0,1.5],[1280,1280],[720,720],"smooth"),
  "fx":[{"type":"sway","box":[0,0,2560,1440],"amp":5,"freq":0.35}]},
 {"id":"D","image":"stills/B2_S02B.png","start":16.4,"camera":cam(16.4,23.67,[1.05,1.3],[1500,1280],[900,760],"smooth"),
  "fx":[{"type":"sway","box":[0,0,2560,1100],"amp":7,"freq":0.3},glow([1100,200],600,[255,235,190],.3,0,.2,.12)]},
 {"id":"E","image":"stills/B2_S03A.png","start":23.67,"camera":cam(23.67,32.4,[1.0,2.6],[1280,1260],[720,830],"pow:2.0"),
  "fx":[glow([1280,300],900,[255,240,215],.22,0,.2,.1)]},
 {"id":"F","image":"stills/B2_S03B.png","start":32.4,"camera":cam(32.4,37.06,[1.0,1.22],[1280,1500],[720,780],"smooth"),
  "fx":[{"type":"parallax","amp":22,"period":6,"depth":"auto_ground"}]},
 {"id":"G","image":"stills/B2_S04A.png","start":37.06,"camera":cam(37.06,45.2,[1.0,1.45],[1280,1050],[720,840],"pow:1.6",shake={"t0":42.2,"t1":45.0,"amp":6,"hz":8}),
  "fx":[{"type":"sway","box":[0,0,2560,1440],"amp":6,"freq":0.7},glow([900,380],700,[255,245,200],.3,0,.3,.2)]},
 {"id":"H","image":"stills/B2_S04B.png","start":45.2,"camera":cam(45.2,50.1,[1.0,1.2],[1500,1280],[720,760],"smooth"),
  "fx":[{"type":"sway","box":[0,0,2560,1440],"amp":8,"freq":0.8}]},
 {"id":"I","image":"stills/B2_S05A.png","start":50.1,"camera":cam(50.1,58.0,[1.0,1.3],[1400,1500],[720,800],"smooth"),
  "fx":[glow([1500,160],800,[255,240,190],.3,0,.3,.12),{"type":"sway","box":[0,0,2560,800],"amp":4,"freq":0.25}]},
]
S=lambda **k:k
els=[
 {"type":"rain","t_in":0,"t_out":11.0,"fade_out":1.6,"density":330,"alpha":.5,"angle":18,"speed":1700,"length":85},
 {"type":"mist","t_in":11.4,"t_out":23.5,"fade_in":1.0,"fade_out":1.2,"opacity":.22,"speed":10},
 {"type":"particles","kind":"dust","t_in":23.7,"t_out":32.4,"n":40,"alpha":.35},
 {"type":"particles","kind":"dust","t_in":37.2,"t_out":45.2,"n":60,"alpha":.5},
 {"type":"particles","kind":"dust","t_in":45.3,"t_out":50.0,"n":60,"alpha":.5},
 {"type":"mist","t_in":50.3,"t_out":58,"opacity":.18,"speed":8},
 # words
 {"type":"strike_cards","t_in":.68,"t_out":2.7,"size":54,"cards":[{"text":"IN ONE PIECE","y":300,"t_in":.68,"t_strike":1.55}]},
 {"type":"label","t_in":2.98,"t_out":4.8,"text":"SOMEWHERE IN THE STORM","pos":[640,150],"size":32,"color":"cream","font":"mono"},
 {"type":"flash","t_in":3.9,"dur":.25,"alpha":.35},
 {"type":"label","t_in":11.7,"t_out":13.5,"text":"BELOW HER","pos":[640,150],"size":38,"color":"cream","font":"mono"},
 {"type":"label","t_in":14.6,"t_out":16.3,"text":"GREAT GREEN CIRCLES","pos":[640,150],"size":34,"color":"yellow","underline":[420,860,182]},
 {"type":"label","t_in":41.1,"t_out":43.4,"text":"THE THICK CANOPY","pos":[640,150],"size":34,"color":"cream","font":"mono"},
 {"type":"dim","t_in":55.8,"t_out":56.3,"alpha":[0,.5]},
 {"type":"flash","t_in":6.48,"dur":.3,"alpha":.6},
 {"type":"highlight_box","t_in":5.3,"t_out":7.6,"scene":"A","src_box":[380,860,840,1110],"label":"HER ROW OF SEATS"},
 {"type":"badge_pop","t_in":10.38,"t_out":11.5,"text":"FALLING","pos":[640,300],"size":96,"anchor":"mm"},
 {"type":"label","t_in":16.82,"t_out":19.3,"text":"IN HER OWN WORDS","pos":[640,150],"size":30,"color":"yellow","underline":[470,810,182]},
 {"type":"lower_third","t_in":19.5,"t_out":21.9,"title":"JULIANE KOEPCKE","sub":"AGE 17","y":110},
 {"type":"label","t_in":21.1,"t_out":23.4,"text":"IMPOSSIBLE CALM","pos":[640,150],"size":34,"color":"cream","font":"mono"},
 {"type":"dim","t_in":23.8,"t_out":24.1,"alpha":[0,.35],"t_end":25.3,"fade_out":.6},
 {"type":"strike_cards","t_in":25.6,"t_out":27.4,"size":50,"cards":[{"text":"SHE WILL SURVIVE","y":300,"t_in":25.6,"t_strike":26.5}]},
 {"type":"label","t_in":27.66,"t_out":30.9,"text":"NOBODY CAN EXPLAIN IT","pos":[640,150],"size":34,"color":"red","underline":[430,850,182]},
 {"type":"ticker","t_in":31.0,"t_out":33.2,"run":[31.06,32.1],"from":0,"to":3000,"suffix":" M","pos":[640,260],"size":120,"label":"THE FALL","power":1.5},
 {"type":"label","t_in":34.0,"t_out":36.4,"text":"SPUN LIKE A MAPLE SEED","pos":[640,150],"size":32,"color":"cream","font":"mono"},
 {"type":"badge_pop","t_in":38.2,"t_out":40.6,"text":"UPDRAFT","pos":[1180,210],"size":84,"anchor":"rm","sub":"FROM THE STORM","sub_pos":[1180,262],"sub_size":26},
 {"type":"stamp","t_in":43.95,"t_out":45.3,"text":"BRANCH BY BRANCH","pos":[640,260],"size":56,"angle":-4,"color":"cream","fill":True},
 {"type":"flash","t_in":45.7,"dur":.2,"alpha":.25},
 {"type":"lower_third","t_in":47.1,"t_out":50.0,"title":"STILL IN HER SEAT","sub":"24 DECEMBER 1971","y":110},
 {"type":"label","t_in":50.5,"t_out":53.4,"text":"THE PERUVIAN RAINFOREST","pos":[640,150],"size":32,"color":"cream","font":"mono"},
 {"type":"spotlight","t_in":54.0,"t_out":57.9,"pos":[900,380],"r":330,"from_mult":2.4,"dim":.5,"soft":100},
 {"type":"captions","wordts":"vo/wordts.json","replace":{"Julianne's":"Juliane's","summary":"…"},"font":"serif","size":38,"y":552,"karaoke":True,"max_width":1120},
]
T=lambda f,s,vol,fi=1.0,fo=(None,1.2),**k:dict(file="sfx/"+f,start=s,volume_db=vol,fade_in=fi,fade_out=[fo[0],fo[1]],**k)
def tr(f,a,b,vol,fi=1.0,fo=1.2):
    return {"file":"sfx/"+f,"start":a,"trim_end":b-a,"fade_in":fi,"fade_out":[max(0,b-a-fo),fo],"volume_db":vol}
tracks=[
 tr("wind_gusty.wav",0,11.8,-16),tr("rain_heavy.wav",0,11.8,-15,.5,1.8),
 tr("engine_prop_distant.wav",0,10.5,-24),
 {"file":"sfx/thunder_deep.wav","start":6.4,"trim_end":4.0,"fade_in":.05,"fade_out":[2.5,1.5],"volume_db":-8},
 tr("forest_ambience.wav",11.0,24.4,-17,1.5,1.5),
 tr("wind_high_altitude.wav",23.3,37.6,-16,1.2,1.5),
 tr("room_tone_footsteps_nhe.wav",23.3,37.6,-30,1.2,1.5),
 tr("wind_gusty.wav",36.8,50.6,-17,1.2,1.5),
 tr("forest_bed_30s.wav",36.8,58.0,-13,2.0,2.5),
 {"file":"sfx/music_bed.wav","start":0,"trim_end":55.5,"fade_in":3,"fade_out":[51.5,4],"volume_db":-25},
]
for t in (.7,1.4,16.8,25.8,27.6,31.1):
    tracks.append({"file":"sfx/accent_hit.wav","start":t,"trim_end":1.2,"fade_in":.01,"fade_out":[.9,.3],"volume_db":-12})
spec={"preset":"cinematic","meta":{"width":1280,"height":720,"fps":30,"duration":D},
 "colors":{"yellow":[255,209,26],"red":[235,50,40],"cream":[255,240,200],"edge":[230,225,200],"card":[10,12,10],"white":[255,255,255]},
 "fonts":{"sans":"fonts/DejaVuSans-Bold.ttf","mono":"fonts/DejaVuSansMono-Bold.ttf","serif":"fonts/Lora-Variable.ttf#SemiBold"},
 "dissolve":.5,"grain":2.4,"vignette":.4,"warm":[1.0,1.0,1.0],
 "scenes":scenes,"elements":els,"audio":{"total":D,"vo":{"file":"vo/VO_beat2_warm-pebble.wav"},"tracks":tracks}}
print(json.dumps(spec,indent=1))
