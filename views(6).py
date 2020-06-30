from django.http import HttpResponse,JsonResponse
from BombApp.models import *
import json,time
from django.db.models import Q, Max
from django.conf import settings
import os

def checkversion(request):  # 版本同步
    vers = json.loads(request.body)['data']
    # print(vers)
    rt = dict(ver=HelpGet(VersionTable.objects.all()), data={})
    for ver in vers:
       tb = MP_TABLE[ver['tb_name']]
       rt["data"][ver['tb_name']] = HelpGet(tb.objects.filter(version__gt=ver['max_version']).all())
    return JsonResponse(rt, safe=False)


def uploading(request):
    if request.method == 'POST':
        obj = request.FILES.get('file')

        # print(obj.name)
        f = open(
            os.path.join(settings.BASE_DIR,'static', obj.name),
            'wb')
        print(f)
        for chunk in obj.chunks():
            f.write(chunk)
        f.close()
        result = {'path': os.path.join(settings.MEDIA_ROOT)}
        print(result)
        return JsonResponse(result)


def addcategory(request):
    cates = json.loads(request.body)
    # print(len(cates))
    pid = cates['pid']
    tb = cates['tb']
    tbid = cates['tbid']
    name = cates['name']

    if pid != 0:
        result = CategoryTable.objects.filter(id=pid).values()
        if len(result) > 0:
            if result[0]['vision'] == 0:
                return JsonResponse({"success": 0, 'msg': 201})
        else:
            return JsonResponse({'success': 0, 'msg': 200})

    ver = VersionTable.objects.filter(tb_name='tablecategory').values()[0]
    version = ver['max_version']+1
    # print(ver)
    cates_datas = CategoryTable.objects.create(
        pid=pid, tb=tb, tbid=tbid, name=name, visible=1, version=version
    )
    cates_datas.save()

    VersionTable.objects.filter(tb_name='tablecategory').update(max_version=version)

    return JsonResponse({"success": 1, "msg": 0})


def addrelation(request):
    add_data = json.loads(request.body)
    verDict = dict()
    for ver in VersionTable.objects.all().values():
        verDict[ver['tb_name']] = ver['max_version']
        if ver['tb_name'] in [ 'relationtable']:
            ver['max_version'] += 1
            VersionTable.objects.filter(tb_name=ver['tb_name']).update(max_version=ver['max_version'])

    add_data['aduit'] = 0
    add_data['version'] = verDict['relationtable'] + 1
    res = RelationTable.objects.create(**add_data)
    res.save()

    return JsonResponse({"success": 1, "msg": 0})


def addlib(request):
    add_data = json.loads(request.body)
    if add_data['data']['type'] == 1:
        result = CategoryTable.objects.filter(
            id=add_data['parentId'],
            visible=1
        ).values()
        if not result:
            return JsonResponse({'success': 0, 'msg': 0})

        verDict = dict()
        for ver in VersionTable.objects.all().values():
            verDict[ver['tb_name']] = ver['max_version']
            if ver['tb_name'] in ['simplelib', 'tablecategory', 'ralationtable', 'checklist']:
                ver['max_version'] += 1
                VersionTable.objects.filter(tb_name=ver['tb_name']).update(max_version=ver['max_version'])

        add_data['audit'] = 0
        add_data['version'] = verDict['simplelib'] + 1
        sim = Simplelib.objects.create(**add_data['data'])
        sim.save()

        CategoryTable.objects.create(
            pid=add_data['parentId'],tb='simplelib',
            tbid=sim.id,visible=1,name=None,version=verDict['tablecategory'] + 1
        ).save()

        CheckTable.objects.create(
            stb="simplelib",sid = sim.id,tid = None,
            account = None,content = None,time = None,
            method =0,audit = 0,version = verDict['checklist'] + 1
        ).save()

        return JsonResponse({'success': 1, 'msg': 200, 'id': sim.id})

    if add_data['data']['type'] == 0:

        verDict = dict()
        for ver in VersionTable.objects.all().values():
            verDict[ver['tb_name']] = ver['max_version']
            if ver['tb_name'] in ['simplelib', 'tablecategory', 'checklist']:
                ver['max_version'] += 1
                VersionTable.objects.filter(tb_name=ver['tb_name']).update(max_version=ver['max_version'])

        add_data['audit'] = 0
        add_data['version'] = verDict['simplelib'] + 1
        sim = Simplelib.objects.create(**add_data['data'])
        sim.save()

        cates = CategoryTable.objects.create(
            pid=0, tb=None,tbid=None, visible=0,
            name=None, version=verDict['tablecategory'] + 1
        )
        cates.save()

        CheckTable.objects.create(
            stb="simplelib", sid=sim.id, tid=None,
            account=None, content=None, time=None,
            method=0, audit=0, version=verDict['checklist'] + 1
        ).save()


        return JsonResponse({'success': 1, 'msg': 200, 'id': sim.id})


def addexplosion(request):
    add_datas = json.loads(request.body)
    result = CategoryTable.objects.filter(
        id=add_datas['parentId'],
        visible=1
    ).values()
    if not result:
        return JsonResponse({'success': 0, 'msg': 0})

    verDict = dict()
    for ver in VersionTable.objects.all().values():
        verDict[ver['tb_name']] = ver['max_version']
        if ver['tb_name'] in ['bombinfo', 'tablecategory', 'checklist']:
            ver['max_version'] += 1
            VersionTable.objects.filter(tb_name=ver['tb_name']).update(max_version=ver['max_version'])

    add_datas['data']['version'] = verDict['bombinfo'] + 1
    add_datas['data']['audit'] = 0
    bomb = Bombinfo.objects.create(**add_datas['data'])
    bomb.save()

    CategoryTable.objects.create(
        pid=add_datas['parentId'], tb='bombinfo',
        tbid=bomb.id, visible=1, name=None, version=verDict['tablecategory'] + 1
    ).save()

    CheckTable.objects.create(
        stb="bombinfo", sid=bomb.id, tid=None,
        account=None, content=None, time=None,
        method=0, audit=0, version=verDict['checklist'] + 1
    ).save()

    return JsonResponse({'success': 1, 'msg': 0, 'id': bomb.id})


def editcategory(request):
    edit_data = json.loads(request.body)
    cate_id = CategoryTable.objects.filter(id=edit_data['id']).values()
    if len(cate_id) == 0:
        return JsonResponse({"success": 0, 'msg': 500})
    cate_version = CategoryTable.objects.filter(
        id=edit_data['id'],
        version=edit_data['version']
    ).values()
    if not cate_version:
        return JsonResponse({"success": 0, 'msg': 501})

    cate_name = CategoryTable.objects.filter(
        ~Q(id=edit_data['id']), name=edit_data['name'], version=1
    ).values()
    if cate_name:
        return JsonResponse({"success": 0, 'msg': 502})
    verDict = dict()
    for ver in VersionTable.objects.all().values():
        verDict[ver['tb_name']] = ver['max_version']
        if ver['tb_name'] in ['tablecategory']:
            ver['max_version'] += 1
            VersionTable.objects.filter(tb_name=ver['tb_name']).update(max_version=ver['max_version'])

    CategoryTable.objects.filter(id=edit_data['id']).update(
        name=edit_data['name'],version=verDict['tablecategory'] + 1
    )
    return JsonResponse({"success": 1, 'msg': 0})




def editlib(request):
    edit_data = json.loads(request.body)

    data_id = Simplelib.objects.filter(id=edit_data['data']['id']).values()
    if len(data_id) == 0:
        return JsonResponse({"success": 0, 'msg': 600})
    else:
        data_version = Simplelib.objects.filter(
            id=edit_data['data']['id'],
            version=edit_data['data']['version']
        ).values()
        if data_version:
            data_name = Simplelib.objects.filter(
                ~Q(id=edit_data['data']['id']), zhname=edit_data['data']['zhname'], audit=2, version=1
            ).values()
            if data_name:
                return JsonResponse({"success": 0, 'msg': 602})
        else:
            return JsonResponse({"success": 0, 'msg': 601})

    verDict = dict()
    for ver in VersionTable.objects.all().values():
        verDict[ver['tb_name']] = ver['max_version']
        if ver['tb_name'] in ['simplelib', 'checklist']:
            ver['max_version'] += 1
            VersionTable.objects.filter(tb_name=ver['tb_name']).update(max_version=ver['max_version'])

    edit_data['data']['audit'] = 0
    edit_data['data']['version'] = verDict['simplelib'] + 1
    data_id = edit_data['data']['id']
    del edit_data['data']['id']
    sim = Simplelib.objects.create(**edit_data['data'])
    sim.save()

    CheckTable.objects.create(
        stb="simplelib", sid=sim.id, tid=sim.id,
        account=None, content=None, time=None,
        method=1, audit=0, version=verDict['checklist'] + 1
    ).save()


    return JsonResponse({'success': 1, 'msg': 0, 'id': sim.id})


def editexplosion(request):
    edit_data = json.loads(request.body)

    info_id = Bombinfo.objects.filter(id=edit_data['data']['id']).values()
    if len(info_id) == 0:
        return JsonResponse({"success": 0, 'msg': 700})
    verDict = dict()
    for ver in VersionTable.objects.all().values():
        verDict[ver['tb_name']] = ver['max_version']
        if ver['tb_name'] in ['bombinfo','checklist']:
            ver['max_version'] += 1
            VersionTable.objects.filter(tb_name=ver['tb_name']).update(max_version=ver['max_version'])

    info_version = Bombinfo.objects.filter(
        id=edit_data['data']['id'],
        version=edit_data['data']['version']
    ).values()
    if info_version:
        edit_data['data']['version'] = verDict['bombinfo'] + 1
        edit_data['data']['audit'] = 0
        edit_id = edit_data['data']['id']
        del edit_data['data']['id']
        bomb = Bombinfo.objects.create(**edit_data['data'])
        bomb.save()

        CheckTable.objects.create(
            stb="bombinfo", sid=bomb.id, tid=bomb.id,
            account=None, content=None, time=None,
            method=1, audit=0, version=verDict['checklist'] + 1
        ).save()
        return JsonResponse({'success': 1, 'msg': 0, 'id': bomb.id})

    return JsonResponse({"success": 0, 'msg': 701})


def audittags(request):
    audit_data = json.loads(request.body)
    preaudit = audit_data['audit']
    verDict = dict()
    for ver in VersionTable.objects.all().values():
        verDict[ver['tb_name']] = ver['max_version']
        if ver['tb_name'] in ['simplelib','bombinfo', 'ralationtable','checklist']:
            ver['max_version'] += 1
            VersionTable.objects.filter(tb_name=ver['tb_name']).update(max_version=ver['max_version'])

    for id_s in audit_data['ids']:
        checklist = CheckTable.objects.filter(
            id=id_s,
            audit=0
        ).values()
        if checklist:
            checklist[0]['audit'] = preaudit
            if checklist[0]['stb'] == 'simplelib':
                edittag = Simplelib.objects.filter(id=checklist[0]['sid']).values()
                if edittag[0]['type'] == 0:
                    checklist[0]['content'] = '单质库' + edittag[0]['zhname']
                checklist[0]['content'] = '混合库' + edittag[0]['zhname']
                edittag[0]['version'] = verDict['simplelib'] + 1
            edittag = Bombinfo.objects.filter(id=checklist[0]['sid']).values()
            checklist[0]['content'] = '爆炸案' + edittag[0]['addr']
            edittag[0]['version'] = verDict['bombinfo'] + 1

            checklist[0]['version'] = verDict['checklist'] + 1
            edittag[0]['audit'] = preaudit

            rels = RelationTable.objects.filter(
                sid=edittag[0]['id'],
                stb=checklist[0]['stb'],
                audit=0
            ).values()
            for rel in rels:
                rel['audit']=preaudit
                rel['version'] =verDict['ralationtable'] + 1
            if checklist[0]['method'] == 2 and preaudit == 2:
                edittag[0]['version'] = 0
            if checklist[0]['method'] == 1 and preaudit == 2:
                if checklist[0]['stb'] == 'simplelib':
                    edittagSrc = Simplelib.objects.filter(
                        id=checklist[0]['tid'],
                        audit=2,
                        visible=1
                    ).values()
                    if edittagSrc:
                        edittagSrc[0]['visible'] = 0
                        edittagSrc[0]['version'] = verDict['simplelib'] + 1
                edittagSrc=Bombinfo.objects.filter(
                        id=checklist[0]['tid'],
                        audit=2,
                        visible=1
                    ).values()
                if edittagSrc:
                    edittagSrc[0]['visible'] = 0
                    edittagSrc[0]['version'] = verDict['bombinfo'] + 1

    return JsonResponse({"success": 1, 'msg': 0})




