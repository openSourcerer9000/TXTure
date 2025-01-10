from copy import copy
from funkshuns import *
from os import mkdir
#TODO wrap all with a dec that takes either lines or Path and returns the same to allow for either method
class Config:

    def __init__(self):
        self.suppressPrints = False

opts = Config()

prunt = copy(print)

def read(txtfile):
    """
    Read lines from a text file, returning a list of lines without newline characters. 
     
    :param txtfile: A Path object or string representing the file path. 
    :return: A list of strings, each representing a line from the file without '\\n' 
     
    .. note:: 
    speed read the whole geo (returns list of lines without \\n 's (newline chars)) 
     
    txtfile: Path obj or TODO str test this implementation 
    """
    # if isinstance(txtfile,PurePath):
    demlines = txtfile.read_text(errors='ignore').split('\n')
    # else:
    #     with open(txtfile, 'r+') as fh:
    #         demlines = fh.readlines() #speed read the whole geo (to list)
    return demlines

def print(*msgs):
    if not opts.suppressPrints:
        prunt(*msgs)

# def readstr(txtfile):
#     """
#     Read the contents of a text file and return it as a single string. 
     
#     :param txtfile: Path to the text file to be read. 
#     :type txtfile: str 
     
#     :return: The entire content of the file as a single string. 
#     :rtype: str 
#     .. note:: 
#     gulp as 1 str 
#     """
#     with open(txtfile, 'r+') as fh:
#         return fh.read()

def findKey(lines, key, how='startswith', startFrom=0, retrn='linenumber'):
    """
    Search for a keyword(s) in a list of lines. 
     
    :param lines: List of strings from a text file. 
    :param key: A string or list of strings to search for. 
    :param how: Method of comparison ('startswith', 'in', 'equals', 'regex', or '!!'). 
    :param startFrom: Index to start searching from in `lines`. 
    :param retrn: Specifies the return format ('linenumber', 'line', or 'both'). 
     
    :returns: 
    - If found, returns a dictionary with: 
        - 'linenumber': Index of the found line. 
        - 'line': Content of the found line. 
        - 'both': Tuple containing (linenumber, line). 
    - If not found, returns None. 
    .. note:: 
    returns line # in lines (list of strs) where keyword key is found 
     
    retrn: returns {'linenumber':Lnum,'line':lines[Lnum],'both':(Lnum,lines[Lnum])} 
    (key can be 1 str, or a list of strs, a list will search for each in sequence, 
    and stop once it finds the last key) 
     
    if an int is entered for key, it will just find that line number offset from startFrom 
     
    if how= "regex", keys should be as strs to re.compile r'Bla bla (\\s|-|\\.)?' 
     
    how= 'in' if key is in line 
     
    how='equals', if key IS the line exactly, 
     useful if searching ex 'Subbasin: key1' which could find 'Subbasin: key12' if 12 comes first 
     
    how = '!!' or '!!something' will add a not before the expression (line doesn't start with key) 
     
    returns None if key not found 
    """
    #--------init
    if type(key) == str:
        key = [key]
    elif type(key) == int:
        Lnum = startFrom + key
        retrnmap = {'linenumber': Lnum, 'line': lines[Lnum], 'both': (Lnum, lines[Lnum])}
        return retrnmap[retrn]
    k = 0
    lookin = 'line.startswith(key[k])'
    #endswith, etc
    nott = False
    if isinstance(how, str):
        if how.startswith('!!'):
            nott = True
            how = how[2:]
    if how in ['regex', 'regx']:
        lookin = 're.compile(key[k]).search(line) != None'
    elif how == 'in':
        lookin = 'key[k] in line'
    elif how == 'equals':
        lookin = 'key[k]==line'
    if nott:
        lookin = 'not ' + lookin
    for i, line in enumerate(lines[startFrom:]):
        if eval(lookin):
            k += 1
            if k == len(key):  #if we had been looking for the last key
                Lnum = i + startFrom
                break  #for loop
    else:
        print('WARNING: Key "' + key[k] + '" not found')
        return None
    retrnmap = {'linenumber': Lnum, 'line': lines[Lnum], 'both': (Lnum, lines[Lnum])}
    return retrnmap[retrn]

def findKeyR(lines, key, how='startswith', startFrom=0, retrn='linenumber'):
    """
    Search for a key in a list of lines from right to left. 
     
    :param lines: List of strings containing text lines. 
    :param key: String or list of strings to search for within the lines. 
    :param how: Method of matching ('startswith' or other) to apply to the key. 
    :param startFrom: Index to begin the search from (default is 0). 
    :param retrn: Specifies the return format ('linenumber', 'linecontent', or other). 
     
    :return: Index of the last occurrence of the key in lines (0-based). 
         Returns -1 if not found. 
    .. note:: 
    findkey but search right to left rather than left to right 
    """
    rpos = findKey(lines[::-1], key, how=how, startFrom=startFrom, retrn=retrn)
    pos = len(lines) - rpos - 1  #index at 0, subtract 1
    return pos

def getBlock(lines, startkey, endkey='same_as_start', **findKeyKwargs):
    """
    Retrieve the indices of a block of lines from a list based on specified start and end keys. 
     
    :param lines: A list of strings representing lines from a text file. 
    :param startkey: A string or list of strings indicating the starting search key. 
    :param endkey: A string or list of strings indicating the ending search key (default is 'same_as_start'). 
    :param findKeyKwargs: Additional keyword arguments for key search customization. 
     
    :return: A tuple of integers (from_index, to_index) where lines[from_index:to_index] selects the block. 
         The to_index is +1 of the last occurrence of the endkey line. 
    .. note:: 
    gets block of lines 
     
    returns (from,to) indices such that lines[from:to] selects the block 
     
    ie to is +1 of the endkey line 
     
    findKeyR endkey - this finds the LAST occurence of endkey 
    """
    if endkey == 'same_as_start':
        endkey = startkey
    i, o = (findKey(lines, startkey, **findKeyKwargs), findKeyR(lines, endkey, **findKeyKwargs) + 1)
    return (i, o)

def replaceBlock(linez, replaceWith, startkey, endkey='same_as_start', fromOffset=0, toOffset=0, **findKeyKwargs):
    """
    Replace a block of lines in the input list with specified lines. 
     
    :param linez: List of strings (lines) from a text file. 
    :param replaceWith: Lines to insert as a replacement (can be a list of strings). 
    :param startkey: Key string to locate the start of the block. 
    :param endkey: Key string to locate the end of the block (default is 'same_as_start'). 
    :param fromOffset: Offset to adjust the start index of replacement (default is 0). 
    :param toOffset: Offset to adjust the end index of replacement (default is 0). 
    :param **findKeyKwargs: Additional keyword arguments for finding keys. 
     
    :return: List of strings with the specified block replaced. 
    .. note:: 
    gets block of lines, then replaces it with replaceWith lines 
     
    (from,to) indices such that lines[from+fromOffset:to+toOffset] selects the block 
     
    ie to is +1 of the endkey line 
     
    """
    lines = linez[:]
    i, o = getBlock(lines, startkey, endkey, **findKeyKwargs)
    lines[i + fromOffset:o + toOffset] = asList(replaceWith)
    return lines

def getKeys(txtfile, keys, startFrom=0, trim=2, how='startswith'):
    """
        Retrieve lines from a text file based on specified keys. 
     
    :param txtfile: Path to the text file to read. 
    :type txtfile: str 
    :param keys: A single key (str) or a list of keys (str or list of str) to search for in the text lines. 
    :type keys: str | list[str] | list[list[str]] 
    :param startFrom: Index to start searching from in the text lines, defaults to 0. 
    :type startFrom: int, optional 
    :param trim: Specifies the trimming behavior: 
                 0 - full line including key, 
                 1 - line without the key, 
                 2 - line without the key, escaped newlines, and whitespace. 
    :type trim: int, optional 
    :param how: Method of key matching ('startswith' or other), defaults to 'startswith'. 
    :type how: str, optional 
     
    :return: A list of strings representing the lines that match the keys. 
    :rtype: list[str] 
     
    :note: If a single key is provided, access the line with getKeys()[0]. 
     
    .. note:: 
    keys list of keys 
     
    can be list of strs, list of (lists of strs), or 1 str 
     
    WARNING: right now a list of strs acts as multiple single-string keys, passing 1 list key should be [key] where key=['str','str2',...] TODO desired behavior? 
     
    WARNING: returns list of strs EVEN IF THERE'S JUST 1 ITEM! 
     
    USE getKeys()[0] if it's just 1 key 
     
    trim: {0:returns full line including key, 1:not including key, 
    2: 
    not including key + trim escape n and white space before and after each result, 
     
     
    """
    if isinstance(keys, str):
        keys = [keys]
        print('REMEMBER to use [0] if you are after a string and not a list with 1 str!!')
    lines = read(txtfile)
    res = [findKey(lines, key, how=how, startFrom=startFrom, retrn='line') for key in keys]
    if trim > 0:  #right split on final key
        res = [st.replace(asList(key)[-1], '', 1) if st else None for st, key in zip(res, keys)]
        # [i[len(key):] for st,key in zip(res,keys) if isinstance(st,str) else st]
    if trim == 2:
        res = [st.replace('\n', '').strip() if st else None for st in res]
    return res

def getKey(txtfile, key, **kwargz):
    """
    Retrieve a specific key from a text file. (Convenience method for singular txt.getKeys(...)[0].)
     
    :param txtfile: The path to the text file to be processed. 
    :type txtfile: str 
    :param key: A string or list of strings representing the key(s) to search for in the file. 
    :type key: str or list of str 
    :param kwargz: Additional keyword arguments for customization (e.g., trim behavior). 
    :returns: The value associated with the last occurrence of the key in the file. 
    :rtype: str 
    :raises: ValueError if the key is not found. 
    .. note:: 
    WARNING: right now a list of strs acts as multiple single-string keys, passing 1 list key should be [key] where key=['str','str2',...] TODO desired behavior? 
     
    trim: {0:returns full line including key, 1:not including key, 
    2: 
    not including key + trim escape n and white space before and after each result, 
     
     
    """
    return getKeys(txtfile, [key], **kwargz)[0]

def getKeysAll(txtfile, keys, startfrom=0, trim=2):
    """
        Retrieve all occurrences of specified keys from a text file. 
     
    :param txtfile: The text file to read from. 
    :type txtfile: str 
    :param keys: A single key or a list of keys to search for in the lines. 
    :type keys: str or list of str 
    :param startfrom: The line index to begin searching from, default is 0. 
    :type startfrom: int, optional 
    :param trim: The number of characters to trim from each found key occurrence, default is 2. 
    :type trim: int, optional 
    :return: A list of tuples, each containing the line index and the content 
             from the line where a key was found. 
    :rtype: list of tuples 
     
    .. note:: 
    TODO getKeys will only get the first instance of each key, this returns all 
    """
    assert False

def getSeq(lines, key, how='startswith', key2=None, how2=None, startFrom=0, retrn='seq', trim=2):
    """
    Retrieve a sequence of lines from a text file based on specified key matches. 
     
    :param lines: List of strings representing lines from a text file. 
    :param key: String or list of strings to search for. 
    :param how: Method of comparison for the key ('startswith' or custom). 
    :param key2: Optional second key to determine end of sequence. 
    :param how2: Optional comparison method for key2. 
    :param startFrom: Index to start searching from in the lines. 
    :param retrn: Specifies return type ('seq', 'bounds', or 'both'). 
    :param trim: Level of trimming on the returned sequence (0, 1, or 2). 
     
    :return: Depending on `retrn`, returns a list of strings, a tuple of bounds, or both. 
    .. note:: 
    findkey convenience method: 
     
    returns first sequence of lines starting from startFrom that all match key/how 
     
    retrn: {'seq':returns the sequence as list of strs,'bounds':tuple of bounds of seq, 
     
    'both':returns tuple of all 3 (['',''],13,16) } 
     
    if not how2, will either search until not how of key1, or until key2 if specified 
     
    key2 and how2 can also be specified explicitly 
     
    trim: {0:returns full line including key, 1:not including key, 
    2: 
    not including key + trim escape n and white space before and after each result} 
    """
    fromm = findKey(lines, key, how=how, startFrom=startFrom)
    if not fromm:
        return None
    if not how2:
        if key2:
            how2 = 'startswith'
        else:
            how2 = '!!' + how
    if not key2:
        key2 = key
    too = findKey(lines, key2, how=how2, startFrom=fromm)
    if not too:
        too = len(lines)
    seq = lines[fromm:too]
    if trim > 0:
        seq = [st[len(key):] if st else None for st in seq]
    if trim == 2:
        seq = [st.replace('\n', '').rstrip() if st else None for st in seq]
    if retrn == 'seq':
        res = seq
    elif retrn == 'both':
        res = (seq, fromm, too)
    else:
        return (fromm, too)
    return res

def insertLines(lines, addlnes, key, how='startswith', newLine=False, insrt=1, lethal=False):
    """
    Insert lines into a specified position within a list of lines. 
     
    :param lines: List of strings representing lines from a text file. 
    :param addlnes: List of strings to be inserted. 
    :param key: String or list of strings indicating the position for insertion. 
             If an integer is provided, it specifies the line index. 
    :param how: Method to match the key ('startswith' by default). 
    :param newLine: If True, adds a newline after the inserted lines. 
    :param insrt: Integer indicating position adjustment (0: before, 1: after, 2: after + 1 line). 
    :param lethal: If True, raises an assertion error on failure. 
     
    :return: Updated list of lines with the new lines inserted. 
    .. note:: 
    TODO inplace= 
     
    geo = PATH object of .g0x file 
     
    addlnes = ['line1','line2',...] to insert 
     
    key = keyword to insert 
     
    (key can be 1 str, or a list of strs, a list will search for each in sequence, 
    and stop once it finds the last key) 
     
    if an integer is entered for key, it will just insert at that line number + insrt 
     
    insrt = 0:before, 1:after 2:after + 1 line, can be any int (within len(lines)) 
     
    #if newline, treats lines as having newline escapes between each line, this is the format that comes from fh.readlines() 
     
    # TODO is this true? not ['line1 
    ','line2 
    '] 
    """
    # if isinstance(addlnes,str):
    #     addlnes = [addlnes]
    # if type(key) == int:
    #     Lnum = key + insrt
    # else:
    Lnum = findKey(lines, key, how)
    if Lnum:
        Lnum += insrt
    else:
        print('ERROR: lines ' + str(addlnes) + ' not inserted')
        if lethal:
            assert False
        return lines
    # print(lines[Lnum])
    if newLine:
        Lnum += 1
        addlnes = listJoin(addlnes)
        addlnes.append('\n')
    # print('lnum',Lnum)
    lines[Lnum:Lnum] = addlnes
    return lines

def removeLines(lines, key1, key2=1, how1='startswith', how2='startswith', rem=0, newLine=False):
    """
    Remove lines from a list based on specified key indicators. 
     
    :param lines: List of strings representing lines from a text file. 
    :param key1: String or list of strings indicating where to start removal. 
    :param key2: String or integer indicating the end of removal (default is 1 line after key1). 
    :param how1: Method to match key1 (default is 'startswith'). 
    :param how2: Method to match key2 (default is 'startswith'). 
    :param rem: Offset to apply to key indices (default is 0). 
    :param newLine: Unused; raises an assertion error if set to True. 
     
    :returns: Tuple of (updated lines, index of the first removed line). 
    :raises AssertionError: If key indices are invalid or if no lines are removed. 
    .. note:: 
    removes the lines in a list of lines from [key1 + rem:key2 + rem] 
     
    returns (lines after removal,line # that was removed) 
     
    if type(key2)==integer rem key2 lines total 
     
    rem: offset of key 
     
    ex (replace): 
     
    lines,Lnum = removeLines(lines,'this line starts with this') 
     
    lines[Lnum:Lnum]=['addline1','addline2'] 
     
    unused??: if newline, treats lines as having newline escapes between each line, this is the format that comes from fh.readlines() 
    """
    if newLine:
        assert False, 'removeLines has no case newLine, TODO'
    fromm = findKey(lines, key1, how1)
    if fromm is None:
        print(f'{fromm}No lines removed')
        return None
    else:
        fromm += rem
    if type(key2) == str:
        too = findKey(lines, key2, how2, startFrom=fromm + 1) + rem
    elif type(key2) == int:
        too = fromm + key2
    assert too > fromm
    tst = len(lines)
    del lines[fromm:too]
    try:
        assert tst > len(lines)
    except:
        print(f'WARNING: no lines removed between {key1} and {key2}')
    return (lines, fromm)

def replaceLines(lines, addLines, key1, key2=1, how1='startswith', how2='startswith', rem=0, newLine=False):
    """
    Replace specified lines in a list of text lines. 
     
    :param lines: List of strings representing lines in a text file. 
    :param addLines: Lines to be added in place of the removed lines. 
    :param key1: Starting index or key to identify the range for removal. 
    :param key2: Ending index or key (default is 1) for the removal range. 
    :param how1: Method to match the first key (default is 'startswith'). 
    :param how2: Method to match the second key (default is 'startswith'). 
    :param rem: Offset to adjust the starting index for removal (default is 0). 
    :param newLine: Flag to indicate if the addition should respect line breaks (default is False). 
     
    :return: Tuple of updated lines and the line number of the first removal. 
    .. note:: 
    TODO update all remove/insert operations to use this, no BS 
     
    removes the lines in a list of lines from [key1 + rem:key2 + rem] 
     
    returns (lines after removal,line # that was removed) 
     
    if type(key2)==integer rem key2 lines total 
     
    rem: offset of key 
     
     
    returns lines (TODO inplace?) 
    """
    lines, Lnum = removeLines(lines, key1, key2=key2, how1=how1, how2=how2, newLine=newLine)  #TODO clean this up with args kwargs?
    lines[Lnum:Lnum] = asList(addLines)
    return lines

def write(txtfile, lines, addNewLines=True, backup=False):
    """
    Overwrite or create a text file with specified lines. 
     
    :param txtfile: The path object of the text file to be written. 
    :type txtfile: pathlib.Path 
    :param lines: Lines of text to write, either as a list of strings or a single string. 
    :type lines: list[str] or str 
    :param addNewLines: If True, add newlines between lines (ignored if lines is a string). 
    :type addNewLines: bool, optional 
    :param backup: If True, create a backup of the file before writing. 
    :type backup: bool, optional 
     
    :returns: None 
    .. note:: 
    overwrites/creates and writes the txtfile: PATH object of text file 
    """  #,writefrom=0):
    'overwrites/creates and writes the txtfile: PATH object of text file\n'
    #writefrom: position to start overwriting from'''
    if backup:
        fileBackup(txtfile)
    #don't add newlines if lines is a string
    sep = '\n' if addNewLines and (not isinstance(lines, str)) else ''
    txtfile.write_text(sep.join(lines))

def setKeys(txtfile, keyz, startFrom=0, how='startswith', backup=False, lethalFail=True):
    """
    Replace keys in a text file with specified values or function outputs. 
     
    :param txtfile: Path to the text file to be modified. 
    :param keyz: List of tuples or dictionary mapping keys to replacement values/functions. 
             Example: [(key1, 'replacewith1'), (['key2a', 'key2b'], 'replacewith2')] 
    :param startFrom: Index to start processing lines (default is 0). 
    :param how: Method of key matching ('startswith', etc.) (default is 'startswith'). 
    :param backup: If True, create a backup of the original file before modification (default is False). 
    :param lethalFail: If True, raise exceptions on failures; otherwise, print warnings (default is True). 
     
    :raises Exception: Raises exceptions based on lethalFail setting. 
    .. note:: 
    keyz = [ 
     
    (key1,'replacewith1'), 
     
    (['key2a','key2b']:'replacewith2'), 
     
    ] 
     
    the dict values can also be functions (or a mix of the two, {key1:'str',key2:myFunc}), 
     
    in which case the OG key will be replaced with the output of func(OG key) 
     
    suff is the suffix to append the keys with, this will likely be a newline character (default) 
     
    USE suff='' not suff=None 
     
    the entire line will be replaced with keyi+replacewithi+suff 
    """
    lines = read(txtfile)
    if isinstance(keyz, dict):
        keylist = list(keyz.items())  # list of tuples
    else:
        keylist = keyz
    for key, val in keylist:
        try:
            if hasattr(val, '__call__'):  #is func
                OGkey = getKeys(txtfile, [key], how=how, trim=1)[0]
                addLine = f'{key}{val(OGkey)}'
            else:  #key is a str or list, not a func
                addLine = f'{asList(key)[-1]}{val}'
            # try:
            lines, Lnum = removeLines(lines, key, key2=1, how1=how)
            # except:
            #     print(f'WARNING: {txtfile} not written- setKeys operation failed')
            #     return None
            lines[Lnum:Lnum] = [addLine]
        except Exception as e:
            if lethalFail:
                raise e
            else:
                print(f'WARNING: {e}')
    write(txtfile, lines, True, backup)

def setOrInsertKey(txtfile, keydict, afterKey, linesAfter=1, **setKeysKwargs):
    """
    Set or insert a key-value pair in a text file. 
     
    :param txtfile: Path to the text file to be modified. 
    :type txtfile: str 
    :param keydict: Dictionary containing a single key-value pair to insert or set. 
    :type keydict: dict 
    :param afterKey: Key after which the new key-value pair will be inserted. 
    :type afterKey: str 
    :param linesAfter: Number of lines after afterKey to insert the new key-value pair (default is 1). 
    :type linesAfter: int 
    :param setKeysKwargs: Additional keyword arguments for setting keys. 
     
    :raises AssertionError: If key or value in keydict is not a string, or if afterKey is not found in the text file. 
    .. note:: 
    setKey (single), expect: create key after afterKey 
     
    keydict: {'key1':'replacewith1'}, only accepts strs for key and replacewith 
     
    change linesAfter to insert before for example (0), after the line after afterKey (2) etc 
    """
    key, val = list(keydict.items())[0]
    try:
        setKeys(txtfile, keydict, **setKeysKwargs)
    except:  # key doesnt exist
        assert isinstance(key, str) and isinstance(val, str), f'Both {key} and {val} should be strs'
        lines = read(txtfile)
        b4 = findKey(lines, afterKey) + linesAfter
        assert b4, f'ERROR: {afterKey} not found in {txtfile}'
        lines[b4:b4] = [key + val]
        write(txtfile, lines)
    assert getKeys(txtfile, key, trim=1)[0] == val

def setSeq(txtfile, newSeq, key, how='startswith', key2=None, how2=None, startFrom=0, backup=False, suff=''):
    """
    Set a new sequence of lines in a specified text file. 
     
    :param txtfile: Path to the text file to modify. 
    :type txtfile: str 
    :param newSeq: List of new lines to insert. 
    :type newSeq: list of str 
    :param key: Key or list of keys to identify the sequence. 
    :type key: str or list of str 
    :param how: Method to match the key (default is 'startswith'). 
    :type how: str 
    :param key2: Optional second key for additional filtering. 
    :type key2: str or None 
    :param how2: Optional method for the second key. 
    :type how2: str or None 
    :param startFrom: Starting index for searching (default is 0). 
    :type startFrom: int 
    :param backup: Flag to create a backup of the original file (default is False). 
    :type backup: bool 
    :param suff: Suffix to append to each new line (default is ''). 
    :type suff: str 
     
    :returns: None 
    .. note:: 
    just one seq 
    """
    if backup:
        fileBackup(txtfile)
    newseqfull = [f'{key}{s}{suff}' for s in newSeq]
    lines = read(txtfile)
    bounds = getSeq(lines, key, how, key2, how2, startFrom, retrn='bounds')
    del lines[bounds[0]:bounds[1]]
    insertLines(lines, newseqfull, bounds[0] - 1, newLine=False)
    write(txtfile, lines, backup=backup)

def equal(txtfiles):
    """
    Compare the contents of multiple text files for equality. 
     
    :param txtfiles: A list of paths to text files to compare. 
    :type txtfiles: list of str 
    :return: True if all files have identical content, False otherwise. 
    :rtype: bool 
     
    :raises ValueError: If no text files are provided. 
    .. note:: 
    for testing, 
    ex: 
     
    assert equal([pth/'1.txt',pth/'2.txt']) 
    """
    lnes = [read(file) for file in txtfiles]
    if len(lnes) < 0:
        res = True
    res = all((ele == lnes[0] for ele in lnes))
    return res

def replaceAll(txtfile, dictFindReplace, backup=True, return_lines=False):
    """
    Replace specified substrings in a text file with given replacements. 
     
    :param txtfile: Path to the text file to be processed. 
    :type txtfile: str 
    :param dictFindReplace: Mapping of substrings to be replaced and their replacements. 
    :type dictFindReplace: dict 
    :param backup: Flag indicating whether to create a backup of the original file. 
    :type backup: bool, optional 
    :param return_lines: If True, return the modified lines instead of writing to the file. 
    :type return_lines: bool, optional 
    :return: List of modified lines if return_lines is True; otherwise, None. 
    :rtype: list or None 
    .. note:: 
    {'find1':'replace1','find2':'replace2'} (in one pass) for each line in txtfile, writes OG 
     
    if return_lines: 
    return lines 
    """
    lines = read(txtfile)
    lines = [replaceMulti(dictFindReplace, line) for line in lines]
    # for fnd,rep in dictFindReplace.items():
    #     lines = [line.replace(fnd,rep) for line in lines]
    write(txtfile, lines, backup=backup)
    if return_lines:
        return lines

class meta():

    def functionize(file=Path(r'C:\Users\seanm\Documents\temp')/"Untitled-1.py" ,iniCells=3,argCell=2,src='vscode'):
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

    def rmdToR(rmd):
        '''converts rmd notebook to r script, with the same name, in the same dir'''
        rscript = rmd.parent/f'{rmd.stem}.R'
        if rscript.exists():
            fileBackup(rscript)
        r = pd.Series(rmd.read_text().split('\n'))
        r
        starts = r[r=='```{r}'].index + 1
        r[starts]
        stops = r[r=='```'].index
        stops
        tups = list(zip(starts,stops))
        tups
        slices = [slice(start,stop) for start,stop in tups]
        slices
        script = [ r[slce].to_list() for slce in slices ]
        script
        script = flattenList(script)
        script
        txt.write(rscript,script)

    def themeMe(themeStem='fonkay',themeDir=Path(r'C:\Users\seanm\Downloads'),
        prjpth='cwd',
        basetheme = "Monokai" ):
        '''
        themejson = themeDir/f'{themeStem}-color-theme.json'
        Puts a themejson created at https://themes.vscode.one/ into your
        .vscode/settings.json
        WARNING overwrites settings TODO'''
        if prjpth=='cwd':
            prjpth=Path.cwd()
        themejson = themeDir/f'{themeStem}-color-theme.json'

        with open(themejson, 'r') as fh:
            jj=json.load(fh)
        
        j = copy(jj)
        j.pop('colors')
        
        settingz = {
            "workbench.colorCustomizations": {
                f'[{basetheme}]': jj['colors']
            },
            **j
            ,
            "workbench.colorTheme": basetheme
        }
        
        settingsjson = prjpth/'.vscode'/'settings.json'
        (settingsjson.parent).mkdir(parents=True,exist_ok=True)
        
        fileBackup(settingsjson)
        if settingsjson.exists():
            settingsjson.unlink()
        with open(settingsjson, 'w') as outfile:
            json.dump(settingz, outfile,indent=4)
        
        return settingsjson

    ipyToHTML = htmler.ipyToHTML