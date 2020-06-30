# from django.http import HttpResponse,JsonResponse
# from BombApp.models import *
# import json,time
# from django.db.models import Q, Max
# from django.conf import settings
# import os
#
# def checkversion(request):  # 版本同步
#     vers = json.loads(request.body)['data']
#     # print(vers)
#     rt = dict(ver=HelpGet(VersionTable.objects.all()), data={})
#     for ver in vers:
#        tb = MP_TABLE[ver['tb_name']]
#        rt["data"][ver['tb_name']] = HelpGet(tb.objects.filter(version__gt=ver['max_version']).all())
#     return JsonResponse(rt, safe=False)
#
#
# def uploading(request):
#     if request.method == 'POST':
#         obj = request.FILES.get('file')
#
#         # print(obj.name)
#         f = open(
#             os.path.join(settings.BASE_DIR,'static', obj.name),'wb')
#         print(f)
#         for chunk in obj.chunks():
#             f.write(chunk)
#         f.close()
#         result = {'path': os.path.join(settings.MEDIA_ROOT)}
#         print(result)
#         return JsonResponse(result)
#
#
# def addrelation(request):
#     add_data = json.loads(request.body)
#     zhs = {}
#     verDict = dict()
#     for ver in VersionTable.objects.all().values():
#         verDict[ver['tb_name']] = ver['max_version']
#         if ver['tb_name'] in ['simplelib', 'relationtable', 'checklist']:
#             ver['max_version'] += 1
#             VersionTable.objects.filter(tb_name=ver['tb_name']).update(max_version=ver['max_version'])
#
#     gr = RelationTable.objects.values_list('groups')
#     groups = 0
#     if len(gr) > 0:
#         groups = gr.aggregate(Max('groups'))['groups__max']
#
#     def util(name, tp):
#         if name not in zhs:
#             rs = Simplelib.objects.filter(zhname=name, audit=2).values()
#             print(rs)
#             if len(rs) == 0:
#                 rs = Simplelib.objects.create(
#                     type=tp, zhname=name, linkable=0, visible=1, audit=0, version=verDict['simplelib'] + 1
#                 )
#                 rs.save()
#                 print(rs.id)
#             zhs[name] = rs.id
#
#         return zhs[name]
#
#     groups += 1
#     sid = util('linktag', 1)
#     for member in add_data['members']:
#         tid = util(member['name'], 0)
#         RelationTable.objects.create(
#             audit=0, stb='simplelib', sid=sid, ttb='simplelib',
#             tid=tid, extra=member['extra'], version=verDict['relationtable'] + 1,
#             groups=groups
#         ).save()
#
#
#     tid = sid
#     rels = RelationTable.objects.create(
#         audit=0, stb=None, sid=None, ttb='simplelib',
#         tid=tid, extra=None, version=verDict['relationtable'] + 1,
#         groups=0
#     )
#     rels.save()
#     rid = rels.id
#     CheckTable.objects.create(
#         rid=rid, account=None, content=None,
#         time=time.time(), version=verDict['checklist'] + 1
#     ).save()
#
#     return JsonResponse({"success": 1, "msg": 0})
#
#
# def addcategory(request):
#     cates = json.loads(request.body)
#     # print(len(cates))
#     pid = cates['pid']
#     tb = cates['tb']
#     tbid = cates['tbid']
#     name = cates['name']
#
#     if pid != 0:
#         result = CategoryTable.objects.filter(id=pid).values()
#         if len(result) > 0:
#             if result[0]['vision'] == 0:
#                 return JsonResponse({"success": 0, 'msg': 201})
#         else:
#             return JsonResponse({'success': 0, 'msg': 200})
#
#     ver = VersionTable.objects.filter(tb_name='tablecategory').values()[0]
#     version = ver['max_version']+1
#     # print(ver)
#     cates_datas = CategoryTable.objects.create(
#         pid=pid, tb=tb, tbid=tbid, name=name, visible=1, version=version
#     )
#     cates_datas.save()
#
#     VersionTable.objects.filter(tb_name='tablecategory').update(max_version=version)
#
#     return JsonResponse({"success": 1, "msg": 0})
#
#
# def addlib(request):
#     add_data = json.loads(request.body)
#     zhs = {}
#     verDict = dict()
#     for ver in VersionTable.objects.all().values():
#         verDict[ver['tb_name']] = ver['max_version']
#         if ver['tb_name'] in ['simplelib', 'relationtable', 'checklist']:
#             ver['max_version'] += 1
#             VersionTable.objects.filter(tb_name=ver['tb_name']).update(max_version=ver['max_version'])
#
#     def util(name, tp):
#         if name not in zhs:
#             rs = Simplelib.objects.filter(zhname=name, audit=2).values()
#             print(rs)
#             if len(rs) == 0:
#                 rs = Simplelib.objects.create(
#                     type=tp, zhname=name, linkable=0, visible=1, audit=0, version=verDict['simplelib'] + 1
#                 )
#                 rs.save()
#                 print(rs.id)
#             zhs[name] = rs.id
#
#         return zhs[name]
#
#     tid = util(add_data['data']['zhname'], 0)
#     rels = RelationTable.objects.create(
#         audit=0, stb=None, sid=None, ttb='simplelib',
#         tid=tid, extra=None, version=verDict['relationtable'] + 1,
#         groups=0
#     )
#     rels.save()
#     rid = rels.id
#     CheckTable.objects.create(
#         rid=rid, account=None,content=None,
#         time=time.time(), version=verDict['checklist'] + 1
#     ).save()
#
#     return JsonResponse({'success': 1, 'msg': 200, 'id': tid})
#
#
# def addexplosion(request):
#     add_data = json.loads(request.body)
#     verDict = dict()
#     for ver in VersionTable.objects.all().values():
#         verDict[ver['tb_name']] = ver['max_version']
#         if ver['tb_name'] in ['bombinfo','relationtable', 'checklist']:
#             ver['max_version'] += 1
#             VersionTable.objects.filter(tb_name=ver['tb_name']).update(max_version=ver['max_version'])
#
#
#     add_data['data']['version'] = verDict['bombinfo'] + 1
#     add_data['data']['audit'] = 0
#     bomb = Bombinfo.objects.create(**add_data['data'])
#     bomb.save()
#     sid = bomb.id
#
#
#     rels = RelationTable.objects.create(
#         audit=0, stb=None, sid=None, ttb='bombinfo',
#         tid=sid, extra=None, version=verDict['relationtable'] + 1,
#         groups=0
#     )
#     rels.save()
#     rid = rels.id
#     CheckTable.objects.create(
#         rid=rid, account=None, content=None,
#         time=time.time(), version=verDict['checklist'] + 1
#     ).save()
#
#     return JsonResponse({'success': 1, 'msg': 0, 'id': sid})
#
#
# def editcategory(request):
#     edit_data = json.loads(request.body)
#     cate_id = CategoryTable.objects.filter(id=edit_data['id']).values()
#     if len(cate_id) == 0:
#         return JsonResponse({"success": 0, 'msg': 500})
#     cate_version = CategoryTable.objects.filter(
#         id=edit_data['id'],
#         version=edit_data['version']
#     ).values()
#     if not cate_version:
#         return JsonResponse({"success": 0, 'msg': 501})
#
#     cate_name = CategoryTable.objects.filter(
#         ~Q(id=edit_data['id']), name=edit_data['name'], version=1
#     ).values()
#     if cate_name:
#         return JsonResponse({"success": 0, 'msg': 502})
#     verDict = dict()
#     for ver in VersionTable.objects.all().values():
#         verDict[ver['tb_name']] = ver['max_version']
#         if ver['tb_name'] in ['tablecategory']:
#             ver['max_version'] += 1
#             VersionTable.objects.filter(tb_name=ver['tb_name']).update(max_version=ver['max_version'])
#
#     CategoryTable.objects.filter(id=edit_data['id']).update(
#         name=edit_data['name'],version=verDict['tablecategory'] + 1
#     )
#     return JsonResponse({"success": 1, 'msg': 0})
#
#
# def editlib(request):
#     edit_data = json.loads(request.body)
#     data_id = Simplelib.objects.filter(id=edit_data['data']['id']).values()
#     if len(data_id) == 0:
#         return JsonResponse({"success": 0, 'msg': 600})
#     else:
#         data_version = Simplelib.objects.filter(
#             id=edit_data['data']['id'],
#             version=edit_data['data']['version']
#         ).values()
#         if data_version:
#             data_name = Simplelib.objects.filter(
#                 ~Q(id=edit_data['data']['id']), zhname=edit_data['data']['zhname'], audit=2, version=1
#             ).values()
#             if data_name:
#                 return JsonResponse({"success": 0, 'msg': 602})
#         else:
#             return JsonResponse({"success": 0, 'msg': 601})
#
#     verDict = dict()
#     for ver in VersionTable.objects.all().values():
#         verDict[ver['tb_name']] = ver['max_version']
#         if ver['tb_name'] in ['simplelib', 'relationtable', 'checklist']:
#             ver['max_version'] += 1
#             VersionTable.objects.filter(tb_name=ver['tb_name']).update(max_version=ver['max_version'])
#
#     edit_data['data']['audit'] = 0
#     edit_data['data']['version'] = verDict['simplelib'] + 1
#     data_id = edit_data['data']['id']
#     del edit_data['data']['id']
#     sim = Simplelib.objects.create(**edit_data['data'])
#     sim.save()
#
#     zhs = {sim.zhname: sim.id}
#
#     def util(name, tp):
#         if name not in zhs:
#             rs = Simplelib.objects.filter(zhname=name, audit=2).values()
#             if len(rs) == 0:
#                 rs = Simplelib.objects.create(
#                     type=tp, zhname=name, linkable=0, visible=1, audit=0, version=verDict['simplelib']+1
#                 )
#                 rs.save()
#             zhs[name] = rs.id
#         return zhs[name]
#     sid = util(edit_data['data']['zhname'], 0)
#     tid = sim.id
#     rels = RelationTable.objects.create(
#         audit=0, stb='simplelib', sid=sid, ttb='simplelib',
#         tid=tid, extra=None, version=verDict['relationtable'] + 1,
#         groups=0
#     )
#     rels.save()
#     rid = rels.id
#     CheckTable.objects.create(
#         rid=rid, account=None, content=None,
#         time=time.time(), version=verDict['checklist'] + 1
#     ).save()
#
#     return JsonResponse({'success': 1, 'msg': 0})
#
#
# def editexplosion(request):
#     edit_data = json.loads(request.body)
#
#     info_id = Bombinfo.objects.filter(id=edit_data['data']['id']).values()
#     if len(info_id) == 0:
#         return JsonResponse({"success": 0, 'msg': 700})
#
#     info_version = Bombinfo.objects.filter(
#         id=edit_data['data']['id'],
#         version=edit_data['data']['version']
#     ).values()
#     if not info_version:
#         return JsonResponse({"success": 0, 'msg': 701})
#
#     verDict = dict()
#     for ver in VersionTable.objects.all().values():
#         verDict[ver['tb_name']] = ver['max_version']
#         if ver['tb_name'] in ['bombinfo', 'relationtable', 'checklist']:
#             ver['max_version'] += 1
#             VersionTable.objects.filter(tb_name=ver['tb_name']).update(max_version=ver['max_version'])
#
#     edit_data['data']['version'] = verDict['bombinfo'] + 1
#     edit_data['data']['audit'] = 0
#     edit_id = edit_data['data']['id']
#     del edit_data['data']['id']
#     bomb = Bombinfo.objects.create(**edit_data['data'])
#     bomb.save()
#     sid = bomb.id
#
#     rels = RelationTable.objects.create(
#         audit=0, stb='bombinfo', sid=edit_id, ttb='bombinfo',
#         tid=sid, extra=None, version=verDict['relationtable'] + 1,
#         groups=0
#     )
#     rels.save()
#     rid = rels.id
#     CheckTable.objects.create(
#         rid=rid, account=None, content=None,
#         time=time.time(), version=verDict['checklist'] + 1
#     ).save()
#
#     return JsonResponse({"success": 1, 'msg': 0})
#
#
#
#
#
#
#
# from dataclasses import dataclass,field,asdict,astuple
# from typing import List
# @dataclass
# class InventoryItem:
#     name: str
#     unit_price: float
#     quantity_on_hand: int = 0
#
#     def total_cost(self) -> float:
#         return self.unit_price * self.quantity_on_hand
#
# item = InventoryItem('hammers', 10.49, 12)
# print(item.total_cost())
# # #
#
# @dataclass
# class Point:
#      x: int
#      y: int
#
# @dataclass
# class C:
#      mylist: List[Point]
#
# p = Point(10, 20)
# assert asdict(p) == {'x': 10, 'y': 20}
#
# c = C([Point(0, 0), Point(10, 4)])
# assert asdict(c) == {'mylist': [{'x': 0, 'y': 0}, {'x': 10, 'y': 4}]}
# assert astuple(p) == (10, 20)
# assert astuple(c) == ([(0, 0), (10, 4)])
