from jinja2 import FileSystemBytecodeCache
import pytest
# from contextlib import contextmanager

from TXTure import TXTure as txt
from funkshuns import *
from pytest import approx
import pandas as pd
import numpy as np
from pathlib import PurePath,Path
import os
import shutil
from statistics import mean
import math

#TODO fresh(x) @
#https://www.youtube.com/watch?v=2R1HELARjUk&feature=youtu.be
# many_triangles = [
#     (90, 60, 30, "right"),
#     (100, 40, 40, "obtuse"),
#     (60, 60, 60, "acute"),
#     (0, 0, 0, "invalid")
# ]

# @pytest.mark.s('a, b, c, expected', many_triangles)
# def test_func(a, b, c, expected):
#     assert triangle_type(a, b, c) == expected

#TODO organize into classes
#TODO split into separate files where long run tests can be run separate

mc = Path(os.path.dirname(os.path.abspath(__file__)))/'mockdata'
bkdir = mc/'fileBackup'
class mockstuff:
    def fresh(self,file):
        '''creates and returns the copy of the backup file\n
        the og does not have a _tst prefix
        '''
        freshest = file.parent/(file.stem+'_tst'+file.suffix)
        shutil.copy(file,freshest)
        return freshest
    def __init__(self):
            self.seq = ['Geom File=g03\n', 'Geom File=g04\n', 'Geom File=g05\n', 'Geom File=g02\n', 'Geom File=g09\n', 'Geom File=g08\n', 'Geom File=g11\n', 'Unsteady File=u01\n', 'Unsteady File=u02\n', 'Unsteady File=u03\n', 'Unsteady File=u04\n', 'Plan File=p02\n', 'Plan File=p08\n', 'Plan File=p09\n', 'Plan File=p03\n', 'Plan File=p07\n', 'Plan File=p04\n', 'Plan File=p10\n', 'Plan File=p11\n', 'Plan File=p12\n', 'Plan File=p13\n', 'Plan File=p14\n', 'Plan File=p15\n', 'Plan File=p16\n', 'Plan File=p17\n', 'Plan File=p18\n', 'Plan File=p19\n', 'Background Map Layer=culs\n']
            self.lines = ['Hello there','Nice to meet you','My name is','Goodbye']
            self.geo = mc/'geo.g01'
            self.msg = mc/'msg.txt'
            self.prj = mc/'proj.prj'
            self.p01,self.p02 = [ mc/f'proj.{p}' for p in ('p01','p02') ]
x=mockstuff()

# def test_2txts_are_equal():
#     '''not a unit test, just using the function with pytest comparison'''
#     pth = Path(r'C:\Users\sean.micek\Desktop\Galv\DickinsonBayouModeling09.08.2020\HEC-RAS')
#     assert txt.equal([pth/'Dickinson_Bayou.u05',pth/'Dickinson_Bayou - Copy.u05'])
def test_x():
    print(x.msg)
    assert x.lines == ['Hello there','Nice to meet you','My name is','Goodbye']
def test_xfresh():
    msg=x.fresh(x.msg)
    assert msg.exists()

#TODO txt.read returns 'line1\n','line2\n' how does this not screw things up? ('line1','\n','line2' ever?) 
# def test_myfilesequal():
#     pthRAS = Path(r'J:\H&H Division Files\WalnutCreek\Walnut Creek\Walnut Creek HEC-RAS')
#     pthWal = Path(r'J:\H&H Division Files\WalnutCreek\Walnut Creek\Walnut Creek')
#     assert txt.equal([pthRAS/'WCTRAIL.g08',pthWal/'WCTRAIL.g08'])
def test_findKey():
    i=x.lines[:]
    i = listJoin(i)
    key = 'Nice'
    # # print(i)
    assert txt.findKey(i,key) == 2
def test_findKey_int():
    i=x.lines[:]
    assert txt.findKey(i,2) == 2
def test_findKey_regx():
    i=x.lines[:]
    i = listJoin(i)
    key = 'ice.*you'
    # print(i)
    assert txt.findKey(i,key,how="regex") == 2
def test_findKey_not():
    o = len(x.seq)-1
    assert txt.findKey(x.seq[:],'Plan File',how='!!',startFrom =len(x.seq[:])-4)==o
def test_findKey_1notfound():
    i = list('abcdefg')
    assert txt.findKey(i,['b','indeed','f']) is None


@pytest.mark.parametrize("linez,i,o",
    [
        (
        ['one','two','three','one','four'],
         'one',3
        ),
        (
         ['zero','four','two','three','four','five','six','seven'],
         'four',4
        ),
    ]
    )
def test_findKeyR(linez,i,o):
    assert txt.findKeyR(linez,i)==o

def test_getKeys():
    assert txt.getKeys(x.fresh(x.geo),['Program Version=','Geom Title=']) == ['5.07','mock']
def test_getKeys_one():
    assert txt.getKeys(x.fresh(x.geo),'Program Version=') == ['5.07']
def test_getKey_whitespace():
    assert txt.getKeys(x.fresh(x.geo),'River Reach=')[0][-1] != ' '
def test_getKeys_keynotfound():
    i = ['Geom Title=mock\n','Program Version=5.07\n','Viewing Rectangle= 3128597.8135\n']
    txt.write(mc/'geo_tst.g01',i,backup=False)
    assert txt.getKeys(mc/'geo_tst.g01',['Program Version=','boomshakalaka!','Geom Title=']) == ['5.07',None,'mock']

@pytest.mark.parametrize('trim,o',
    [
    (0,['     Time of Concentration: 19.3',
        '     Time of Concentration: 11.28',
        '     Time of Concentration: 10.31']),
    (1,[' 19.3',
        ' 11.28',
        ' 10.31']),
    (2,['19.3',
        '11.28',
        '10.31'])
        ]
)
def test_getKeys_trim(trim,o):
    bsn = x.fresh(mc/'mockHMS'/'2018_Existing_Conditions.basin')
    DAs = ['S_Cr_43', 'S_Cr_p4', 'S_Cr_1']   
    DAs = [f'Subbasin: {da}' for da in DAs]
    keyz = list(zip(DAs,['     Time of Concentration:']*len(DAs)))
    
    assert txt.getKeys(bsn,keyz,trim=trim)==o

def test_setKeys():
    geo = x.fresh(x.geo)
    txt.setKeys(geo,{'Program Version=':'9000','Geom Title=':'best'},backup=False)
    assert txt.getKeys(geo,['Program Version=','Geom Title=']) == ['9000','best'], \
        geo.read_text()[:100]
def test_setKeys_func():
    titlefunc = lambda st: st.replace('o','a')
    versionfunc = lambda st: f'{st}.099'
    geo = x.fresh(x.geo)
    txt.setKeys(geo,{'Program Version=':versionfunc,
        'Geom Title=':titlefunc,'Viewing Rectangle=':'Super Wide'},
        backup=False)
    assert txt.getKeys(geo,['Program Version=','Geom Title=','Viewing Rectangle=']) \
        == ['5.07.099','mack','Super Wide'], geo.read_text()[:100]

@pytest.mark.parametrize("key,val",
    [
        ('DSS File=','Dee Ess Ess'),
        ('Crank dat=','Soulja Boy'),
    ]
    )
def test_setOrInsertKey(key,val):
    prj=x.fresh(x.prj)
    txt.setOrInsertKey(prj,{key:val},'DSS End Time')
    assert txt.getKeys(prj,key,trim=1)[0]==val

def test_getSeq():
    i=x.seq[:]
    o=['Plan File=p02\n', 'Plan File=p08\n', 'Plan File=p09\n', 'Plan File=p03\n', 'Plan File=p07\n', 'Plan File=p04\n', 'Plan File=p10\n', 'Plan File=p11\n', 'Plan File=p12\n', 'Plan File=p13\n', 'Plan File=p14\n', 'Plan File=p15\n', 'Plan File=p16\n', 'Plan File=p17\n', 'Plan File=p18\n', 'Plan File=p19\n']
    assert txt.getSeq(i,'Plan File',trim=0)==o
def test_getSeq_how2():
    i=x.seq[:]
    o=['Plan File=p02\n', 'Plan File=p08\n', 'Plan File=p09\n', 'Plan File=p03\n', 'Plan File=p07\n', 'Plan File=p04\n', 'Plan File=p10\n', 'Plan File=p11\n', 'Plan File=p12\n', 'Plan File=p13\n', 'Plan File=p14\n', 'Plan File=p15\n', 'Plan File=p16\n', 'Plan File=p17\n', 'Plan File=p18\n', 'Plan File=p19\n']
    assert txt.getSeq(i,'Plan File',trim=0)==o
def test_getSeq_key2():
    i=x.seq[:]
    o=['Unsteady File=u01\n', 'Unsteady File=u02\n', 'Unsteady File=u03\n', 'Unsteady File=u04\n']
    assert txt.getSeq(i,'Unsteady File',key2='Plan File',trim=0)==o
def test_getSeq_trim1():
    i=x.seq[:]
    o=['02\n', '08\n', '09\n', '03\n', '07\n', '04\n', '10\n', '11\n', '12\n', '13\n', '14\n', '15\n', '16\n', '17\n', '18\n', '19\n']
    assert txt.getSeq(i,'Plan File=p',trim=1)==o
def test_getSeq_trim2():
    i=x.seq[:]
    o=['02', '08', '09', '03', '07', '04', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19']
    assert txt.getSeq(i,'Plan File=p',trim=2)==o
def test_getSeq_trim2_2():
    i=['Proj Title=precip_model\n', 'Current Plan=p05\n', 'Default Exp/Contr=0.3,0.1\n', 'English Units\n', 'Geom File=g01\n', 'Geom File=g03\n', 'Geom File=g04\n', 'Geom File=g05\n', 'Geom File=g02\n', 'Geom File=g09\n', 'Geom File=g08\n', 'Geom File=g11\n', 'Geom File=g12\n', 'Geom File=g13\n', 'Geom File=g14\n', 'Unsteady File=u01\n', 'Unsteady File=u02\n', 'Unsteady File=u03\n', 'Unsteady File=u04\n', 'Unsteady File=u05\n', 'Plan File=p02\n', 'Plan File=p08\n', 'Plan File=p09\n', 'Plan File=p03\n', 'Plan File=p07\n', 'Plan File=p04\n', 'Plan File=p10\n', 'Plan File=p11\n', 'Plan File=p12\n', 'Plan File=p13\n', 'Plan File=p14\n', 'Plan File=p15\n', 'Plan File=p16\n', 'Plan File=p17\n', 'Plan File=p18\n', 'Plan File=p19\n', 'Plan File=p01\n', 'Plan File=p05\n', 'Background Map Layer=DAs\n', 'Background Map Layer=culs\n', 'Background Map Layer=byhand2\n', 'Background Map Layer=CulvertCenterline\n', 'Background Map Layer=culverts 1d\n', 'Background Map Layer=SurveyPts_prj\n', 'Background Map Layer=TankAreas\n', 'Background Map Layer=DAs\n', 'Y Axis Title=Elevation\n', 'X Axis Title(PF)=Main Channel Distance\n', 'X Axis Title(XS)=Station\n', 'BEGIN DESCRIPTION:\n', '\n', 'END DESCRIPTION:\n', 'DSS Start Date=01JAN2020\n', 'DSS Start Time=00:00\n', 'DSS End Date=01JAN2020\n', 'DSS End Time=24:00\n', 'DSS File=dss\n', 'DSS Export Filename=\n', 'DSS Export Rating Curves= 0 \n', 'DSS Export Rating Curve Sorted= 0 \n', 'DSS Export Volume Flow Curves= 0 \n', 'DXF Filename=\n', 'DXF OffsetX= 0 \n', 'DXF OffsetY= 0 \n', 'DXF ScaleX= 1 \n', 'DXF ScaleY= 10 \n', 'GIS Export Profiles= 0 \n']
    o=['02','08','09','03','07','04','10','11','12','13','14','15','16','17','18','19','01','05']
    assert txt.getSeq(i,'Plan File=p',trim=2)==o
def test_getseq_whitespace():
    i=['seek  \n','seqaleek      \n','seqaleek asdf         \n']
    o = txt.getSeq(i,'seq',trim=2)
    print(o)
    for seq in o:
        assert seq[-1]!=' '
        assert not '\n' in seq
def test_getseq_seqAtEnd():
    i=['seek  \n','seq\n','seq\n']
    o = txt.getSeq(i,'seq',trim=0)
    assert o == ['seq\n','seq\n']
def test_getseq_notfound():
    i=x.seq[:]
    assert txt.getSeq(i,'notgonnafind') is None
def test_getSeq_limits():
    i=x.seq[:]
    o=['Plan File=p02\n', 'Plan File=p08\n', 'Plan File=p09\n', 'Plan File=p03\n', 'Plan File=p07\n', 'Plan File=p04\n', 'Plan File=p10\n', 'Plan File=p11\n', 'Plan File=p12\n', 'Plan File=p13\n', 'Plan File=p14\n', 'Plan File=p15\n', 'Plan File=p16\n', 'Plan File=p17\n', 'Plan File=p18\n', 'Plan File=p19\n']
    ot= txt.getSeq(i,'Plan File',retrn='both',trim=0)
    assert ot[0]==o
    assert ot[2]>ot[1]
def test_setSeq_recip():
    '''reciprocal'''
    prj=x.fresh(x.prj)
    seq = ['p01','p02','p03']
    txt.setSeq(prj,seq,'Plan File=')
    lines = txt.read(prj)
    assert txt.getSeq(lines,'Plan File=')==seq
def test_Equal():
    msg=x.fresh(x.msg)
    assert txt.equal([msg,x.msg])
def test_Read_overwrite():
    msg=x.fresh(x.msg)
    lines = txt.read(msg)
    txt.write(msg,lines,backup=False)
    assert txt.equal([msg,x.msg])

def test_insertLines():
    i = x.lines[:]
    i = listJoin(i)
    addlnes = ['Jim','And you?','Nevermind']
    o = ['Hello there','Nice to meet you','My name is','Jim','And you?','Nevermind','Goodbye']
    o = listJoin(o)
    assert txt.insertLines(i,addlnes,'My name',newLine=True) == o
def test_insertLines_called_twice():
    i = x.lines[:]
    i = listJoin(i)
    addlnes = ['Jim','And you?','Nevermind']
    i = txt.insertLines(i,addlnes,'My name',newLine=True)
    o = ['Hello there','Nice to meet you','My name is','Jim','And you?','Nevermind','Jim','And you?','Nevermind','Goodbye']
    o = listJoin(o)
    assert txt.insertLines(i,addlnes,'My name',newLine=True) == o
def test_insertLines_no_newline():
    i = x.lines[:]
    addlness = ['Jim','And you?','Nevermind']
    o = ['Hello there','Nice to meet you','My name is','Jim','And you?','Nevermind','Goodbye']
    assert txt.insertLines(i,addlness,'My name',newLine=False) == o
def test_insertLines_oneliner():
    i = x.lines[:]
    addlness = ['Joe']
    o = ['Hello there','Nice to meet you','My name is','Joe','Goodbye']
    assert txt.insertLines(i,addlness,'My name',newLine=False) == o
    #False,'bug! if only one line and newLine=True listjoin operates on string instead list'
def test_insertLines_keyAsInt():
    i = x.lines[:]
    addlness = ['Joe']
    o = ['Hello there','Nice to meet you','My name is','Joe','Goodbye']
    assert txt.insertLines(i,addlness,2,newLine=False) == o
# def test_insertLinesregex():
#     i = x.lines + ['999 999','65','45 45    45','end']
#     i = listJoin(i)
#     addlnes = ['Jim','Nevermind']
#     o = ['Hello there','Nice to meet you','My name is','Jim','And you?','Nevermind','Goodbye']
#     o = listJoin(o)
#     assert txt.insertLines(i,addlnes,'My name',how='regex') == o
def test_removeLines():
    i = [listJoin(x.lines[:]),'Nice','Good']
    o = ['Hello there','Goodbye']
    o = listJoin(o)
    assert txt.removeLines(*i)[0] == o
    assert x.lines == ['Hello there','Nice to meet you','My name is','Goodbye']
def test_removeLines_1():
    i = [listJoin(x.lines[:]),'Nice','Good']
    assert txt.removeLines(*i)[1] == 2
def test_removeLines_noNewLine():
    i = [x.lines[:],'Nice','Good']
    o = ['Hello there','Goodbye']
    assert txt.removeLines(*i)[0] == o
def test_removeLinesL():
    i = [listJoin(x.lines[:]),'Hello','Good']
    o = ['Goodbye']
    #o = listJoin(o)
    assert txt.removeLines(*i)[0] == o
def test_removeLinesregex():
    # print(x.lines)
    i = x.lines + ['999 999','65','45 45    45','end']
    i = listJoin(i)
    # print(i)
    o = ['Hello there','Nice to meet you','My name is','end']
    o = listJoin(o)
    assert txt.removeLines(i,'Good',regxASCII,how2='regex')[0] == o
def test_replaceLines():
    lines = x.lines[:]
    addlines = ["Whats your favorite color?","mines blue"]
    o = ['Hello there','Nice to meet you',"Whats your favorite color?","mines blue",'Goodbye']
    # print(txt.replaceLines(lines,addlines,'My '))
    assert txt.replaceLines(lines,addlines,'My ')==o
def test_getBlock():
    assert False, 'todo'
def test_replaceBlock():
    assert False, 'todo'