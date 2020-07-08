from django.http import JsonResponse
from BombApp.models import *
from django.db.models import Q
from django.core.paginator import Paginator
import pypinyin
from django.core import serializers
import re
from _collections import defaultdict


def TezImg(request):  # 7.读取指定单质/混合库的“太兹光谱图”图片链接列表
    id = request.GET.get('id', None)
    print(id)
    if id:
        imgIdList = Simplelib.objects.filter(id=id).values('img')
        s = imgIdList[0]['img'].replace('\n','').replace('[','').replace(']','').replace(',','')
        paths = ImgTable.objects.filter(
            id__in=list(map(int,list(s)))
        ).values('paths')
        paths_list = []
        for path in paths:
            paths_list.append("http://127.0.0.1:8000"+ path['paths'])
        return JsonResponse({'success': 0, 'pathList': paths_list})


def boomRelevanceInf(request):  # 3.查找爆炸案关联的单质、混合库信息
    id = request.GET.get('id', None)
    if id:
        bomb = RelationTable.objects.filter(
            stb='bombinfo',
            sid=id
        ).values()
        # print(bomb)
        s = bomb[0]['content'].replace(',\n',"").replace('[','').replace(']','').replace('"','').split()
        print(s)
        relname_list = []

        result = []
        # for i in s:
        sim = Simplelib.objects.filter(
            Q(zhname__in=s) |
            Q(enname__in=s) |
            Q(nickname__in=s) |
            Q(cas__in=s)
        ).values('id','zhname','enname','nickname','cas').distinct().order_by("id")
        # print(sim)
        q = sim[0]
        print(q)
        for key,value in q.items():
            # print(key,value)
            q = [i for i in s if value==i]
            print(q)

        # if sim:
        #     relname_list.append(i)
        #     relatedname = relname_list[0]
        #     relatedId = sim[0]['id']
        #     isNot = True
        #     print(relatedname,relatedId,isNot)

            # else:
            #     relatedname = i
            #     relatedId = -1
            #     isNot = False
            #     print(relatedname, relatedId, isNot)

        #     result.append(relatedname)
        #     result.append(relatedId)
        #     result.append(isNot)
        #
        # print(list(set(result)))
    return JsonResponse({'success': 0, 'msg': 0})


def simpleRelevanceInf(request):  # 4.查找单质/混合库关联的爆炸案信息
    id = request.GET.get('id', None)
    if id:
        sim = Simplelib.objects.filter(
            id=id
        ).values('zhname','enname','nickname','cas')
        s = sim[0]['nickname'].replace('\n',"").replace('[','').replace(']','').replace(",",'').replace('"','').split()
        print(type(s))
        if sim:
            rel = RelationTable.objects.filter(
                stb='bombinfo').filter(
                Q(content__icontains=sim[0]['zhname']) |
                Q(content__icontains=sim[0]['enname']) |
                Q(content__in=s) |
                Q(content__icontains=sim[0]['cas'])
            ).values('sid')
            if rel:
                for re in rel:
                    bom = Bombinfo.objects.filter(
                        id=re['sid']
                    ).values('casename','id','time')
                    print(bom)

    return JsonResponse({'success': 0, 'msg': 0})


def nodeTimeBomb(request):  # 2.通过节点名称或时间段搜索爆炸案
    # kw = request.GET.get('kw', None)
    # if kw:
    #     sim_list = CategoryTable.objects.filter(
    #         Q(zhname__icontains=kw) |
    #         Q(enname__icontains=kw) |
    #         Q(nickname__icontains=kw) |
    #         Q(cas__icontains=kw)
    #     ).values()

    page = int(request.GET.get('page'))
    pageSize = int(request.GET.get("pageSize"))
    res ={}
    master_list = CategoryTable.objects.filter(
        pid=1
    ).values()

    ptr = Paginator(master_list, pageSize)
    res['total'] = ptr.count
    masters = ptr.page(page)
    print(masters)
    res['list'] = masters
    print(res)
    # res['list'] = serializers.serialize('json',masters)
    print(serializers.serialize('json',master_list))
    return JsonResponse({"msg":0})


def hanzi_to_pinyin(last_name):  # 排序
    rows = pypinyin.pinyin(last_name, style=pypinyin.NORMAL)  # 获取首字母
    return ''.join(row[0][0] for row in rows if len(row) > 0)


def simClassify(request): #列出单质库第一级分类列表
    classify = CategoryTable.objects.filter(
        pid=0,
        type=0,
        tb='simplelib'
    ).values('name','id')

    if classify:
        cls = [{'nodename':i['name'],'nodeid':i['id']}for i in classify]
        cls.sort(key=lambda x: hanzi_to_pinyin(x["nodename"][0]))

        return JsonResponse({'success': 0, 'msg': cls})


def bombClassify(request):  # 列出爆炸案第一、二级分类列表
    pid = request.GET.get('pid', None)

    classify = CategoryTable.objects.filter(
        pid=pid,
        tb='bombinfo'
    ).values('name', 'id')
    print(classify)
    if classify:
        cls = [{'nodename':i['name'],'nodeid':i['id']}for i in classify]
        cls.sort(key=lambda x: hanzi_to_pinyin(x["nodename"][0]))
        return JsonResponse({'success': 0, 'msg': cls})


def moleculeFormat(request):   # 分子式格式化显示
    formula = request.GET.get('formula',None).replace('0', "₀").replace('1', "₁").replace('2', "₂").replace('3', "₃")\
        .replace('4', "₄").replace("5", "₅").replace('6', "₆").replace('7', "₇").replace('8', "₈").replace('9', "₉")
    print(formula)

    return JsonResponse({'success': 0, 'msg': formula})


def mixtureIngredient(request):   # 6查找混合库有关的混合物组成成分表
    id = request.GET.get('id', None)
    rel = RelationTable.objects.filter(
        id=id,
        stb='simplelib'
    ).values('content')
    patternSim = re.compile(r'"name": (.*)')
    patternMix = re.compile(r'"linktag": (.*),')
    sim = patternSim.findall(rel[0]['content'])
    mix = patternMix.findall(rel[0]['content'])
    m = mix[0].replace('"','')
    sim_id = Simplelib.objects.filter(
        type=1
    ).filter(
        Q(zhname=m) |
        Q(enname=m) |
        Q(cas=m) |
        Q(nickname__icontains=m)
    ).values()
    print(sim_id)
    # if m === sim_id[0]:
    #     print(1)
    for s in sim:
        print(s.replace('"',''))
    return JsonResponse({'success': 0, 'msg': 0})

