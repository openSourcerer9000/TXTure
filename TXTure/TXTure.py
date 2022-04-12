from funkshuns import *

def read(txtfile):
    '''speed read the whole geo (returns list of lines without \\n 's (newline chars))\n
    txtfile: Path obj or TODO str test this implementation\n'''
    # if isinstance(txtfile,PurePath):
    demlines = txtfile.read_text().split('\n')
    # else:
    #     with open(txtfile, 'r+') as fh:
    #         demlines = fh.readlines() #speed read the whole geo (to list)
    return demlines
def readstr(txtfile):
    '''gulp as 1 str'''
    with open(txtfile, 'r+') as fh:
        return fh.read()
def findKey(lines,key,how = 'startswith',startFrom = 0,retrn='linenumber'):
    '''returns line # in lines (list of strs) where keyword key is found\n
    retrn: returns {'linenumber':Lnum,'line':lines[Lnum],'both':(Lnum,lines[Lnum])}
    (key can be 1 str, or a list of strs, a list will search for each in sequence, 
    and stop once it finds the last key) \n
    if an int is entered for key, it will just find that line number offset from startFrom\n
    if how= "regex", keys should be as strs to re.compile r'Bla bla (\s|-|\.)?'    \n
    how= 'in' if key is in line\n
    how = '!!' or '!!something' will add a not before the expression (line doesn't start with key)\n
    returns None if key not found'''
    #--------init
    if type(key) == str:
        key = [key]
    elif type(key) == int:
        Lnum = startFrom + key
        retrnmap = {'linenumber':Lnum,'line':lines[Lnum],'both':(Lnum,lines[Lnum])}
        return retrnmap[retrn]
    k = 0
    lookin = r'line.startswith(key[k])'
    #endswith, etc
    nott = False
    if isinstance(how,str):
        if how.startswith('!!'):
            nott = True
            how = how[2:]
    if how in ['regex','regx']:
        lookin = r're.compile(key[k]).search(line) != None'
    elif how == 'in':
        lookin = r'key[k] in line'
    if nott:
        lookin = r'not ' + lookin

    for i,line in enumerate(lines[startFrom:]):
        if eval(lookin):
            k += 1
            if k == len(key): #if we had been looking for the last key
                Lnum = i + startFrom
                break #for loop
    else:
        print('WARNING: Key "' + key[k] + '" not found')
        return None
    retrnmap = {'linenumber':Lnum,'line':lines[Lnum],'both':(Lnum,lines[Lnum])}
    return retrnmap[retrn]
    # if retrn =='linenumber':
    #     return Lnum
    # elif retrn == 'both':
    #     return (Lnum,lines[Lnum])
    # else:
    #     return lines[Lnum]
def getKeys(txtfile,keys,startFrom = 0,trim=2,how='startswith'):
    '''keys list of keys\n
    can be list of strs, list of (lists of strs), or 1 str \n
    WARNING: right now a list of strs acts as multiple single-string keys, passing 1 list key should be [key] where key=['str','str2',...] TODO desired behavior?\n
    WARNING: returns list of strs EVEN IF THERE'S JUST 1 ITEM!\n
    USE getKeys()[0] if it's just 1 key\n
    trim: {0:returns full line including key, 1:not including key,\n2:
    not including key + trim escape n and white space before and after each result,\n
    1.5:not including key + trim escape n BUT NOT WHITESPACE- TODO untested, unused 111820}
    '''
    if isinstance(keys,str):
        keys = [keys]
        print('REMEMBER to use [0] if you are after a string and not a list with 1 str!!')
    lines = read(txtfile)
    res = [findKey(lines,key,how=how,startFrom=startFrom,retrn='line') for key in keys]
    if trim>0:
        res = [st[len(key):] if st else None for st,key in zip(res,keys)]
        # [i[len(key):] for st,key in zip(res,keys) if isinstance(st,str) else st]
    if trim>1:
        res = [st.replace('\n','') if st else None for st in res]
    if trim==2:
        res = [st.rstrip() if st else None for st in res]
    return res
def getKeysAll(txtfile,keys,startfrom=0,trim=2):
    '''TODO getKeys will only get the first instance of each key, this returns all'''
    assert False
    
def getSeq(lines,key,how = 'startswith',key2=None,how2=None,startFrom = 0,retrn='seq',trim=2):
    '''findkey convenience method:\n
    returns first sequence of lines starting from startFrom that all match key/how\n
    retrn: {'seq':returns the sequence as list of strs,'bounds':tuple of bounds of seq,\n
    'both':returns tuple of all 3 (['',''],13,16) }\n
    if not how2, will either search until not how of key1, or until key2 if specified\n
    key2 and how2 can also be specified explicitly\n
    trim: {0:returns full line including key, 1:not including key,\n2:
    not including key + trim escape n and white space before and after each result}'''
    fromm = findKey(lines,key,how=how,startFrom=startFrom)
    if not fromm:
        return None
    if not how2:
        if key2:
            how2='startswith'
        else:
            how2 = '!!'+how
    if not key2:
        key2 = key
    too = findKey(lines,key2,how=how2,startFrom=fromm)
    if not too:
        too = len(lines)
    seq = lines[fromm:too]
    if trim>0:
        seq = [st[len(key):] if st else None for st in seq]
    if trim==2:
        seq = [st.replace('\n','').rstrip() if st else None for st in seq]
    if retrn == 'seq':
        res = seq
    elif retrn == 'both':
        res = (seq,fromm,too)
    else:
        return (fromm,too)
    return res
def insertLines(lines,addlnes,key,how ='startswith', newLine=False, insrt = 1,lethal=False):
    """TODO inplace=\n
    geo = PATH object of .g0x file \n
    addlnes = ['line1','line2',...] to insert \n
    key = keyword to insert \n
    (key can be 1 str, or a list of strs, a list will search for each in sequence, 
    and stop once it finds the last key) \n
    if an integer is entered for key, it will just insert at that line number + insrt\n
    insrt = 0:before, 1:after 2:after + 1 line, can be any int (within len(lines)) \n
    #if newline, treats lines as having newline escapes between each line, this is the format that comes from fh.readlines()\n
    # TODO is this true? not ['line1\n','line2\n']"""
    # if isinstance(addlnes,str):
    #     addlnes = [addlnes]
    # if type(key) == int:
    #     Lnum = key + insrt
    # else:
    Lnum = findKey(lines,key,how)
    if Lnum:
        Lnum += insrt
    else:
        print('ERROR: lines '+str(addlnes)+' not inserted')
        if lethal:
            assert False
        return lines
    # print(lines[Lnum])
    if newLine:
        Lnum += 1
        addlnes=listJoin(addlnes)
        addlnes.append('\n')
    # print('lnum',Lnum)
    lines[Lnum:Lnum]=addlnes
    return lines
def removeLines(lines,key1,key2=1,how1 ='startswith',how2 ='startswith',rem = 0,newLine=False):
    '''removes the lines in a list of lines from [key1 + rem:key2 + rem]\n
    returns (lines after removal,line # that was removed)\n
    if type(key2)==integer rem key2 lines total\n
    rem: offset of key\n
    ex (replace):\n
    lines,Lnum = removeLines(lines,'this line starts with this')\n
    lines[Lnum:Lnum]=['addline1','addline2']\n
    unused??: if newline, treats lines as having newline escapes between each line, this is the format that comes from fh.readlines()\n'''
    if newLine:
        assert False, 'removeLines has no case newLine, TODO'
    fromm = findKey(lines,key1,how1) 
    if fromm is None:
        print(f'{fromm}No lines removed')
        return None
    else:
        fromm += rem
    if type(key2)==str:
        too = findKey(lines,key2,how2,startFrom = fromm+1) + rem
    elif type(key2)==int:
        too = fromm+key2
    assert too > fromm
    tst = len(lines)
    del lines[fromm:too]
    try:
        assert tst > len(lines)
    except:
        print(f'WARNING: no lines removed between {key1} and {key2}')
    return (lines,fromm)
def replaceLines(lines,addLines,key1,key2=1,how1 ='startswith',how2 ='startswith',rem=0,newLine=False):
    '''TODO update all remove/insert operations to use this, no BS\n
    removes the lines in a list of lines from [key1 + rem:key2 + rem]\n
    returns (lines after removal,line # that was removed)\n
    if type(key2)==integer rem key2 lines total\n
    rem: offset of key\n

    returns lines (TODO inplace?)
    '''
    lines,Lnum = removeLines(lines,key1,key2=key2,how1=how1,how2=how2,newLine=newLine) #TODO clean this up with args kwargs?
    lines[Lnum:Lnum]=addLines
    return lines
def write(txtfile,lines,addNewLines=True,backup=False):#,writefrom=0):
    '''overwrites/creates and writes the txtfile: PATH object of text file\n'''
    #writefrom: position to start overwriting from'''
    if backup:
        fileBackup(txtfile)
    sep = '\n' if addNewLines else ''
    txtfile.write_text(sep.join(lines))

    # with open(txtfile, 'r+') as fh:
    #     fh.truncate(writefrom)
    #     fh.seek(writefrom)
    #     fh.writelines(lines)
def setKeys(txtfile,keyz,startFrom = 0,suff='\n',how='startswith',backup=False):
    '''keyz: {key1:'replacewith1',key2:...}\n
    the dict values can also be functions (or a mix of the two, {key1:'str',key2:myFunc}), \n
    in which case the OG key will be replaced with the output of func(OG key)\n
    suff is the suffix to append the keys with, this will likely be a newline character (default)\n
    USE suff='' not suff=None\n
    the entire line will be replaced with keyi+replacewithi+suff\n'''
    lines = read(txtfile)
    for key in list(keyz.keys()):
        if hasattr(keyz[key], '__call__'): #is func
            OGkey=getKeys(txtfile,[key],how=how,trim=1)[0]
            OGkey = OGkey.rstrip(suff)
            addLine = f'{key}{keyz[key](OGkey)}{suff}'
        else:
            addLine = f'{key}{keyz[key]}{suff}'
        try:
            lines,Lnum=removeLines(lines,key,key2=1,how1=how)
        except:
            print(f'WARNING: {txtfile} not written- setKeys operation failed')
            return None
        lines[Lnum:Lnum] = addLine

    write(txtfile,lines,True,backup)
def setSeq(txtfile,newSeq,key,how = 'startswith',key2=None,how2=None,startFrom = 0,backup=False,newLine=True):
    '''just one seq'''
    if backup:
        fileBackup(txtfile)
    if newLine:
        suff = '\n' 
    else: 
        suff = ''
    newseqfull = [f'{key}{s}{suff}' for s in newSeq]
    lines = read(txtfile)
    bounds = getSeq(lines,key,how,key2,how2,startFrom,retrn='bounds')
    del lines[bounds[0]:bounds[1]]
    insertLines(lines,newseqfull,bounds[0],newLine=False)
    write(txtfile,lines,False,backup)
def equal(txtfiles):
    '''for testing, 
    ex:\n
    assert equal([pth/'1.txt',pth/'2.txt'])'''
    lnes = [read(file) for file in txtfiles]
    if len(lnes) < 0 : 
        res = True
    res = all(ele == lnes[0] for ele in lnes)
    return res
def replaceAll(txtfile,dictFindReplace,backup=True,return_lines=False):
    '''{'find1':'replace1','find2':'replace2'} (in one pass) for each line in txtfile, writes OG\n
    if return_lines:
        return lines
    '''
    lines = read(txtfile)
    lines = [replaceMulti(dictFindReplace,line) for line in lines]
    # for fnd,rep in dictFindReplace.items():
    #     lines = [line.replace(fnd,rep) for line in lines]
    write(txtfile,lines,False,backup)
    if return_lines:
        return lines


class meta():
    '''metaprogramming utils'''
    def functionize(file=Path(r'C:\Users\seanm\Desktop\temp')/"Untitled-1.py" ,iniCells=3,argCell=2,src='vscode'):
        '''Functionizes a .ipynb Exported as executable script (.py)\n
        iniCells: how many code cells before the function begins\n
        argCell: which cell to pull args from'''
        key = '# %%' if src=='vscode' else '# In['
        tabb = ' '*4
        def deJpy(lines):
            '''cleans the jupyter out of Exported as executable scripts (.py)'''
            p = [line for line in lines if not line.startswith(key)]
            wspace = []
            for i in range(len(p)):
                if not p[i-1:i+1]==['','']:
                    wspace += [ p[i] ]
            return wspace
        # p = file.read_text().split('\n')
        lines = read(file)
        lines[6:11]
        
        funkstart = findKey(lines,[key]*(iniCells+1))+1
        ini,funk = lines[:funkstart],lines[funkstart:]
        ini
        
        #del extra whitespace
        funk = funk[findKey(funk,r'\w+',how='regex'):]
        funk[:5]
        
        ini,funk = [deJpy(lnes) for lnes in (ini,funk)]
        ini
        
        #TODO convention for this? Just big bold docstrings?
        found = findKey(lines,'#  # ')
        if found:
            docstring = "'''" + lines[found].replace('#  # ','') + "'''"
        else:
            docstring = "''''''"
        print(docstring)
        
        argstart = findKey(lines,[key]*(argCell-1))+1
        lines[argstart:]
        
        argz = [i for i in ini if i.find('=')>-1]
        argz
        
        argz = [a.split('=')[0] for a in argz]
        argz
        
        splitit = lambda argz: [[a for a in arg.split(' ') if len(a)>0][0] for arg in argz]
        assert splitit(['arg1 ', 'arg2','   arg3']) == ['arg1', 'arg2','arg3']
        argz = splitit(argz)
        argz
        
        funk = [f'{tabb}{line}' for line in funk]
        funk[-5:]
        
        funknmer = lambda filestem: filestem.split('_')[-1].split(' ')[0]
        assert funknmer('w_PC_funk (6)')=='funk'
        assert funknmer('w_PC_funk')=='funk'
        funknm = funknmer(file.stem)
        funknm
        
        deff = f"def {funknm}({','.join(argz)}):"
        deff
        
        res = ini+[deff]+[tabb+docstring]+funk+[f'{tabb}return ']
        res
        
        file.write_text('\n'.join(res))
        print(f'{file} has been functionized')