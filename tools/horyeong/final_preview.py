import sys, json, numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0,'.')
import cg
R=sys.argv[1]; OUT=sys.argv[2]
A=R+'/assets/cobblemon'
m=cg.load_geo(A+'/bedrock/pokemon/models/horyeong/horyeong.geo.json')
T=lambda n: np.array(Image.open(A+'/textures/pokemon/horyeong/'+n).convert('RGBA'))
tn,ts,ta=T('horyeong.png'),T('horyeong_shiny.png'),T('horyeong_alpha.png')
AN={k.split('.')[-1]:v for k,v in json.load(open(A+'/bedrock/pokemon/animations/horyeong/horyeong.animation.json'))['animations'].items()}
parts=cg.build_java(m)
idle=cg.anim_overrides(AN['ground_idle'],0.0)
def lab(im,t):
    img=Image.fromarray(im); ImageDraw.Draw(img).text((8,8),t,fill=(255,255,255)); return np.array(img)
row1=[lab(cg.render(m,parts,tn,idle,yaw=30,pitch=8,scale=9,size=(460,480),center=(0,21,-2)),'normal'),
      lab(cg.render(m,parts,ts,idle,yaw=30,pitch=8,scale=9,size=(460,480),center=(0,21,-2)),'shiny'),
      lab(cg.render(m,parts,tn,idle,yaw=30,pitch=8,scale=9,size=(460,480),center=(0,21,-2),emissive=ta,bg=(20,22,30)),'alpha (normal + glowing eyes)'),
      lab(cg.render(m,parts,ts,idle,yaw=-30,pitch=8,scale=9,size=(460,480),center=(0,21,-2),emissive=ta,bg=(20,22,30)),'alpha shiny')]
bi=cg.anim_overrides(AN['battle_idle'],0.0)
sl=cg.anim_overrides(AN['sleep'],0.0)
row2=[lab(cg.render(m,parts,tn,bi,yaw=40,pitch=12,scale=7,size=(460,400),center=(0,19,-2)),'battle_idle'),
      lab(cg.render(m,parts,tn,cg.anim_overrides(AN['ground_walk'],0.3),yaw=75,pitch=10,scale=7,size=(460,400),center=(0,18,0)),'ground_walk'),
      lab(cg.render(m,parts,tn,cg.anim_overrides(AN['cry'],0.8,base=idle),yaw=20,pitch=8,scale=7,size=(460,400),center=(0,24,-4)),'cry'),
      lab(cg.render(m,parts,tn,sl,yaw=40,pitch=25,scale=7,size=(460,400),center=(0,8,-4)),'sleep')]
Image.fromarray(np.concatenate([np.concatenate(row1,1),np.concatenate(row2,1)],0)).save(OUT)
print(OUT)
