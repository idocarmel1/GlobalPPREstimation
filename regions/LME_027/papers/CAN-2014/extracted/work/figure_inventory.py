from PIL import Image,ImageOps,ImageDraw
import pathlib,sys
p=pathlib.Path(sys.argv[1]);out=Image.new('RGB',(1500,1800),'white');d=ImageDraw.Draw(out)
for i,f in enumerate(sorted(p.glob('Figure_*.tif'))):
 im=Image.open(f).convert('RGB');im.thumbnail((480,550));x=(i%3)*500;y=(i//3)*600;out.paste(im,(x+(500-im.width)//2,y+30));d.text((x+12,y+8),f.name,fill='black')
out.save(p/'extracted/work/figure_inventory.png')
