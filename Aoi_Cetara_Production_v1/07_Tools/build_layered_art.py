"""Rebuild the editable art-preparation package from its supplied source plates.

Art is generated with imagegen. This script performs the explicitly requested
technical part separation, preserves source pixels, and packages PSD/ORA/PNG.
Polygon cuts are an initial material separation, not finished deformation art.
L/R names always mean the CHARACTER's anatomical left/right.
"""
from pathlib import Path
import csv, io, json, zipfile, math
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageCms
from psd_tools import PSDImage
from psd_tools.api.layers import PixelLayer, Group
from psd_tools.constants import Resource, BlendMode
from psd_tools.psd.image_resources import ImageResource

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT/'01_Source'
W,H=1024,1536
master=Image.open(SRC/'Aoi_Cetara_Neutral_Master.png').convert('RGBA')
assert master.size==(W,H)
rgba=np.array(master)
labels=np.zeros((H,W),dtype=np.int16)
parts=[]

def region(group,name,points,pivot=None,note='Potongan awal; rapikan tepi dan overlap sebelum deformasi.'):
    idx=len(parts)+1
    mask=Image.new('1',(W,H)); d=ImageDraw.Draw(mask)
    d.polygon(points,fill=1)
    labels[np.array(mask,dtype=bool)]=idx
    parts.append(dict(id=idx,group=group,name=name,pivot=pivot,note=note))

def rect(group,name,box,pivot=None,note=None):
    x0,y0,x1,y1=box
    region(group,name,[(x0,y0),(x1,y0),(x1,y1),(x0,y1)],pivot, note or 'Potongan awal; periksa batas bagian yang berdekatan.')

# Broad material fields, followed by smaller anatomical and ornament contours.
rect('01_HAIR_BACK','HAIR_BACK_RIGHT',(0,0,511,1050),(460,160))
rect('01_HAIR_BACK','HAIR_BACK_LEFT',(512,0,1023,1050),(562,160))
rect('02_CLOTHING_BACK','SKIRT_BACK_RIGHT',(0,1000,511,1535),(470,570))
rect('02_CLOTHING_BACK','SKIRT_BACK_LEFT',(512,1000,1023,1535),(555,570))
region('02_CLOTHING_BACK','SKIRT_BACK_CENTER',[(421,650),(602,650),(662,1190),(648,1430),(513,1465),(351,1410),(358,1180)],(512,575))
region('03_CLOTHING','TRAIN_RIGHT',[(320,736),(436,753),(400,1060),(344,1290),(292,1494),(200,1525),(23,1454),(145,1392),(207,1210),(272,1035)],(425,640))
region('03_CLOTHING','TRAIN_LEFT',[(609,753),(703,737),(753,1010),(830,1218),(903,1398),(1003,1454),(847,1530),(739,1499),(676,1254),(620,1004)],(598,640))
region('03_CLOTHING','OVERSKIRT_RIGHT',[(414,558),(480,624),(452,785),(406,1018),(346,1220),(310,1453),(228,1490),(294,1242),(321,1020),(302,883),(252,795),(293,673)],(438,562))
region('03_CLOTHING','OVERSKIRT_LEFT',[(608,552),(731,676),(791,795),(717,899),(714,1028),(778,1250),(801,1500),(724,1460),(674,1237),(607,991),(569,773),(546,631)],(585,562))
region('03_CLOTHING','SKIRT_FRONT_RIGHT',[(413,518),(496,565),(493,649),(449,716),(410,795),(350,835),(244,780),(302,686),(323,596)],(443,542))
region('03_CLOTHING','SKIRT_FRONT_LEFT',[(524,552),(606,519),(705,587),(728,686),(790,781),(690,841),(619,792),(577,708),(527,644)],(585,542))
region('03_CLOTHING','SKIRT_FRONT_CENTER',[(449,548),(510,577),(578,545),(611,641),(585,789),(539,790),(510,777),(474,791),(431,774),(426,684)],(511,570))
region('04_BODY','LEG_RIGHT',[(444,771),(508,774),(516,922),(508,1089),(508,1267),(491,1315),(458,1317),(443,1216),(444,1056),(432,882)],(475,790))
region('04_BODY','LEG_LEFT',[(509,776),(571,771),(600,893),(575,1061),(574,1215),(554,1339),(513,1332),(506,1196),(511,1030),(505,881)],(544,788))
region('04_BODY','SHOE_RIGHT',[(437,1246),(471,1245),(507,1269),(524,1326),(513,1425),(484,1467),(456,1444),(443,1377)],(480,1297))
region('04_BODY','SHOE_LEFT',[(513,1286),(551,1302),(580,1295),(594,1327),(571,1400),(566,1477),(541,1527),(509,1510),(493,1467),(501,1380)],(536,1350))
region('04_BODY','NECK',[(475,241),(544,241),(555,306),(525,338),(480,332),(469,289)],(510,269))
region('04_BODY','TORSO_UPPER',[(448,303),(478,288),(541,287),(583,305),(611,324),(636,385),(580,410),(449,406),(392,385),(405,328)],(510,365))
region('03_CLOTHING','BODICE',[(422,364),(459,370),(501,386),(529,383),(566,369),(601,368),(612,424),(587,473),(589,520),(552,569),(512,589),(468,568),(429,521),(434,473),(410,429)],(509,453))
region('05_ARMS','ARM_RIGHT',[(377,457),(409,477),(390,529),(360,577),(321,635),(281,674),(256,651),(286,602),(327,544),(354,486)],(390,480))
region('05_ARMS','ARM_LEFT',[(616,478),(646,457),(669,486),(694,544),(737,601),(769,650),(739,679),(700,634),(658,577),(634,530)],(635,480))
region('05_ARMS','HAND_RIGHT',[(256,650),(282,671),(268,704),(249,737),(233,766),(219,784),(211,773),(217,751),(207,771),(195,770),(203,746),(188,754),(174,751),(194,733),(212,718),(232,683)],(260,686))
region('05_ARMS','HAND_LEFT',[(742,671),(768,650),(791,685),(809,716),(832,733),(850,753),(837,755),(820,747),(831,769),(820,774),(808,751),(814,774),(804,784),(789,768),(777,744),(760,716)],(765,687))
region('03_CLOTHING','SLEEVE_RIGHT',[(369,366),(410,371),(432,390),(434,450),(413,486),(405,518),(373,504),(358,493),(326,484),(308,454),(326,414),(343,397)],(397,392))
region('03_CLOTHING','SLEEVE_LEFT',[(612,372),(653,367),(675,396),(693,416),(713,455),(695,486),(663,498),(646,510),(619,517),(607,489),(590,453),(592,390)],(628,392))
region('06_FACE','FACE',[(474,111),(527,110),(563,139),(579,168),(580,199),(563,233),(539,254),(511,268),(480,254),(458,236),(443,210),(443,176),(454,140)],(511,211))
region('06_FACE','EAR_RIGHT',[(438,185),(451,195),(466,217),(458,233),(444,230),(434,217),(433,200)],(447,210))
region('06_FACE','EAR_LEFT',[(568,195),(579,185),(587,199),(587,215),(576,230),(564,234),(555,218)],(571,211))
region('10_HAIR_SIDE','HAIR_SIDE_RIGHT',[(415,132),(449,153),(454,186),(450,214),(469,236),(455,249),(433,258),(428,290),(431,312),(421,340),(423,360),(401,346),(405,310),(397,294),(405,249),(390,226),(396,196)],(431,185))
region('10_HAIR_SIDE','HAIR_SIDE_LEFT',[(570,151),(602,135),(621,197),(624,232),(604,247),(610,287),(603,312),(624,355),(603,369),(585,343),(584,310),(580,286),(567,265),(550,243),(563,234),(575,207)],(586,185))
region('11_HAIR_FRONT','HAIR_CROWN',[(398,124),(408,94),(443,69),(477,57),(510,52),(547,61),(581,78),(606,110),(590,145),(547,133),(512,117),(475,134),(445,150)],(510,81))
region('11_HAIR_FRONT','BANG_RIGHT',[(449,92),(488,70),(482,122),(464,171),(451,209),(433,220),(412,198),(417,167),(427,143)],(464,97))
region('11_HAIR_FRONT','BANG_CENTER',[(488,69),(516,65),(527,106),(522,143),(534,181),(542,201),(519,197),(501,181),(486,153),(478,128)],(504,86))
region('11_HAIR_FRONT','BANG_LEFT',[(517,68),(551,77),(575,97),(584,129),(601,161),(623,186),(631,209),(607,213),(581,204),(561,187),(545,151),(528,125)],(541,92))
# Finer strands can move independently; long hidden overlaps remain to refine.
region('10_HAIR_SIDE','HAIR_TRESS_RIGHT',[(398,259),(414,273),(390,310),(355,340),(315,365),(306,390),(284,400),(280,376),(304,347),(343,322),(378,292)],(403,272))
region('10_HAIR_SIDE','HAIR_TRESS_LEFT',[(610,267),(625,258),(650,293),(688,323),(727,348),(745,379),(731,407),(711,393),(707,368),(670,345),(638,318)],(619,271))
region('01_HAIR_BACK','HAIR_TIP_RIGHT',[(133,694),(185,738),(221,800),(200,865),(175,926),(134,953),(100,939),(88,903),(93,860),(83,823)],(184,737))
region('01_HAIR_BACK','HAIR_TIP_LEFT',[(841,738),(892,693),(938,817),(934,857),(939,905),(921,944),(892,959),(855,930),(831,870),(804,800)],(840,738))
# Eye primitives from visible neutral master. Reconstructed complete irises are
# supplied separately in the hidden FACE_COMPONENTS group.
for side,cx,eye_box in [('RIGHT',474,(446,171,496,203)),('LEFT',545,(524,171,575,203))]:
    x0,y0,x1,y1=eye_box
    region('07_EYES','EYE_WHITE_'+side,[(x0,183),(x0+6,176),(cx,173),(x1-4,180),(x1,191),(x1-9,199),(cx,202),(x0+7,197)],(cx,187))
    region('07_EYES','IRIS_'+side,[(cx-10,174),(cx+8,174),(cx+13,182),(cx+12,192),(cx+6,199),(cx-7,199),(cx-13,192),(cx-13,182)],(cx,187),'Iris tampak saja; ganti/isi batas tersembunyi memakai komponen iris lengkap.')
    region('07_EYES','PUPIL_'+side,[(cx-3,178),(cx+3,178),(cx+4,185),(cx+2,193),(cx-2,193),(cx-4,185)],(cx,186),'Potongan pupil netral; siapkan clipping dengan sclera saat rig.')
    rect('07_EYES','HIGHLIGHT_'+side,(cx-4,178,cx+3,184),(cx,182))
    region('07_EYES','UPPER_EYELID_'+side,[(x0-3,178),(x0+8,171),(cx-1,171),(x1-4,176),(x1+4,182),(x1,186),(x1-8,180),(cx,177),(x0+7,180),(x0-1,186)],(cx,178))
    region('07_EYES','LOWER_EYELID_'+side,[(x0+4,195),(cx-7,199),(cx+5,199),(x1-5,195),(x1-5,199),(cx+6,202),(cx-8,202),(x0+3,198)],(cx,199))
region('08_BROWS','EYEBROW_RIGHT',[(452,151),(466,147),(479,148),(488,151),(488,155),(477,151),(466,151),(454,156)],(470,151))
region('08_BROWS','EYEBROW_LEFT',[(525,149),(539,147),(553,150),(565,155),(565,159),(552,154),(538,151),(525,153)],(545,151))
rect('06_FACE','NOSE',(501,195,515,213),(508,204),'Sorot dan garis hidung dipisah dari dasar wajah.')
rect('09_MOUTH','MOUTH_CLOSED_NEUTRAL',(499,225,519,236),(509,230),'Bibir default tertutup. Bangun keyform bibir atas/bawah; jangan regangkan garis ini sebagai seluruh mulut terbuka.')
# Jewelry kept as separate assets. Some chains still contain tiny substrate pixels.
region('12_ACCESSORIES','TIARA',[(432,74),(434,43),(457,35),(477,18),(491,20),(508,4),(526,23),(544,22),(568,42),(583,51),(581,71),(548,59),(509,52),(474,58)],(510,57))
region('12_ACCESSORIES','WHALE_TAIL_ORNAMENT',[(545,54),(571,56),(590,62),(612,54),(642,49),(672,42),(687,32),(690,51),(679,70),(650,83),(626,91),(605,96),(577,88),(556,72)],(605,88))
region('12_ACCESSORIES','HAIR_FLOWER_MAIN',[(589,89),(592,75),(607,72),(617,87),(627,88),(638,100),(630,111),(634,127),(618,128),(609,116),(592,123),(582,113),(591,102)],(609,104))
region('12_ACCESSORIES','HAIR_FLOWERS_SMALL',[(636,113),(652,111),(663,129),(654,146),(665,161),(656,178),(640,178),(625,165),(616,149),(626,136)],(644,145))
region('12_ACCESSORIES','HAIR_CLIP_RIGHT',[(394,77),(410,87),(419,101),(431,103),(433,118),(420,131),(404,126),(394,117),(403,105)],(414,111))
region('12_ACCESSORIES','FOREHEAD_JEWEL',[(501,89),(514,86),(519,105),(513,125),(511,143),(504,139),(497,120),(489,112),(490,99)],(508,102))
region('12_ACCESSORIES','HAIR_CHAIN_LEFT',[(650,174),(659,186),(660,215),(653,239),(656,266),(647,291),(648,316),(634,333),(629,325),(638,309),(637,289),(644,265),(642,240),(650,214)],(656,180))
region('12_ACCESSORIES','HAIR_CHAIN_RIGHT',[(407,160),(413,164),(406,194),(397,223),(399,246),(389,269),(385,295),(374,317),(366,313),(374,291),(379,268),(390,244),(389,220),(398,193)],(407,168))
region('12_ACCESSORIES','EARRING_RIGHT',[(447,229),(454,230),(455,248),(463,251),(465,259),(456,268),(448,260)],(450,232))
region('12_ACCESSORIES','EARRING_LEFT',[(565,230),(573,229),(570,259),(563,269),(555,259),(557,251),(564,248)],(568,232))
region('12_ACCESSORIES','COLLAR',[(478,260),(494,263),(508,280),(522,265),(541,262),(551,280),(545,299),(481,301),(471,281)],(512,286))
region('12_ACCESSORIES','NECK_RIBBON',[(477,286),(497,285),(511,292),(525,286),(544,288),(542,311),(530,315),(553,335),(538,349),(513,319),(485,347),(473,334),(491,313),(477,310)],(510,298))
region('12_ACCESSORIES','NECK_PENDANT',[(505,317),(514,315),(518,327),(514,339),(518,355),(511,364),(503,354),(506,340),(502,328)],(510,317))
region('12_ACCESSORIES','CHEST_RIBBON_RIGHT',[(449,383),(472,383),(500,394),(506,414),(493,425),(459,441),(443,426),(455,411)],(505,417))
region('12_ACCESSORIES','CHEST_RIBBON_LEFT',[(521,395),(547,383),(570,385),(563,411),(575,427),(560,442),(526,426),(513,416)],(512,417))
region('12_ACCESSORIES','CHEST_RIBBON_TAIL_RIGHT',[(498,425),(508,426),(500,476),(486,526),(468,530),(454,522),(475,478)],(501,429))
region('12_ACCESSORIES','CHEST_RIBBON_TAIL_LEFT',[(513,427),(523,424),(549,477),(567,519),(548,532),(530,527),(523,479)],(518,429))
rect('12_ACCESSORIES','CHEST_GEM',(499,408,518,430),(509,418))
region('12_ACCESSORIES','CHEST_CHAIN',[(503,430),(513,430),(511,466),(516,487),(511,515),(518,541),(510,558),(502,546),(506,516),(501,489),(506,465)],(509,431))
region('12_ACCESSORIES','SLEEVE_FLOWER_RIGHT',[(366,398),(384,398),(391,410),(407,409),(412,423),(396,433),(382,441),(371,429),(357,426),(354,414)],(383,416))
region('12_ACCESSORIES','SLEEVE_FLOWER_LEFT',[(631,408),(641,397),(658,400),(672,415),(667,430),(650,431),(641,443),(629,433),(616,423),(620,410)],(644,419))
region('12_ACCESSORIES','WAIST_RIBBON_RIGHT',[(337,591),(349,578),(373,581),(385,570),(401,579),(405,595),(421,599),(413,618),(397,621),(384,603),(367,626),(349,622),(360,602)],(384,589))
region('12_ACCESSORIES','WAIST_RIBBON_LEFT',[(607,598),(614,580),(631,570),(643,582),(667,577),(682,592),(661,602),(676,620),(655,628),(639,605),(624,622),(609,618)],(639,590))
region('12_ACCESSORIES','WAIST_CHAIN',[(443,547),(459,564),(480,575),(509,586),(536,575),(557,562),(574,545),(582,551),(562,571),(539,584),(516,595),(516,610),(509,621),(502,611),(505,594),(478,584),(454,571),(436,554)],(510,586))
region('12_ACCESSORIES','BRACELET_RIGHT',[(264,633),(281,635),(297,650),(286,673),(272,688),(252,680),(244,667),(251,651)],(271,662))
region('12_ACCESSORIES','BRACELET_LEFT',[(728,650),(746,634),(762,634),(776,651),(781,669),(771,683),(751,687),(738,672)],(754,663))
region('12_ACCESSORIES','THIGH_GARTER_LEFT',[(511,810),(536,815),(549,807),(565,813),(578,811),(594,831),(591,852),(575,865),(550,852),(527,862),(508,848)],(548,833))
region('12_ACCESSORIES','THIGH_JEWELS_LEFT',[(528,854),(544,850),(550,867),(563,859),(579,858),(597,871),(594,910),(587,927),(581,912),(582,887),(569,875),(555,880),(545,869),(543,897),(536,921),(527,908),(534,884)],(548,855))
region('12_ACCESSORIES','TRAIN_GEM_RIGHT',[(148,1026),(164,1028),(169,1053),(161,1074),(149,1061),(144,1048)],(157,1034))
region('12_ACCESSORIES','TRAIN_GEM_LEFT',[(862,1029),(875,1025),(882,1048),(877,1063),(866,1076),(858,1053)],(869,1035))
region('12_ACCESSORIES','HAIR_STAR_RIGHT',[(108,820),(123,821),(127,844),(123,853),(128,868),(120,882),(111,875),(104,865),(110,850)],(117,824))
region('12_ACCESSORIES','HAIR_STAR_LEFT',[(907,823),(920,822),(925,847),(920,858),(926,874),(916,889),(906,874),(900,864),(909,849)],(915,826))

# Write real independent raster layers; no duplication of the flattened master.
layers=[]
for p in parts:
    a=rgba.copy(); selected=(labels==p['id']); a[~selected]=0; a[a[:,:,3]==0]=0
    bbox=Image.fromarray(a).getbbox()
    if not bbox: continue
    p.update(visible=True,status='CUT_NEEDS_EDGE_AND_OVERLAP_REVIEW',source='Aoi_Cetara_Neutral_Master.png')
    layers.append((p,Image.fromarray(a)))
assert np.all(labels[rgba[:,:,3]>0]>0),'Unclassified nontransparent pixels'

# Independent generated backfill plates, aligned coarsely. Hidden until artist QC.
bf=Image.open(SRC/'Backfill_Head_and_Dressed_Body.png').convert('RGBA')
bf_canvas=Image.new('RGBA',(W,H));bf_canvas.paste(bf,(0,20))
for name,points,pivot in [
('BF_FACE_COMPLETE',[(430,56),(588,56),(596,191),(572,250),(512,271),(451,246),(425,192)],(511,211)),
('BF_NECK_AND_TORSO',[(398,260),(625,260),(649,389),(602,455),(418,454),(379,385)],(511,330)),
('BF_CLOTHING_BODY',[(405,371),(619,371),(629,519),(713,663),(781,799),(692,891),(594,827),(510,780),(422,826),(324,889),(239,789),(311,659),(394,518)],(511,565)),
('BF_LOWER_SKIRT',[(425,736),(596,736),(712,1099),(858,1459),(704,1509),(326,1509),(158,1451),(309,1083)],(511,755))]:
    mask=Image.new('L',(W,H));ImageDraw.Draw(mask).polygon(points,fill=255)
    aa=np.array(bf_canvas); aa[:,:,3]=(aa[:,:,3].astype(np.uint16)*np.array(mask)//255).astype(np.uint8)
    layers.append((dict(group='00_BACKFILL_ALIGN_FIRST',name=name,visible=False,pivot=pivot,status='GENERATED_BACKFILL_ALIGNMENT_REQUIRED',source='Backfill_Head_and_Dressed_Body.png',note='Plate terpisah; offset awal y+20. Cocokkan kontur/shading sebelum diaktifkan.'),Image.fromarray(aa)))
hair=Image.open(SRC/'Backfill_Rear_Hair.png').convert('RGBA')
# Exact source remains in 01_Source; this placement is only an alignment starting point.
hair_crop=hair.crop((0,20,1024,1240)).resize((928,928),Image.Resampling.LANCZOS)
hair_canvas=Image.new('RGBA',(W,H));hair_canvas.paste(hair_crop,(48,50))
layers.append((dict(group='00_BACKFILL_ALIGN_FIRST',name='BF_HAIR_BACK_COMPLETE',visible=False,pivot=(512,150),status='GENERATED_BACKFILL_ALIGNMENT_REQUIRED',source='Backfill_Rear_Hair.png',note='Rambut belakang utuh tanpa lubang kepala/badan. Periksa posisi dan siluet sebelum aktif.'),hair_canvas))

# Crop the 16 generated components into useful source PNGs and place optional
# aligned variants in a hidden group. Do not silently replace the neutral face.
kit=Image.open(SRC/'Face_Components_Sheet.png').convert('RGBA')
kit_out=ROOT/'03_PNG_Layers'/'Face_Components_Highres';kit_out.mkdir(exist_ok=True)
kit_spec=[
('SCLERA_RIGHT',(446,174,496,202)),('SCLERA_LEFT',(524,174,574,202)),
('IRIS_FULL_RIGHT',(460,173,488,201)),('IRIS_FULL_LEFT',(531,173,559,201)),
('PUPIL_FULL_RIGHT',(470,178,478,195)),('PUPIL_FULL_LEFT',(541,178,549,195)),
('GLINT_RIGHT',(467,177,481,189)),('GLINT_LEFT',(538,177,552,189)),
('LASH_UPPER_RIGHT',(445,171,497,186)),('LASH_UPPER_LEFT',(523,171,575,186)),
('LASH_LOWER_RIGHT',(450,195,492,203)),('LASH_LOWER_LEFT',(528,195,571,203)),
('MOUTH_INSIDE',(496,228,522,244)),('TEETH',(499,229,519,234)),
('TONGUE',(502,236,517,243)),('MOUTH_CLOSED_ALT',(498,226,520,234))]
component_records=[]
for idx,(name,target) in enumerate(kit_spec):
    cw,ch=kit.width//4,kit.height//4; col,row=idx%4,idx//4
    cell=kit.crop((col*cw,row*ch,(col+1)*cw,(row+1)*ch))
    # Tight bounds of visible content; alpha itself is retained unchanged.
    threshold=cell.getchannel('A').point(lambda a:255 if a>64 else 0)
    bbox=threshold.getbbox() or cell.getbbox(); crop=cell.crop(bbox)
    crop.save(kit_out/(name+'.png'))
    x0,y0,x1,y1=target
    aligned=Image.new('RGBA',(W,H));aligned.paste(crop.resize((x1-x0,y1-y0),Image.Resampling.LANCZOS),(x0,y0))
    meta=dict(group='13_FACE_COMPONENTS_ALTERNATES',name='ALT_'+name,visible=False,pivot=((x0+x1)//2,(y0+y1)//2),status='OPTIONAL_COMPONENT_FIT_AND_CLEAN_REQUIRED',source='Face_Components_Sheet.png',note='Komponen lengkap dari plate terpisah; ganti padanan asli, jangan aktifkan keduanya. Sesuaikan outline dan warna.')
    layers.append((meta,aligned))
    component_records.append(dict(name=name,source_cell=idx+1,source_size=crop.size,target_bbox=target,file='03_PNG_Layers/Face_Components_Highres/'+name+'.png'))

supplement=Image.open(SRC/'Facial_Supplement_Sheet.png').convert('RGBA')
supp_spec=[('MOUTH_UPPER',(498,227,520,232)),('MOUTH_LOWER',(501,231,518,235)),('BLUSH_RIGHT',(449,203,487,221)),('BLUSH_LEFT',(531,203,570,221)),('EYEBROW_FULL_RIGHT',(452,147,489,156)),('EYEBROW_FULL_LEFT',(525,147,565,159))]
for idx,(name,target) in enumerate(supp_spec):
    col,row=idx%3,idx//3
    cell=supplement.crop((round(col*supplement.width/3),round(row*supplement.height/2),round((col+1)*supplement.width/3),round((row+1)*supplement.height/2)))
    bbox=cell.getchannel('A').point(lambda a:255 if a>32 else 0).getbbox() or cell.getbbox()
    crop=cell.crop(bbox);crop.save(kit_out/(name+'.png'))
    x0,y0,x1,y1=target;aligned=Image.new('RGBA',(W,H))
    aligned.paste(crop.resize((x1-x0,y1-y0),Image.Resampling.LANCZOS),(x0,y0))
    layers.append((dict(group='13_FACE_COMPONENTS_ALTERNATES',name='ALT_'+name,visible=False,pivot=((x0+x1)//2,(y0+y1)//2),status='OPTIONAL_COMPONENT_FIT_AND_CLEAN_REQUIRED',source='Facial_Supplement_Sheet.png',note='Bahan tambahan terpisah; sesuaikan kontur/warna. Blush default opacity 0; aktif hanya untuk ekspresi.'),aligned))
    component_records.append(dict(name=name,source_cell=idx+1,source_size=crop.size,target_bbox=target,file='03_PNG_Layers/Face_Components_Highres/'+name+'.png'))

layers.sort(key=lambda item:item[0]['group'])
psd=PSDImage.new('RGBA',(W,H),color=(0,0,0,0),depth=8)
psd._background_color=None
psd._merged_alpha=True
icc=ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB')).tobytes()
psd.image_resources[Resource.ICC_PROFILE]=ImageResource(key=Resource.ICC_PROFILE,data=icc)
groups={};manifest=[];merged=Image.new('RGBA',(W,H))
for order,(p,im) in enumerate(layers):
    group_name=p['group']
    if group_name not in groups:
        groups[group_name]=Group.new(psd,group_name)
        groups[group_name].blend_mode=BlendMode.NORMAL
    # Discard only invisible RGB; preserve every visible source pixel and alpha.
    clean=np.array(im);clean[clean[:,:,3]==0]=0;im=Image.fromarray(clean)
    box=im.getbbox();assert box
    outdir=ROOT/'03_PNG_Layers'/group_name;outdir.mkdir(exist_ok=True)
    file=outdir/(p['name']+'.png');png_tmp=file.with_suffix('.png.tmp')
    im.save(png_tmp,format='PNG',icc_profile=icc);png_tmp.replace(file)
    layer=PixelLayer.frompil(im.crop(box),groups[group_name],name=p['name'],left=box[0],top=box[1])
    layer.visible=p['visible'];layer.blend_mode=BlendMode.NORMAL
    if p['visible']:merged.alpha_composite(im)
    meta={k:v for k,v in p.items() if k!='id'}
    meta.update(order_bottom_to_top=order,bbox=list(box),canvas=[W,H],png=file.relative_to(ROOT).as_posix(),nontransparent_pixels=int(np.count_nonzero(np.array(im)[:,:,3])))
    manifest.append(meta)
psd_path=ROOT/'02_Layered_Artwork'/'Aoi_Cetara_ArtPrep_v1.psd'
psd_tmp=psd_path.with_suffix('.psd.tmp')
psd.save(psd_tmp)
psd_tmp.replace(psd_path)
merged.save(ROOT/'06_Previews'/'Aoi_Cetara_Layered_Composite.png',icc_profile=icc)
with (ROOT/'02_Layered_Artwork'/'Layer_Manifest.json').open('w') as f:
    json.dump(dict(project='Aoi Cetara',stage='ART_PREPARATION_NOT_RIGGED',canvas=[W,H],side_convention='LEFT/RIGHT = anatomical character; viewer-left = RIGHT',layers=manifest,face_components=component_records),f,ensure_ascii=False,indent=2)
with (ROOT/'02_Layered_Artwork'/'Layer_Manifest.csv').open('w',newline='',encoding='utf-8-sig') as f:
    writer=csv.DictWriter(f,fieldnames=['name','group','visible','status','pivot','bbox','png','note'],extrasaction='ignore');writer.writeheader();writer.writerows(manifest)

# OpenRaster alternative with real grouped independent layers.
ora=ROOT/'02_Layered_Artwork'/'Aoi_Cetara_ArtPrep_v1.ora'
image_node=ET.Element('image',w=str(W),h=str(H),name='Aoi Cetara ArtPrep v1',version='0.0.3')
stack=ET.SubElement(image_node,'stack');ora_groups={}
ora_tmp=ora.with_suffix('.ora.tmp')
with zipfile.ZipFile(ora_tmp,'w',zipfile.ZIP_DEFLATED) as z:
    z.writestr('mimetype','image/openraster',compress_type=zipfile.ZIP_STORED)
    for idx,(p,im) in enumerate(reversed(layers)):
        group=p['group']
        if group not in ora_groups:
            ora_groups[group]=ET.SubElement(stack,'stack',name=group,opacity='1.0',visibility='visible',isolation='isolate',**{'composite-op':'svg:src-over'})
        box=im.getbbox();buff=io.BytesIO();im.crop(box).save(buff,format='PNG')
        src='data/layer%03d.png'%idx;z.writestr(src,buff.getvalue())
        ET.SubElement(ora_groups[group],'layer',name=p['name'],src=src,x=str(box[0]),y=str(box[1]),opacity='1.0',visibility='visible' if p['visible'] else 'hidden',**{'composite-op':'svg:src-over'})
    z.writestr('stack.xml',ET.tostring(image_node,encoding='utf-8',xml_declaration=True))
    b=io.BytesIO();merged.save(b,format='PNG');z.writestr('mergedimage.png',b.getvalue())
    thumb=merged.copy();thumb.thumbnail((256,256));b=io.BytesIO();thumb.save(b,format='PNG');z.writestr('Thumbnails/thumbnail.png',b.getvalue())
with zipfile.ZipFile(ora_tmp) as verify_archive:
    assert verify_archive.testzip() is None
ora_tmp.replace(ora)

# Technical contact sheet and exact reconstruction validation.
font_path='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
font=ImageFont.truetype(font_path,15);tiny=ImageFont.truetype(font_path,12)
cols=6;cw,ch=260,245;rows=math.ceil(len(layers)/cols)
board=Image.new('RGB',(cols*cw,rows*ch+85),'#eef3fa');d=ImageDraw.Draw(board)
d.text((26,20),'AOI CETARA / MATERIAL SEPARATION v1',font=ImageFont.truetype(font_path,25),fill='#273654')
d.text((26,53),'Cut parts + optional backfill / Source 1024 x 1536 / Not a rig preview',font=font,fill='#53627c')
for idx,(p,im) in enumerate(layers):
    x=(idx%cols)*cw;y=85+(idx//cols)*ch
    for yy in range(y+8,y+195,16):
        for xx in range(x+8,x+cw-8,16):
            d.rectangle((xx,yy,min(xx+15,x+cw-9),min(yy+15,y+194)),fill='#cad5e5' if ((xx-x)//16+(yy-y)//16)%2 else '#e4eaf4')
    crop=im.crop(im.getbbox());crop.thumbnail((cw-30,178))
    board.paste(crop,(x+(cw-crop.width)//2,y+10+(178-crop.height)//2),crop)
    d.text((x+12,y+202),p['name'][:31],font=tiny,fill='#26334c')
    d.text((x+12,y+220),'VISIBLE CUT' if p['visible'] else 'OPTIONAL / ALIGN FIRST',font=tiny,fill='#486789' if p['visible'] else '#956b32')
board.save(ROOT/'06_Previews'/'Layer_Contact_Sheet.jpg',quality=90)
diff=np.abs(np.array(merged).astype(int)-rgba.astype(int))
visible=rgba[:,:,3]>0
reopened=PSDImage.open(psd_path)
leaves=[l for l in reopened.descendants() if not l.is_group()]
qc=dict(canvas=[W,H],rgb_depth=reopened.depth,total_pixel_layers=len(leaves),visible_cut_layers=sum(p['visible'] for p,_ in layers),optional_backfill_layers=5,optional_face_component_layers=len(component_records),layer_names_unique=len(set(l.name for l in leaves))==len(leaves),all_layers_nonempty=all(m['nontransparent_pixels']>0 for m in manifest),layer_masks=sum(l.has_mask() for l in leaves),default_composite_max_pixel_difference=int(diff[visible].max()),native_cubism_import_tested=False,live2d_rig_created=False,vtube_studio_tested=False,remaining_artwork_work=['Rapi ulang tepi potongan, terutama rantai dan perhiasan kecil.','Aktifkan backfill hanya setelah menyamakan posisi, outline, dan warna.','Lengkapi overlap antarhelai rambut, lengan, tangan, dan kain saat digerakkan.','Selaraskan bibir atas/bawah dan blush opsional; semua komponennya tersedia tetapi belum diuji deformasi.','Bangun masking sclera/iris dan semua keyform mata-mulut di Cubism.'])
(ROOT/'06_Previews'/'QA_Result.json').write_text(json.dumps(qc,ensure_ascii=False,indent=2))
assert qc['layer_names_unique'] and qc['all_layers_nonempty'] and qc['layer_masks']==0
assert qc['default_composite_max_pixel_difference']==0
print(json.dumps(qc,ensure_ascii=False,indent=2))

if __name__=='__main__':
    print('Saved',psd_path)
