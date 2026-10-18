_signal_hierarchy=ns['route']
_code=(STAGE/'scripts/revW/w_hierarchical.py').read_text(encoding='utf-8')
_code=_code.replace('def hierarchy(task):','def power_hierarchy(task):').replace("ns['route']=hierarchy",'')
_code=_code.replace('arr=fast_raster(obs,rad);G=',"obs.skip_endpoint_check=True;arr=fast_raster(obs,rad);narrow=fast_raster(obs,.05);G=")
_code=_code.replace('or arr[yy,xx]:continue','or narrow[yy,xx]:continue').replace('(arr[y,xx] or arr[yy,x])','(narrow[y,xx] or narrow[yy,x])')
_code=_code.replace('fast_clear(x,z,obs,rad-.000001)','fast_clear(x,z,obs,.05-.000001)')
_code=_code.replace('radius=math.ceil(stride/2)+1','radius=math.ceil(stride/2)')
_code=_code.replace('if len(prev)>120000','if len(prev)>1500000')
_code=_code.replace('coarse=inflated[::stride,::stride];labels,nlabels=ndimage.label(~coarse)',"sx,sy=(round(z/G) for z in start);ex,ey=(round(z/G) for z in end)\n narrowlabels,_=ndimage.label(~narrow);region=narrowlabels[sy,sx]\n if not region or region!=narrowlabels[ey,ex]:raise RuntimeError('narrow endpoint regions disconnected')\n coarse=inflated[::stride,::stride] | (narrowlabels[::stride,::stride]!=region);labels,nlabels=ndimage.label(~coarse)")
exec(compile(_code,'wide power with short narrow escapes','exec'),globals())
def mixed_hierarchy(task):
 return power_hierarchy(task) if task.get('kind')=='POWER_CONTROL' and task['width']>.15 else _signal_hierarchy(task)
ns['route']=mixed_hierarchy
