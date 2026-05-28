import zipfile, re, shutil, os, formulas, warnings, logging
from xml.sax.saxutils import escape
logging.getLogger('formulas').setLevel(logging.ERROR); warnings.filterwarnings('ignore')
SRC='/tmp/bess/Castellan_BESS_Model.xlsx'; FN='Castellan_BESS_Model.xlsx'
xl=formulas.ExcelModel().loads(SRC).finish(); sol=xl.calculate()
vals={}; pat=re.compile(r"^'\[%s\]([^']+)'!([A-Z]+\d+)$"%re.escape(FN))
for k,v in sol.items():
    m=pat.match(k)
    if not m: continue
    try: val=v.value[0,0]
    except Exception: val=getattr(v,'value',None)
    vals[(m.group(1).upper(),m.group(2))]=val
z=zipfile.ZipFile(SRC)
wbxml=z.read('xl/workbook.xml').decode(); rels=z.read('xl/_rels/workbook.xml.rels').decode()
rid2tgt={}
for rel in re.finditer(r'<Relationship\b[^>]*/?>',rels):
    s=rel.group(0)
    rid=re.search(r'Id="([^"]+)"',s); tgt=re.search(r'Target="([^"]+)"',s)
    if rid and tgt:
        t=tgt.group(1).lstrip('/')
        if not t.startswith('xl/'): t='xl/'+t
        rid2tgt[rid.group(1)]=t
name2file={}
for m in re.finditer(r'<sheet\b[^>]*/?>',wbxml):
    s=m.group(0); nm=re.search(r'name="([^"]+)"',s); rid=re.search(r'r:id="([^"]+)"',s)
    if nm and rid and rid.group(1) in rid2tgt:
        name2file[rid2tgt[rid.group(1)]]=nm.group(1).upper()
def num(x): return isinstance(x,(int,float)) and not isinstance(x,bool)
def inject(xml, sheetU):
    def repl(mc):
        c=mc.group(0)
        rm=re.search(r'\br="([A-Z]+\d+)"',c)
        if not rm or '<f' not in c: return c
        ref=rm.group(1)
        if (sheetU,ref) not in vals: return c
        val=vals[(sheetU,ref)]
        c2=re.sub(r'<v\s*/>|<v>.*?</v>','',c)
        c2=re.sub(r'\s+t="[^"]*"','',c2)
        if num(val):
            vstr=str(int(val)) if float(val).is_integer() else ('%.10g'%float(val))
            ins=f'<v>{vstr}</v>'
        else:
            c2=re.sub(r'^<c ','<c t="str" ',c2)
            ins=f'<v>{escape("" if val is None else str(val))}</v>'
        return c2.replace('</c>', ins+'</c>')
    return re.sub(r'<c\b[^>]*>.*?</c>', repl, xml)
tmp='/tmp/bess/_out.xlsx'
zin=zipfile.ZipFile(SRC,'r'); zout=zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED)
patched=0; ncells=0
for item in zin.infolist():
    data=zin.read(item.filename)
    if item.filename in name2file:
        xml=data.decode('utf-8'); xml2=inject(xml,name2file[item.filename])
        ncells+=xml2.count('<v>')-xml.count('<v>')
        data=xml2.encode('utf-8'); patched+=1
    zout.writestr(item,data)
zout.close(); zin.close(); shutil.move(tmp,SRC)
print(f"patched {patched} sheets, injected ~{ncells} cached values")
