from django.http import JsonResponse
from BombApp.models import *
from django.conf import settings
import json
import time
import os
import hashlib
import re


def md5(pwd):
    md5 = hashlib.md5()
    md5.update(bytes(pwd, encoding='utf-8'))
    return md5.hexdigest()


def loginValid_user(checktype=False):
    def login_Valid(fun):
        def inner(request, *args, **kwargs):
            account_result = request.session.get('account', None)
            if account_result:
                us_exit = User.objects.filter(
                    account=account_result,
                    visible=1
                ).first()
                if us_exit:
                    if checktype == True:
                        if us_exit.type == 0:
                            return fun(request, *args, **kwargs)
                    else:
                        return fun(request, *args, **kwargs)
                return JsonResponse({'success': 0, 'msg': 0})
            else:
                return JsonResponse({'success': 0, 'msg': 10000})
        return inner
    return login_Valid


def checkversion(request):  # 版本同步
    result = VersionTable.objects.filter()
    if not result.exists():
        result_list = [VersionTable(tb_name='simplelib', max_version=1),
                      VersionTable(tb_name='bombinfo', max_version=1),
                      VersionTable(tb_name='tablecategory', max_version=2),
                      VersionTable(tb_name='relationtable', max_version=1),
                      VersionTable(tb_name='checklist', max_version=1),
                      VersionTable(tb_name='imgtable', max_version=1),
                      VersionTable(tb_name='usertable', max_version=1),
                     ]
        VersionTable.objects.bulk_create(result_list)
        User.objects.create(
            type=0, name="admin", account="admin",
            pwd=md5("admin"), phone="", visible=1, audit=2, version=1
        ).save()

        with open('BombApp/CountryName.json','r',encoding="utf-8") as f:
            data = json.loads(f.read())
            for key, value in data.items():
                cate_id = CategoryTable.objects.create(
                    pid=0, tb='bombinfo', tbid=0, name=key, visible=1, type=2, version=2
                )
                cate_id.save()
                for v in value:
                    cate_id1 = CategoryTable.objects.create(
                        pid=cate_id.id, tb='bombinfo', tbid=0, name=v, visible=1, type=2, version=2
                    )
                    cate_id1.save()

    vers = json.loads(request.body)['data']
    rt = dict(ver=HelpGet(VersionTable.objects.all()), data={})
    for ver in vers:
       tb = MP_TABLE[ver['tb_name']]
       rt["data"][ver['tb_name']] = HelpGet(tb.objects.filter(version__gt=ver['max_version']).all())
    return JsonResponse(rt, safe=False)


@loginValid_user()
def uploadimg(request):
    if request.method == 'POST':
        obj = request.FILES.get('file')
        # reg = re.compile('(.*?(.jpg|.png|.bmp|.jpeg)$)')
        # if not reg.findall(obj.name):
        #     return JsonResponse({'success': 0, 'msg': 0})
        bs = b''
        for chunk in obj.chunks():
            bs += chunk
        m = hashlib.md5()
        m.update(bs)
        file = m.hexdigest()
        f = open(
            os.path.join(
                settings.BASE_DIR, 'static', file
            ), 'wb')
        for chunk in obj.chunks():
            f.write(chunk)
        f.close()
        paths = '/static/'+file

        result = ImgTable.objects.filter(
            md5=file
        ).values()
        if result:
            img_data = result[0]['id']
        else:
            verDict = dict()
            for ver in VersionTable.objects.all().values():
                verDict[ver['tb_name']] = ver['max_version']
                if ver['tb_name'] in ['imgtable']:
                    ver['max_version'] += 1
                    VersionTable.objects.filter(tb_name=ver['tb_name']).update(max_version=ver['max_version'])

            img_datas = ImgTable.objects.create(
                md5=file,
                paths=paths,
                version=verDict['imgtable'] + 1
            )
            img_datas.save()
            img_data = img_datas.id
        return JsonResponse({'success': 1, 'msg': 0, 'id': img_data})


@loginValid_user()
def addcategory(request):
    cates = json.loads(request.body)

    if cates['pid'] != 0:
        result = CategoryTable.objects.filter(id=cates['pid']).values()
        if len(result) > 0:
            if result[0]['visible'] == 0:
                return JsonResponse({"success": 0, 'msg': 201})
        else:
            return JsonResponse({'success': 0, 'msg': 200})

    ver = VersionTable.objects.filter(tb_name='tablecategory').values()[0]
    cates['version'] = ver['max_version']+1
    cates['visible'] = 1
    cates_datas = CategoryTable.objects.create(**cates)
    cates_datas.save()
    VersionTable.objects.filter(tb_name='tablecategory').update(max_version=ver['max_version']+1)

    return JsonResponse({"success": 1, "msg": 0})


@loginValid_user()
def addrelation(request):
    add_data = json.loads(request.body)
    verDict = dict()
    for ver in VersionTable.objects.all().values():
        verDict[ver['tb_name']] = ver['max_version']
        if ver['tb_name'] in ['relationtable']:
            ver['max_version'] += 1
            VersionTable.objects.filter(tb_name=ver['tb_name']).update(max_version=ver['max_version'])

    add_data['audit'] = 0
    add_data['version'] = verDict['relationtable'] + 1
    res = RelationTable.objects.create(**add_data)
    res.save()

    return JsonResponse({"success": 1, "msg": 0})


@loginValid_user()
def addlib(request):
    add_data = json.loads(request.body)
    # if add_data['data']['type'] == 1:
    #     result = CategoryTable.objects.filter(
    #         id=add_data['parentId'],
    #         visible=1
    #     ).values()
    #     if not result:
    #         return JsonResponse({'success': 0, 'msg': 0})

    verDict = dict()
    for ver in VersionTable.objects.all().values():
        verDict[ver['tb_name']] = ver['max_version']
        if ver['tb_name'] in ['simplelib', 'tablecategory', 'checklist']:
            ver['max_version'] += 1
            VersionTable.objects.filter(tb_name=ver['tb_name']).update(max_version=ver['max_version'])

    add_data['data']['audit'] = 0
    add_data['data']['version'] = verDict['simplelib'] + 1
    sim = Simplelib.objects.create(**add_data['data'])
    sim.save()
    # pid = 0
    #     # if add_data['data']['type'] == 1:
    pid = add_data['parentId']
    CategoryTable.objects.create(
        pid=pid, tb='simplelib',type=add_data['data']["type"],
        tbid=sim.id, visible=1, name=sim.zhname, version=verDict['tablecategory'] + 1
    ).save()

    account = request.session.get('account')
    if add_data['data']['type'] == 0:
        content = "单质库 " + add_data['data']['zhname']
    else:
        content = "混合库 " + add_data['data']['zhname']
    CheckTable.objects.create(
        stb="simplelib", sid=sim.id, tid=None,
        account=account, content=content, time=time.time(),
        method=0, audit=0, version=verDict['checklist'] + 1
    ).save()

    return JsonResponse({'success': 1, 'msg': 0, 'id': sim.id})


@loginValid_user()
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
        pid=add_datas['parentId'], tb='bombinfo',type=2,
        tbid=bomb.id, visible=1, name=add_datas['data']['casename'], version=verDict['tablecategory'] + 1
    ).save()

    account = request.session.get('account')
    content = "爆炸案 " + add_datas['data']['addr']
    CheckTable.objects.create(
        stb="bombinfo", sid=bomb.id, tid=None,
        account=account, content=content, time=time.time(),
        method=0, audit=0, version=verDict['checklist'] + 1
    ).save()

    return JsonResponse({'success': 1, 'msg': 0, 'id': bomb.id})


@loginValid_user()
def editcategory(request):
    edit_data = json.loads(request.body)
    cate_id = CategoryTable.objects.filter(id=edit_data['id']).values()
    if len(cate_id) == 0:
        return JsonResponse({"success": 0, 'msg': 500})
    if not cate_id[0]['version'] == edit_data['version']:
        return JsonResponse({"success": 0, 'msg': 501})

    if cate_id[0]['id'] != edit_data['id'] and \
            cate_id[0]['name'] == edit_data['name'] and \
            cate_id[0]['version'] == 1:
        return JsonResponse({"success": 0, 'msg': 502})

    verDict = dict()
    for ver in VersionTable.objects.all().values():
        verDict[ver['tb_name']] = ver['max_version']
        if ver['tb_name'] in ['tablecategory']:
            ver['max_version'] += 1
            VersionTable.objects.filter(tb_name=ver['tb_name']).update(max_version=ver['max_version'])

    CategoryTable.objects.filter(id=edit_data['id']).update(
        name=edit_data['name'], version=verDict['tablecategory'] + 1
    )
    return JsonResponse({"success": 1, 'msg': 0})


@loginValid_user()
def editlib(request):
    edit_data = json.loads(request.body)
    data_id = Simplelib.objects.filter(id=edit_data['data']['id']).values()
    if len(data_id) == 0:
        return JsonResponse({"success": 0, 'msg': 600})
    if not data_id[0]['version'] == edit_data['data']['version']:
        return JsonResponse({"success": 0, 'msg': 601})
    if data_id[0]['id'] != edit_data['data']['id'] and \
            data_id[0]['name'] == edit_data['data']['name'] and \
            data_id[0]['version'] == 1:
        return JsonResponse({"success": 0, 'msg': 602})

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

    account = request.session.get('account')
    if edit_data['data']['type'] == 0:
        content = "单质库 " + edit_data['data']['zhname']
    else:
        content = "混合库 " + edit_data['data']['zhname']
    CheckTable.objects.create(
        stb="simplelib", sid=sim.id, tid=data_id,
        account=account, content=content, time=time.time(),
        method=1, audit=0, version=verDict['checklist'] + 1
    ).save()

    return JsonResponse({'success': 1, 'msg': 0, 'id': sim.id})


@loginValid_user()
def editexplosion(request):
    edit_data = json.loads(request.body)
    info_id = Bombinfo.objects.filter(id=edit_data['data']['id']).values()
    if len(info_id) == 0:
        return JsonResponse({"success": 0, 'msg': 700})
    verDict = dict()
    for ver in VersionTable.objects.all().values():
        verDict[ver['tb_name']] = ver['max_version']
        if ver['tb_name'] in ['bombinfo', 'checklist']:
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

        account = request.session.get('account')
        content = "爆炸案 " + edit_data['data']['addr']
        CheckTable.objects.create(
            stb="bombinfo", sid=bomb.id, tid=edit_id,
            account=account, content=content, time=time.time(),
            method=1, audit=0, version=verDict['checklist'] + 1
        ).save()
        return JsonResponse({'success': 1, 'msg': 0, 'id': bomb.id})

    return JsonResponse({"success": 0, 'msg': 701})


@loginValid_user(checktype=True)
def deletecategory(request):
    delete_data = json.loads(request.body)
    delete_id = CategoryTable.objects.filter(
        pid=delete_data['id'],
        visible=1
    ).values()
    if len(delete_id) != 0:
        return JsonResponse({"success": 0, 'msg': 0})

    verDict = dict()
    for ver in VersionTable.objects.all().values():
        verDict[ver['tb_name']] = ver['max_version']
        if ver['tb_name'] in ['tablecategory', 'simplelib', 'bombinfo']:
            ver['max_version'] += 1
            VersionTable.objects.filter(tb_name=ver['tb_name']).update(max_version=ver['max_version'])

    CategoryTable.objects.filter(
        id=delete_data['id']
    ).update(
        visible=0,
        version=verDict['tablecategory'] + 1
    )

    tbid_result = CategoryTable.objects.filter(
        id=delete_data['id']
    ).values()
    if tbid_result[0]['tbid'] != 0:
        if tbid_result[0]['tb'] == 'simplelib':
            Simplelib.objects.filter(
                    id=tbid_result[0]['tbid']
                ).update(
                    visible=0,
                    version=verDict['simplelib'] + 1
                )
        if tbid_result[0]['tb'] == 'bombinfo':
            Bombinfo.objects.filter(
                id=tbid_result[0]['tbid']
            ).update(
                visible=0,
                version=verDict['bombinfo'] + 1
            )

    return JsonResponse({"success": 1, 'msg': 0})


@loginValid_user(checktype=True)
def audittags(request):
    if request.method == 'POST':
        # user = User.objects.filter(
        #     account=request.session.get('account'),
        #     type=0
        # ).values()
        # if user:
        audit_data = json.loads(request.body)
        preaudit = audit_data['audit']

        verDict = dict()
        for ver in VersionTable.objects.all().values():
            verDict[ver['tb_name']] = ver['max_version']
            if ver['tb_name'] in ['simplelib', 'bombinfo', 'tablecategory', 'relationtable', 'checklist']:
                ver['max_version'] += 1
                VersionTable.objects.filter(tb_name=ver['tb_name']).update(max_version=ver['max_version'])

        checklist = CheckTable.objects.filter(
            id__in=audit_data['ids'],
            audit=0
        ).order_by('-time').values()
        for list in checklist:
            if list['stb'] == 'simplelib':
                if list['method'] != 2:
                    edittag = Simplelib.objects.filter(
                        id=list['sid'],
                    ).values()
                else:
                    edittag = Simplelib.objects.filter(
                        id=list['tid'],
                    ).values()
                if edittag and edittag[0]['type'] == 0:
                    list['content'] = '单质库 ' + edittag[0]['zhname']
                # print(edittag)
                if edittag and edittag[0]['type'] == 1:
                    list['content'] = '混合库 ' + edittag[0]['zhname']

                Simplelib.objects.filter(
                    id=edittag[0]["id"]
                ) .update(audit=preaudit,version=verDict['simplelib'] + 1)
            else:
                if list['method'] != 2:
                    edittag = Bombinfo.objects.filter(id=list['sid']).values()
                else:
                    edittag = Bombinfo.objects.filter(id=list['tid']).values()
                if edittag:
                    list['content'] = '爆炸案 ' + edittag[0]['casename']
                    Bombinfo.objects.filter(
                        id=edittag[0]["id"]
                    ).update(audit=preaudit,version=verDict['bombinfo'] + 1)
            CheckTable.objects.filter(
                version=list['version']
            ).update(content=list['content'],audit=preaudit,version=verDict['checklist'] + 1)

            RelationTable.objects.filter(
                sid=edittag[0]['id'],
                stb=list['stb'],
                audit=0
            ).update(audit=preaudit, version=verDict['relationtable'] + 1)

            if list['method'] == 2 and preaudit == 2:
                if list['stb'] == 'simplelib':
                    Simplelib.objects.filter(
                        id=list["tid"]
                    ).update(visible=0)
                if list['stb'] == 'bombinfo':
                    Bombinfo.objects.filter(
                        id=list["tid"]
                    ).update(visible=0)

            if list['method'] == 1 and preaudit == 2:
                if list['stb'] == 'simplelib':
                    Simplelib.objects.filter(
                        id=list['tid'],
                        audit=2,
                        visible=1
                    ).update(visible=0, version=verDict['simplelib'] + 1)
                    CategoryTable.objects.filter(
                        tbid=list['tid'],
                        tb='simplelib',
                        visible=1
                    ).update(
                        name=edittag[0]['zhname'],
                        tbid=edittag[0]['id'],
                        version=verDict['tablecategory'] + 1)

                else:
                    Bombinfo.objects.filter(
                        id=list['tid'],
                        audit=2,
                        visible=1
                    ).update(visible=0, version=verDict['bombinfo'] + 1)

                    CategoryTable.objects.filter(
                        tbid=list['tid'],
                        tb='bombinfo',
                        visible=1
                    ).update(
                        name=edittag[0]['casename'],
                        tbid=edittag[0]['id'],
                        version=verDict['tablecategory'] + 1)

                CheckTable.objects.filter(
                    tid=list['tid']
                ).update(tid=edittag[0]['id'])

        return JsonResponse({"success": 1, 'msg': 0})

    # return JsonResponse({"success": 0, 'msg': 0})




def login(request):
    if request.method == "POST" and request.POST:
        account = request.POST.get('account')
        pwd = request.POST.get('pwd')
        users = User.objects.filter(
            account=account,
            visible=1
        ).first()
        if users and md5(pwd) == users.pwd:
            response = JsonResponse({'success': 1, 'msg': 0})
            account_session = request.session.get('account', None)
            # print(account_session)
            if account_session:
                request.session.flush()
            request.session['account'] = users.account
            return response
        return JsonResponse({'success': 0, 'msg': 0})


def registerrequest(request):
    if request.method == 'POST':
        register = json.loads(request.body)
        register_data = User.objects.filter(
            account=register['account'],
            visible=1
        ).first()
        if register_data:
            return JsonResponse({'success': 0, 'msg': 0})
        else:
            verDict = dict()
            for ver in VersionTable.objects.all().values():
                verDict[ver['tb_name']] = ver['max_version']
                if ver['tb_name'] in ['usertable']:
                    ver['max_version'] += 1
                    VersionTable.objects.filter(tb_name=ver['tb_name']).update(max_version=ver['max_version'])

            register['type'] = 1
            register['pwd'] = md5(register['pwd'])
            register['visible'] = 1
            register['audit'] = 0
            register['version'] = verDict['usertable'] + 1
            User.objects.create(**register).save()

            return JsonResponse({'success': 1, 'msg': 0})

@loginValid_user(checktype=True)
def registeruser(request):
    if request.method == "POST":
        register_data = json.loads(request.body)
        users = User.objects.filter(
            account=register_data['account'],
            visible=1
        ).values()
        if not users:
            verDict = dict()
            for ver in VersionTable.objects.all().values():
                verDict[ver['tb_name']] = ver['max_version']
                if ver['tb_name'] in ['usertable']:
                    ver['max_version'] += 1
                    VersionTable.objects.filter(tb_name=ver['tb_name']).update(max_version=ver['max_version'])

            register_data['pwd'] = md5(register_data['pwd'])
            register_data['visible'] = 1
            register_data['audit'] = 2
            register_data['version'] = verDict['usertable'] + 1
            User.objects.create(**register_data).save()

            return JsonResponse({'success': 1, 'msg': 0})
        return JsonResponse({'success': 0, 'msg': 0})



@loginValid_user(checktype=True)
def audituser(request):
    if request.method == "POST" and request.POST:
        user = User.objects.filter(
            id=request.POST.get('id'),
            visible=1
        ).values()
        if user:

            verDict = dict()
            for ver in VersionTable.objects.all().values():
                verDict[ver['tb_name']] = ver['max_version']
                if ver['tb_name'] in ['usertable']:
                    ver['max_version'] += 1
                    VersionTable.objects.filter(tb_name=ver['tb_name']).update(max_version=ver['max_version'])

            User.objects.filter(
                id=request.POST.get('id'),
            ).update(
                audit=request.POST.get('audit'),
                version=verDict['usertable'] + 1
            )
            return JsonResponse({'success': 1, 'msg': 0})
        return JsonResponse({'success': 0, 'msg': 0})


@loginValid_user(checktype=True)
def edituserinfo(request):
    if request.method == 'POST':
        edit_data = json.loads(request.body)
        user = User.objects.filter(
            account=edit_data['account'],
            visible=1
        ).first()
        if not user:
            return JsonResponse({'success': 0, 'msg': 0})

        verDict = dict()
        for ver in VersionTable.objects.all().values():
            verDict[ver['tb_name']] = ver['max_version']
            if ver['tb_name'] in ['usertable']:
                ver['max_version'] += 1
                VersionTable.objects.filter(tb_name=ver['tb_name']).update(max_version=ver['max_version'])

        if edit_data['pwd'] == '':
            User.objects.filter(
                account=edit_data['account'],
                visible=1
            ).update(
                name=edit_data['name'],
                account=edit_data['account'],
                phone=edit_data['phone'],
                type=edit_data['type'],
                version=verDict['usertable'] + 1
            )
        else:
            edit_data['pwd'] = md5(edit_data['pwd'])
            User.objects.filter(
                account=edit_data['account'],
                visible=1
            ).update(
                name=edit_data['name'],
                account=edit_data['account'],
                pwd=md5(edit_data['pwd']),
                phone=edit_data['phone'],
                type=edit_data['type'],
                version=verDict['usertable'] + 1
            )

        return JsonResponse({'success': 1, 'msg': 0})


@loginValid_user(checktype=True)
def deleteuser(request):
    if request.method == 'POST' and request.POST:
        user = User.objects.filter(
            id=request.POST.get('id')
        ).first()
        if user:
            verDict = dict()
            for ver in VersionTable.objects.all().values():
                verDict[ver['tb_name']] = ver['max_version']
                if ver['tb_name'] in ['usertable']:
                    ver['max_version'] += 1
                    VersionTable.objects.filter(tb_name=ver['tb_name']).update(max_version=ver['max_version'])

            User.objects.filter(
                id=request.POST.get('id')
            ).update(visible=0, version=verDict['usertable'] + 1)
            return JsonResponse({'success': 1, 'msg': 0})
        return JsonResponse({'success': 0, 'msg': 0})

