from django.http import JsonResponse
from BombApp.models import *
from django.db.models import Q
from django.core.paginator import Paginator
import json
from django.core import serializers
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
        # print(s)
        relname_list = []

        result = []
        for i in s:
            sim = Simplelib.objects.filter(
                Q(zhname=i) |
                Q(enname__icontains=i) |
                Q(nickname__icontains=i) |
                Q(cas=i)
            ).values('id','zhname','enname','nickname','cas')
            # print(sim)
            if sim:
                relname_list.append(i)
                relatedname = relname_list[0]
                relatedId = sim[0]['id']
                isNot = True
                print(relatedname,relatedId,isNot)

            else:
                relatedname = i
                relatedId = -1
                isNot = False
                print(relatedname, relatedId, isNot)

            result.append(relatedname)
            result.append(relatedId)
            result.append(isNot)
        list(set(result)).sort(key=result.index)
        print(list(set(result)))
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



