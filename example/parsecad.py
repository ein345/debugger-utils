
import sys
sys.path.append('/home/ubuntu/debugger-utils')
import gdb
import gdb_utils
import pyperclip
def Point(who, *args):
    x = gdb.parse_and_eval(who[0]+"->x")
    y = gdb.parse_and_eval(who[0]+"->y")
    strOut ="({},{})".format(x,y)
    return strOut  

def TouchSegment(who, *args):
    strVar = who[0]+".ETouchType"
    strOut=""
    ttype = gdb.parse_and_eval(strVar)
    if ttype == 1:
        strOut+="接触墙体"
    elif ttype == 4:
        strOut+="接触横梁"
    elif ttype == 5:
        strOut+="接触楼板"
    
    strOut+=str(gdb.parse_and_eval(who[0]+".fStart"))
    strOut+="~"
    strOut+=str(gdb.parse_and_eval(who[0]+".fEnd"))
    return strOut

def Edge(who, *args):
    ptS = Point([who[0]+"->ptStart"])
    ptE = Point([who[0]+"->ptEnd"])
    
    strOut ="({},{})".format(ptS,ptE)
    
    ts = gdb.parse_and_eval(who[0]+"->touchSegments")

    tsi = gdb.parse_and_eval(who[0]+"->touchSegments.size()")
    
    if tsi>0:
        strOut+="\n  接触个数:" +str(tsi)+"\n"
        for it in range(tsi):
            strTouchVar = who[0]+"->touchSegments[{}]".format(it)
            strOut+="  " +TouchSegment([strTouchVar])+"\n"

    return strOut 


def Polygon(who, *args):
    edges = gdb.parse_and_eval(who[0]+"->m_edges")
    pSize = gdb.parse_and_eval(who[0]+"->m_points.size()")
    eSize = gdb.parse_and_eval(who[0]+"->m_edges.size()")
   
	# #######打印顶点序列
    str = who[0]+"->m_points[0]"
    strP0 = Point([str])
    strOut ="顶点个数:{}\n".format(pSize)
    strOut+="Polyline("
    ii=0
    while(ii<pSize):
        print(".",end="",flush=True)#进度条
        strVar = who[0]+"->m_points[{}]".format(ii)
        if ii == 0:
            strOut+=Point([strVar])
        else:
            strOut+=","+Point([strVar])
        ii=ii+1
    
    if(pSize>0):
        strOut+=")"   
	# #######
    if eSize>0:
        strOut+="\n边数{}:\n".format(eSize)
    ii=0
    while ii<eSize :
        print(".",end="",flush=True)#进度条
        edge = Edge([who[0] + "->m_edges[{}]".format(ii)])
        strOut+=edge+"\n"
        ii=ii+1
    
    print("\r",end="",flush=True)#进度条
    return strOut


gdb_utils.define(Polygon)

def Comp(who, *args):
    flH = gdb.parse_and_eval(who[0]+"->floorHeight")
    comptype = gdb.parse_and_eval(who[0]+"->m_eCompType")
    
    compthick = gdb.parse_and_eval(who[0]+"->m_thick")
    compOffset = gdb.parse_and_eval(who[0]+"->getZOffset()")
 
    strOut = "结构件类型:{}, 楼层高:{} 厚度:{}, 沉降:{}\n".format(comptype,flH,compthick,compOffset)
    strOut += Polygon([who[0]+"->m_plg"])
    return strOut

gdb_utils.define(Comp)

def findType(type, arr):
    for it in arr:
        if it in type:
            return True
    return False

def jsonStr(who, *args):
    gdb.execute("set print elements 0")
    strOut = str(gdb.parse_and_eval(who[0] + ".toString()"))
    strOut=strOut.replace('\\"', '\"')
    strOut=strOut.replace('\\n', '')
   
    if len(strOut)<1000:
        print(strOut)
    else:
        pyperclip.copy(strOut)  
        print("Json文本太长,已复制到剪切板")
gdb_utils.define(jsonStr)


def mp(who, *args):
    type = str(gdb.parse_and_eval(who[0]).type)
    gdb.execute("set scheduler-locking on")
    if type in ["FPointSPtr", "MatchMold::FPoint"]:
        print("点:")
        print(Point(who))
    elif findType(type,["FEdgeSPtr", "MatchMold::FEdge"]):
        print("边:")
        print(Edge(who))
    elif findType(type,["FPolygonSPtr", "MatchMold::FPolygon"]):
        print("多边形:")
        print(Polygon(who))
    elif findType(type,["FExtrudeComponentSPtr", "MatchMold::FExtrudeComponent"]):
        print("结构件:")
        print(Comp(who))
    
    elif findType(type,["JsonVal", "Json::Value"]):
        jsonStr(who)
    else:
        gdb.execute("p {}".format(who[0]))
    print("===============================")
    gdb.execute("set scheduler-locking off")
gdb_utils.define(mp)

def findBox(who, *args):
    iVarCnt = len(who)
    icnt = gdb.parse_and_eval(who[0]+".size()")
    
    iFindCnt = 0
    for i in range(icnt):
        print("\r",i,end="",flush=True)
        v0 = gdb.parse_and_eval("{0}[{1}]->getBox().minx<={2}".format(who[0], i,who[1]))
        if not v0:  
            continue
        v1 = gdb.parse_and_eval("{0}[{1}]->getBox().maxx>={2}".format(who[0], i,who[1]))
        if not v1:
            continue
        v2 = gdb.parse_and_eval("{0}[{1}]->getBox().miny<={2}".format(who[0], i,who[2]))
        if not v2:
            continue
        v3 = gdb.parse_and_eval("{0}[{1}]->getBox().maxy>={2}".format(who[0], i,who[2]))
        if not v3:
            continue
        
        iFindCnt=iFindCnt+1
        print("\r","\n",end="\r",flush=True)
        print(i)
        print(gdb.parse_and_eval(who[0]+"[{}]".format(i)).address)
        print(gdb.parse_and_eval(who[0]+"[{}]->getBox()".format(i)))
        if iVarCnt<4 or who[3]!="1":
            break
    if iFindCnt==0:
        print("\r","无匹配",end="\r",flush=True)
gdb_utils.define(findBox)
