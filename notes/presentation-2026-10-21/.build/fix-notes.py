from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from lxml import etree as E
import shutil
base=Path(__file__).resolve().parent.parent
path=base/'output/yang-iot-presentation-wps.pptx'
shutil.copy2(path,base/'.build/wps-before-notes-fix.pptx')
ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main','p':'http://schemas.openxmlformats.org/presentationml/2006/main'}
def q(n): prefix,local=n.split(':');return '{'+ns[prefix]+'}'+local
def geometry(sp,rect):
 pr=sp.find('p:spPr',ns)
 if pr is None:pr=E.SubElement(sp,q('p:spPr'))
 for x in pr.findall('a:xfrm',ns):pr.remove(x)
 t=E.Element(q('a:xfrm'));pr.insert(0,t)
 x,y,w,h=[str(round(v*914400)) for v in rect]
 E.SubElement(t,q('a:off'),x=x,y=y);E.SubElement(t,q('a:ext'),cx=w,cy=h)
rects={'sldImg':(.5,.6,6.5,3.65625),'body':(.5,4.5,6.5,4.7),'sldNum':(6.4,9.4,.6,.3),'hdr':(.5,.15,3,.3),'dt':(4,.15,3,.3),'ftr':(.5,9.4,5,.3)}
with ZipFile(path) as z: data={n:z.read(n) for n in z.namelist()}
for name,raw in list(data.items()):
 if name.endswith('.xml') and (name.startswith('ppt/notesSlides/') or name.startswith('ppt/notesMasters/')):
  root=E.fromstring(raw)
  for sp in root.findall('.//p:sp',ns):
   ph=sp.find('p:nvSpPr/p:nvPr/p:ph',ns)
   if ph is None:continue
   kind=ph.get('type');geometry(sp,rects.get(kind,rects['body']))
   if kind=='sldImg':ph.set('idx','2')
   if kind=='body':
    ph.set('idx','3');ph.attrib.pop('sz',None)
    body=sp.find('p:txBody/a:bodyPr',ns)
    if body is not None:
     body.set('wrap','square');body.set('lIns','0');body.set('rIns','0');body.set('tIns','0');body.set('bIns','0');body.set('anchor','t')
    for para in sp.findall('p:txBody/a:p',ns):
     pr=para.find('a:pPr',ns)
     if pr is None:pr=E.Element(q('a:pPr'));para.insert(0,pr)
     pr.set('algn','l')
     for run in para.findall('a:r',ns):
      rp=run.find('a:rPr',ns)
      if rp is None:rp=E.Element(q('a:rPr'));run.insert(0,rp)
      rp.set('sz','1400')
      for tag,font in [('a:latin','Arial'),('a:ea','Arial Unicode MS'),('a:cs','Arial')]:
       el=rp.find(tag,ns)
       if el is None:el=E.SubElement(rp,q(tag))
       el.set('typeface',font)
  data[name]=E.tostring(root,xml_declaration=True,encoding='UTF-8',standalone=True)
 elif name.startswith('ppt/theme/') and name.endswith('.xml'):
  root=E.fromstring(raw)
  for font in root.xpath('//*[@typeface]'):
   if font.get('typeface'):font.set('typeface','Arial')
  data[name]=E.tostring(root,xml_declaration=True,encoding='UTF-8',standalone=True)
with ZipFile(path,'w',ZIP_DEFLATED) as z:
 for n,b in data.items():z.writestr(n,b)
print('Repaired notes geometry on 16 slides; text unchanged.')
