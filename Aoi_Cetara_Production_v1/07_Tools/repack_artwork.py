"""Repackage existing layer PNGs without redrawing or regenerating artwork."""
from pathlib import Path
import json,io,zipfile
import xml.etree.ElementTree as ET
from PIL import Image,ImageCms
from psd_tools import PSDImage
from psd_tools.api.layers import Group,PixelLayer
from psd_tools.constants import Resource,BlendMode
from psd_tools.psd.image_resources import ImageResource

r=Path(__file__).resolve().parents[1]
m=json.loads((r/'02_Layered_Artwork/Layer_Manifest.json').read_text())
psd=PSDImage.new('RGBA',tuple(m['canvas']),color=(0,0,0,0),depth=8)
# Preserve composite transparency as well as per-layer transparency.
psd._background_color=None
psd._merged_alpha=True
icc=ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB')).tobytes()
psd.image_resources[Resource.ICC_PROFILE]=ImageResource(key=Resource.ICC_PROFILE,data=icc)
groups={}
for item in m['layers']:
    group=item['group']
    if group not in groups:
        groups[group]=Group.new(psd,group);groups[group].blend_mode=BlendMode.NORMAL
    im=Image.open(r/item['png']).convert('RGBA');b=im.getbbox()
    layer=PixelLayer.frompil(im.crop(b),groups[group],name=item['name'],top=b[1],left=b[0]);layer.visible=item['visible']
out=r/'02_Layered_Artwork/Aoi_Cetara_ArtPrep_v1.psd'
tmp=out.with_suffix('.psd.tmp');psd.save(tmp)
check=PSDImage.open(tmp)
assert check.topil().mode=='RGBA'
assert len([l for l in check.descendants() if not l.is_group()])==113
tmp.replace(out)

ora=r/'02_Layered_Artwork/Aoi_Cetara_ArtPrep_v1.ora';tmp=ora.with_suffix('.ora.tmp')
root=ET.Element('image',w=str(m['canvas'][0]),h=str(m['canvas'][1]),name='Aoi Cetara ArtPrep v1',version='0.0.3')
stack=ET.SubElement(root,'stack');groups={}
with zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED) as z:
    z.writestr('mimetype','image/openraster',compress_type=zipfile.ZIP_STORED)
    for i,item in enumerate(reversed(m['layers'])):
        group=item['group']
        if group not in groups:
            groups[group]=ET.SubElement(stack,'stack',name=group,opacity='1.0',visibility='visible',isolation='isolate',**{'composite-op':'svg:src-over'})
        im=Image.open(r/item['png']).convert('RGBA');b=im.getbbox();data=io.BytesIO();im.crop(b).save(data,format='PNG')
        path=f'data/layer{i:03}.png';z.writestr(path,data.getvalue())
        ET.SubElement(groups[group],'layer',name=item['name'],src=path,x=str(b[0]),y=str(b[1]),opacity='1.0',visibility='visible' if item['visible'] else 'hidden',**{'composite-op':'svg:src-over'})
    z.writestr('stack.xml',ET.tostring(root,encoding='utf-8',xml_declaration=True))
    z.write(r/'06_Previews/Aoi_Cetara_Layered_Composite.png','mergedimage.png')
    thumb=Image.open(r/'06_Previews/Aoi_Cetara_Layered_Composite.png');thumb.thumbnail((256,256));data=io.BytesIO();thumb.save(data,format='PNG');z.writestr('Thumbnails/thumbnail.png',data.getvalue())
with zipfile.ZipFile(tmp) as z:
    assert z.testzip() is None
    assert len(z.namelist())==117
tmp.replace(ora)
print('Repacked PSD with RGBA composite, 113 pixel layers; ORA CRC validated.')
