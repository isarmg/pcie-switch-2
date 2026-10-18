from i_common import *
import sys
def esc(s):return str(s).replace('\\','\\\\').replace('"','\\"')
def fx(sz=1,just='',hide=False):return f'(effects (font (size {sz} {sz}))'+(f' (justify {just})' if just else '')+(' (hide yes)' if hide else '')+')'
def prop(n,s,x,y,hide=False):return f'(property "{n}" "{esc(s)}" (at {x} {y} 0) {fx(hide=hide)})'
def label(s,x,y,left):return f'(global_label "{esc(s)}" (shape passive) (at {x} {y} {180 if left else 0}) {fx(.8,"right" if left else "left")} (uuid "{uid()}"))'
def header(root,title,paper='A2'):return f'(kicad_sch (version 20250114) (generator "eeschema") (uuid "{root}") (paper "{paper}") (title_block (title "{esc(title)}") (date "2026-09-29") (rev "J") (comment 1 "Connectivity/layout draft; fictitious switch; provisional vertical M.2 lands"))'
def run(n):
    o=ROOT/n;bp=o/(n+'.kicad_pcb');pro=(o/(n+'.kicad_pro')).read_bytes();b=p.LoadBoard(str(bp));cs={c['ref']:c for c in json.loads((o/'COMPONENTS.json').read_text())};root=uid();blocks=[];defs={};instances={};rootitems=[];lib=[]
    fs=sorted(b.GetFootprints(),key=lambda f:(0 if f.GetReference()=='U1' and n.startswith('Main') else 1,f.GetReference()[0],int(re.search(r'\d+',f.GetReference())[0]) if re.search(r'\d+',f.GetReference()) else 0))
    for f in fs:
        ref=f.GetReference();pins={q.GetNumber():q.GetNetname() for q in f.Pads() if q.GetNumber()};items=list(pins.items());chunks=[items[i:i+60] for i in range(0,len(items),60)];key='PART_'+ref;defs[key]=[];pinpositions={};sid=uid()
        for un,chunk in enumerate(chunks,1):
            count=(len(chunk)+1)//2;half=max(3.81,count*1.27);d=[f'(symbol "{key}_{un}_1" (rectangle (start -12.7 {half}) (end 12.7 {-half}) (stroke (width .254) (type default)) (fill (type background)))'];coords={}
            for i,(pn,nn) in enumerate(chunk):
                left=i<count;x=-15.24 if left else 15.24;y=(count-1)*1.27-(i if left else i-count)*2.54;ang=0 if left else 180;pinname='~' if nn.startswith('unconnected-') else cs.get(ref,{}).get('pin_names',{}).get(pn,pn)
                d.append(f'(pin passive line (at {x} {y} {ang}) (length 2.54) (name "{esc(pinname)}" {fx(.8)}) (number "{pn}" {fx(.8)}))');coords[pn]=(x,y,left)
            defs[key].append(d[0]+'\n'+'\n'.join(d[1:])+')')
            blocks.append(dict(ref=ref,key=key,unit=un,uuid=uid(),foot=f,value=f.GetValue(),pins=chunk,coords=coords,half=half))
        body='\n'.join(defs[key]);fp='Local:'+str(f.GetFPID().GetLibItemName())
        d=f'(symbol "{key}" (pin_names (offset .5)) (in_bom yes) (on_board yes) '+prop('Reference',ref[0],0,0)+prop('Value',f.GetValue(),0,0)+prop('Footprint',fp,0,0,True)+f'\n{body})';defs[key]=d;lib.append(d)
        f.SetFPID(p.LIB_ID('Local',str(f.GetFPID().GetLibItemName())))
    # 12 blocks per A2 sheet; ports and BGA units naturally sort before passives.
    pages=[blocks[i:i+12] for i in range(0,len(blocks),12)]
    assigned=set()
    for page,entries in enumerate(pages,1):
        sheetid=uid();file=f'Connectivity_{page:02}.kicad_sch';childroot=uid();keys=list(dict.fromkeys(z['key'] for z in entries));cache='\n'.join(defs[k].replace(f'(symbol "{k}"',f'(symbol "Local:{k}"',1) for k in keys);parts=[header(childroot,f'{n} / Connectivity {page:02}'),'(lib_symbols '+cache+')'];path=f'/{root}/{sheetid}'
        for i,c in enumerate(entries):
            x=round((75+(i%4)*143)/1.27)*1.27;y=round((74+(i//4)*128)/1.27)*1.27;ref=c['ref'];fp='Local:'+str(c['foot'].GetFPID().GetLibItemName());un=c['unit'];s=c['uuid'];titley=y-c['half']-5
            parts.append(f'(symbol (lib_id "Local:{c["key"]}") (at {x} {y} 0) (unit {un}) (in_bom yes) (on_board yes) (dnp no) (uuid "{s}") '+prop('Reference',ref,x,titley)+prop('Value',c['value'],x,titley-3)+prop('Footprint',fp,x,y,True)+''.join(f'(pin "{pn}" (uuid "{uid()}"))' for pn,nn in c['pins'])+f'(instances (project "{n}" (path "{path}" (reference "{ref}") (unit {un})))))')
            for pn,nn in c['pins']:
                dx,dy,left=c['coords'][pn];px,py=x+dx,y-dy
                parts.append(f'(no_connect (at {px} {py}) (uuid "{uid()}"))' if not nn or nn.startswith('unconnected-') else label(nn,px,py,left))
            if ref not in assigned:
                pp=p.KIID_PATH()
                for z in [root,sheetid,s]:pp.push_back(p.KIID(z))
                c['foot'].SetPath(pp);assigned.add(ref)
        (o/file).write_text('\n'.join(parts)+'\n)',encoding='utf8')
        x=20+(page-1)%4*95;y=40+(page-1)//4*42
        rootitems.append(f'(sheet (at {x} {y}) (size 80 25) (fields_autoplaced) (stroke (width .15) (type default)) (fill (color 0 0 0 0)) (uuid "{sheetid}") '+prop('Sheetname',f'Connectivity {page:02}',x,y-2)+prop('Sheetfile',file,x,y+27)+f'(instances (project "{n}" (path "/{root}" (page "{page+1}")))))')
    text=f'(text "REV J: ROUTING / CONNECTIVITY DRAFT\\nPin types are passive: ERC checks connectivity syntax only, not switch logic or power sequencing.\\nSee README.md and VALIDATION.json before manufacturing." (at 20 15 0) {fx(1.2,"left")} (uuid "{uid()}"))'
    (o/(n+'.kicad_sch')).write_text(header(root,n,'A3')+'\n(lib_symbols)\n'+text+'\n'+'\n'.join(rootitems)+'\n)',encoding='utf8')
    (o/'Local.kicad_sym').write_text('(kicad_symbol_lib (version 20241209) (generator "kicad_symbol_editor")\n'+'\n'.join(lib)+'\n)',encoding='utf8');p.SaveBoard(str(bp),b);(o/(n+'.kicad_pro')).write_bytes(pro)
    print(n,len(pages),'sheets',len(fs),'parts',flush=True)
for n in sys.argv[1:] or ['Main_10E1S','Left_2M2_Vertical','Right_M2_Upstream']:run(n)
