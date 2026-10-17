"""Create honest, unrigged handoff specifications and conditional JSON templates."""
from pathlib import Path
import csv,json

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'04_Rigging_Spec'; EX=ROOT/'05_Expression_Templates'
def write(path,obj):path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
params=[]
def param(pid,lo,default,hi,keys,purpose,status='KEYFORMS_NOT_BUILT'):
    params.append(dict(id=pid,min=lo,default=default,max=hi,keyforms=keys,purpose=purpose,status=status))
for a in 'XYZ':param('ParamAngle'+a,-30,0,30,[-30,0,30],'Kepala '+a+'; uji sudut gabungan, tambah backfill sebelum ekstrem.')
for a in 'XY':param('ParamEyeBall'+a,-1,0,1,[-1,0,1],'Arah iris/pupil/glint; clipping ke sclera.')
for side in 'LR':
    param('ParamEye'+side+'Open',0,1,1,[0,.5,1],'Tutup penuh tanpa bocor; default 1.')
    param('ParamEye'+side+'Smile',0,0,1,[0,1],'Bentuk mata senyum pada kedipan; netral 0.')
    for dim in ['Y','Angle','Form']:
        param('ParamBrow'+side+dim,-1,0,1,[-1,0,1],'Alis '+side+' '+dim+'; Form: -1 sedih, 0 netral, +1 tegas/marah.')
param('ParamMouthOpenY',0,0,1,[0,.25,.5,.75,1],'Bukaan mulut; default 0. Padankan ke volume/audio atau pelacakan.')
param('ParamMouthForm',-1,0,1,[-1,0,1],'Bentuk bibir: sedih / netral / senyum. Cross-key dengan bukaan.')
param('ParamMouthVowel',0,0,5,[0,1,2,3,4,5],'CUSTOM: 0 netral, 1 A, 2 I, 3 U, 4 E, 5 O. Perlu penggerak fonem; volume audio saja tidak memilih vokal.')
for a in 'XYZ':param('ParamBodyAngle'+a,-10,0,10,[-10,0,10],'Rotasi/warp badan '+a+' lembut; amplitudo akhir ditentukan saat rig.')
param('ParamBreath',0,0,1,[0,1],'Napas lembut; kunci kaki, bahu naik tipis.')
param('ParamCheek',0,0,1,[0,1],'Opacity blush. Artwork blush opsional tersedia; selaraskan pada pipi lalu atur opacity default 0.')
physics_channels=['HairBackL','HairBackR','HairSideL','HairSideR','HairFront','Ribbon','SkirtL','SkirtR','EarringL','EarringR','Chain','WhaleOrnament']
for name in physics_channels: param('Param'+name+'Sway',-1,0,1,[-1,0,1],'CUSTOM physics output; jangan dipetakan sebagai input pelacakan.')
write(OUT/'Parameter_Spec.json',dict(status='PLANNED_NOT_IMPLEMENTED',parameters=params))
with (OUT/'Parameter_Spec.csv').open('w',newline='',encoding='utf-8-sig') as f:
    wr=csv.DictWriter(f,fieldnames=list(params[0]));wr.writeheader();wr.writerows(params)

legacy={
'PARAM_ANGLE_X':'ParamAngleX','PARAM_ANGLE_Y':'ParamAngleY','PARAM_ANGLE_Z':'ParamAngleZ',
'PARAM_EYE_BALL_X':'ParamEyeBallX','PARAM_EYE_BALL_Y':'ParamEyeBallY',
'PARAM_EYE_L_OPEN':'ParamEyeLOpen','PARAM_EYE_R_OPEN':'ParamEyeROpen',
'PARAM_BROW_L':'ParamBrowLY / ParamBrowLAngle / ParamBrowLForm',
'PARAM_BROW_R':'ParamBrowRY / ParamBrowRAngle / ParamBrowRForm',
'PARAM_MOUTH_OPEN_Y':'ParamMouthOpenY','PARAM_MOUTH_FORM':'ParamMouthForm',
'PARAM_BODY_ANGLE_X':'ParamBodyAngleX','PARAM_BODY_ANGLE_Y':'ParamBodyAngleY','PARAM_BODY_ANGLE_Z':'ParamBodyAngleZ',
'PARAM_BREATH':'ParamBreath','PARAM_HAIR_SWAY':'ParamHairBackLSway / ParamHairBackRSway / ParamHairSideLSway / ParamHairSideRSway / ParamHairFrontSway',
'PARAM_CLOTH_SWAY':'ParamSkirtLSway / ParamSkirtRSway / ParamRibbonSway',
'PARAM_ACCESSORY_SWAY':'ParamEarringLSway / ParamEarringRSway / ParamChainSway / ParamWhaleOrnamentSway'}
write(OUT/'Brief_Parameter_Mapping.json',legacy)

deformers=[
dict(id='D_ROOT',parent=None,type='rotation',pivot=[512,1460],parameters=[],members=['all']),
dict(id='D_BODY',parent='D_ROOT',type='warp',pivot=[512,645],parameters=['ParamBodyAngleX','ParamBodyAngleY','ParamBodyAngleZ','ParamBreath'],members=['clothing','torso','arms','neck','head']),
dict(id='D_HEAD_Z',parent='D_BODY',type='rotation',pivot=[511,275],parameters=['ParamAngleZ'],members=['head','face','eyes','brows','mouth','head hair','head accessories']),
dict(id='D_HEAD_XY',parent='D_HEAD_Z',type='warp',pivot=[511,200],parameters=['ParamAngleX','ParamAngleY'],members=['face','ears','eyes','brows','mouth','front hair','head ornaments']),
dict(id='D_EYE_L',parent='D_HEAD_XY',type='warp',pivot=[545,187],parameters=['ParamEyeLOpen','ParamEyeLSmile'],members=['EYE_*_LEFT','IRIS_LEFT','PUPIL_LEFT','HIGHLIGHT_LEFT','*_EYELID_LEFT']),
dict(id='D_EYE_R',parent='D_HEAD_XY',type='warp',pivot=[474,187],parameters=['ParamEyeROpen','ParamEyeRSmile'],members=['EYE_*_RIGHT','IRIS_RIGHT','PUPIL_RIGHT','HIGHLIGHT_RIGHT','*_EYELID_RIGHT']),
dict(id='D_GAZE_L',parent='D_EYE_L',type='warp',pivot=[545,187],parameters=['ParamEyeBallX','ParamEyeBallY'],members=['IRIS_LEFT','PUPIL_LEFT','HIGHLIGHT_LEFT']),
dict(id='D_GAZE_R',parent='D_EYE_R',type='warp',pivot=[474,187],parameters=['ParamEyeBallX','ParamEyeBallY'],members=['IRIS_RIGHT','PUPIL_RIGHT','HIGHLIGHT_RIGHT']),
dict(id='D_MOUTH',parent='D_HEAD_XY',type='warp',pivot=[509,231],parameters=['ParamMouthOpenY','ParamMouthForm','ParamMouthVowel'],members=['ALT_MOUTH_UPPER','ALT_MOUTH_LOWER','ALT_MOUTH_INSIDE','ALT_TEETH','ALT_TONGUE']),
dict(id='D_HAIR_BACK',parent='D_BODY',type='warp',pivot=[512,175],parameters=['ParamHairBackLSway','ParamHairBackRSway'],members=['HAIR_BACK_LEFT','HAIR_BACK_RIGHT','HAIR_TIP_LEFT','HAIR_TIP_RIGHT']),
dict(id='D_HAIR_FRONT',parent='D_HEAD_XY',type='warp',pivot=[512,85],parameters=['ParamHairFrontSway'],members=['BANG_RIGHT','BANG_CENTER','BANG_LEFT']),
dict(id='D_SKIRT',parent='D_BODY',type='warp',pivot=[512,575],parameters=['ParamSkirtLSway','ParamSkirtRSway'],members=['SKIRT_*','TRAIN_*','OVERSKIRT_*']),
dict(id='D_ACCESSORIES',parent='D_BODY',type='per-object rotation+warp',pivot=None,parameters=['ParamRibbonSway','ParamChainSway'],members=['chest ribbons','waist ribbons','waist chains']),
dict(id='D_HEAD_ACCESSORIES',parent='D_HEAD_XY',type='per-object rotation+warp',pivot=None,parameters=['ParamEarringLSway','ParamEarringRSway','ParamWhaleOrnamentSway'],members=['earrings','whale ornament'])]
write(OUT/'Deformer_Hierarchy.spec.json',dict(status='PLAN_ONLY_NOT_CMO3',coordinate_system='source pixels top-left origin',deformers=deformers))

# Valid-format conditional templates. Values are initial tuning proposals only.
settings=[];dictionary=[]
for i,name in enumerate(physics_channels):
    pid='PhysicsSetting'+str(i+1);dictionary.append(dict(Id=pid,Name=name))
    is_hair='Hair' in name; is_skirt='Skirt' in name
    main='ParamBodyAngleX' if is_skirt else 'ParamAngleX'
    other='ParamBodyAngleZ' if is_skirt else 'ParamAngleZ'
    delay=.28 if is_hair else (.35 if is_skirt else .22)
    mobility=.72 if is_hair else (.65 if is_skirt else .58)
    settings.append(dict(Id=pid,
      Input=[dict(Source=dict(Target='Parameter',Id=main),Weight=100,Type='X',Reflect=False),dict(Source=dict(Target='Parameter',Id=other),Weight=100,Type='Angle',Reflect=False)],
      Output=[dict(Destination=dict(Target='Parameter',Id='Param'+name+'Sway'),VertexIndex=2,Scale=.08 if is_hair else .05,Weight=65 if is_hair else 50,Type='Angle',Reflect=False)],
      Vertices=[dict(Position=dict(X=0,Y=0),Mobility=1,Delay=1,Acceleration=1,Radius=0),dict(Position=dict(X=0,Y=5),Mobility=mobility,Delay=delay,Acceleration=.7,Radius=5),dict(Position=dict(X=0,Y=10),Mobility=mobility*.9,Delay=delay*1.2,Acceleration=.7,Radius=5)],
      Normalization=dict(Position=dict(Minimum=-10,Default=0,Maximum=10),Angle=dict(Minimum=-30,Default=0,Maximum=30))))
physics=dict(Version=3,Meta=dict(PhysicsSettingCount=len(settings),TotalInputCount=2*len(settings),TotalOutputCount=len(settings),VertexCount=3*len(settings),Fps=60,EffectiveForces=dict(Gravity=dict(X=0,Y=-1),Wind=dict(X=0,Y=0)),PhysicsDictionary=dictionary),PhysicsSettings=settings)
write(OUT/'Aoi_Cetara_TEMPLATE.physics3.json',physics)

baseline={'ParamMouthForm':0,'ParamEyeLSmile':0,'ParamEyeRSmile':0,'ParamBrowLForm':0,'ParamBrowRForm':0,'ParamBrowLY':0,'ParamBrowRY':0,'ParamBrowLAngle':0,'ParamBrowRAngle':0,'ParamCheek':0}
recipes={
 'DEFAULT':{},
 'SMILE':{'ParamMouthForm':.45},
 'HAPPY':{'ParamMouthForm':.85,'ParamEyeLSmile':1,'ParamEyeRSmile':1,'ParamBrowLY':.15,'ParamBrowRY':.15},
 'SAD':{'ParamMouthForm':-.6,'ParamBrowLForm':-1,'ParamBrowRForm':-1},
 'ANGRY':{'ParamMouthForm':-.3,'ParamBrowLForm':1,'ParamBrowRForm':1,'ParamBrowLY':-.2,'ParamBrowRY':-.2},
 'SURPRISED':{'ParamBrowLY':.8,'ParamBrowRY':.8,'ParamMouthForm':-.2,'ParamMouthOpenY':.55},
 'SHY':{'ParamMouthForm':.15,'ParamCheek':.75},
 'BLINK':{'ParamEyeLOpen':0,'ParamEyeROpen':0},
 'WINK':{'ParamEyeLOpen':0,'ParamEyeLSmile':.6,'ParamMouthForm':.25}}
for name,values in recipes.items():
    p=baseline|values
    write(EX/(name+'.exp3.json'),dict(Type='Live2D Expression',FadeInTime=.18,FadeOutTime=.25,Parameters=[dict(Id=k,Value=v,Blend='Overwrite') for k,v in p.items()]))

motions=OUT/'Motion_Templates';motions.mkdir(exist_ok=True)
def motion(name,duration,curve_points,loop=False):
    curves=[];ns=np=0
    for pid,pts in curve_points.items():
        values=list(pts[0])
        for t,v in pts[1:]: values.extend([0,t,v])
        curves.append(dict(Target='Parameter',Id=pid,Segments=values));ns+=len(pts)-1;np+=len(pts)
    write(motions/(name+'.motion3.json'),dict(Version=3,Meta=dict(Duration=duration,Fps=60,Loop=loop,AreBeziersRestricted=True,FadeInTime=.1,FadeOutTime=.1,CurveCount=len(curves),TotalSegmentCount=ns,TotalPointCount=np,UserDataCount=0,TotalUserDataSize=0),Curves=curves,UserData=[]))
blink=[(0,1),(.07,.25),(.10,0),(.15,0),(.23,1),(.3,1)]
motion('Blink_Once_TEMPLATE',.3,{'ParamEyeLOpen':blink,'ParamEyeROpen':blink})
motion('Breath_Idle_TEMPLATE',4,{'ParamBreath':[(0,0),(.5,.15),(1,.5),(1.5,.85),(2,1),(2.5,.85),(3,.5),(3.5,.15),(4,0)]},True)

write(OUT/'Runtime_Export_Contract.json',dict(status='NOT_EXPORTED_NOT_LOADABLE',native_project_present=False,moc3_present=False,model3_present=False,texture_atlas_present=False,required_exports=['Aoi_Cetara.cmo3 (editable project; not loaded by VTube Studio)','Aoi_Cetara.moc3','Aoi_Cetara.model3.json','Aoi_Cetara.physics3.json','Texture atlas PNG(s) referenced by the exported model3.json'],instruction='Generate these in Cubism after material cleanup, ArtMesh creation, deformation/keyforms, clipping, physics tuning and runtime export. No placeholder .moc3 or misleading model3.json is supplied.'))
write(OUT/'VTube_Studio_Mapping.spec.json',dict(status='GUIDE_ONLY_NOT_VTUBE_JSON',convention='anatomical model L/R; verify mirror behavior in VTS calibration',mapping=[dict(source='FaceAngleX',target='ParamAngleX'),dict(source='FaceAngleY',target='ParamAngleY'),dict(source='FaceAngleZ',target='ParamAngleZ'),dict(source='EyeOpenLeft',target='ParamEyeLOpen'),dict(source='EyeOpenRight',target='ParamEyeROpen'),dict(source='EyeLeftX / EyeRightX (available tracker)',target='ParamEyeBallX'),dict(source='EyeLeftY / EyeRightY (available tracker)',target='ParamEyeBallY'),dict(source='MouthOpen or supported audio volume input',target='ParamMouthOpenY')],notes=['Pilih input yang tersedia pada perangkat/tracker VTS; kalibrasi nilai min/max.','MouthForm default 0 harus netral; jangan menaruh smile di idle default.','Volume audio bukan deteksi vokal; ParamMouthVowel memerlukan penggerak tambahan bila diperlukan.','VTS membuat konfigurasi vtube.json setelah model runtime asli dimuat.']))

known={p['id'] for p in params}
for f in EX.glob('*.json'):
    data=json.loads(f.read_text());assert all(p['Id'] in known for p in data['Parameters'])
for s in settings:
    assert all(x['Source']['Id'] in known for x in s['Input'])
    assert all(x['Destination']['Id'] in known for x in s['Output'])
print(json.dumps(dict(parameters=len(params),physics_settings=len(settings),expression_templates=len(recipes),motion_templates=2,all_referenced_parameters_declared=True)))
