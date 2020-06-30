from django.db import models


# Create your models here.

# 单质库
class Simplelib(models.Model):

    type = models.IntegerField()  # 区别单质还是混合 0表示单质 1混合
    zhname = models.CharField(max_length=256)  # 名称
    enname = models.CharField(max_length=256, null=True)  # 英文名称
    linkable = models.IntegerField()  # 表示是否可以连接  0表示不可以连接 ， 1表示可以连接
    nickname = models.CharField(max_length=256, null=True)  # 别名(俗名)
    cas = models.CharField(max_length=256, null=True)  # CAS号
    formula = models.CharField(max_length=256, null=True)  # 分子式
    formulaWeight = models.CharField(max_length=256, null=True)  # 相对分子质量
    OxygenBalance = models.CharField(max_length=256, null=True)  # 氧平衡
    nitrogen = models.CharField(max_length=256, null=True)  # 含氮量
    relativeDensity = models.CharField(max_length=256, null=True)  # 相对密度
    meltingPoint = models.CharField(max_length=256, null=True)  # 熔点
    boilingPoint = models.CharField(max_length=256, null=True)  # 沸点
    flashPoint = models.CharField(max_length=256, null=True)  # 闪点
    decompTemp = models.CharField(max_length=256, null=True)  # 分解温度
    standardHeat = models.CharField(max_length=256, null=True)  # 标准生成热
    heatCapacity = models.CharField(max_length=256, null=True)  # 热容
    character = models.TextField(null=True)  # 性状
    standardmg = models.CharField(max_length=256, null=True)  # 标准摩尔生成焓
    wettability = models.CharField(max_length=256, null=True)  # 易湿性
    combustionheat = models.CharField(max_length=256, null=True)  # 燃烧热
    burstspeed = models.CharField(max_length=256, null=True)  # 爆速
    temp = models.CharField(max_length=256, null=True)  # 爆温
    bursthot = models.CharField(max_length=256, null=True)  # 爆热
    burstpress = models.CharField(max_length=256, null=True)  # 爆压
    burstvol = models.CharField(max_length=256, null=True)  # 爆容
    burstpoint = models.CharField(max_length=256, null=True)  # 5S爆发点
    frisen = models.TextField(null=True)  # 摩擦感度
    impsen = models.TextField(null=True)  # 撞击感度
    stasen = models.TextField(null=True)  # 静电感度
    explosionlimit = models.TextField(null=True)  # 爆炸极限
    svp = models.CharField(max_length=256, null=True)  # 蒸气压
    img = models.CharField(max_length=256, null=True)  # imgtable表中数据的id列表
    visible = models.IntegerField()  # 删除 0不可见 1可见
    audit = models.IntegerField(default=0)  # 表示是否审核中   0表示审核中 1表示审核未通过 2审核通过
    version = models.IntegerField()  # 版本 版本号表中找最大加1

    class Meta:
        managed = True
        db_table = 'simplelib'


# 爆炸案
class Bombinfo(models.Model):

    casename = models.CharField(max_length=256)  # 按键名称 添加编辑带上
    time = models.IntegerField()  # 时间
    addr = models.CharField(max_length=256)  # 发生地
    casualties = models.CharField(max_length=256)  # 伤亡情况
    visible = models.IntegerField()  # 删除 0不可见 1可见
    audit = models.IntegerField(default=0)  # 表示是否审核中   0表示审核中 1表示审核未通过 2审核通过
    version = models.IntegerField()  # 版本

    class Meta:
        managed = True
        db_table = "bombinfo"


# 类别表
class CategoryTable(models.Model):

    pid = models.IntegerField()  # 父节点id
    tb = models.CharField(max_length=256, null=True)  # 表名
    tbid = models.IntegerField(null=True)  # 表id
    name = models.CharField(max_length=256, null=True)  # 节点名称
    visible = models.IntegerField()  # 表示是否删除，0不可见 1可见
    type = models.IntegerField()  # 库类型 0单质库 1混合库  2备用
    version = models.IntegerField()  # 版本

    class Meta:
        managed = True
        db_table = 'categorytable'


# 关系表
class RelationTable(models.Model):

    audit = models.IntegerField(default=0)  # 审核状态 0表示审核中 1表示审核未通过 2审核通过
    stb = models.CharField(max_length=256, null=True)  # 连接原数据表名
    sid = models.IntegerField(null=True)  # 连接原数据id
    content = models.TextField(null=True)  # 链接内容
    version = models.IntegerField()  # 版本

    class Meta:
        managed = True
        db_table = 'relationtable'


# 审核列表
class CheckTable(models.Model):

    stb = models.CharField(max_length=256, null=True)  # 连接原数据表名
    sid = models.IntegerField(null=True)  # 连接原数据id
    tid = models.IntegerField(null=True)  # 修改目标id
    audit = models.IntegerField(default=0)  # 审核状态 0表示审核中 1表示审核未通过 2审核通过
    method = models.IntegerField()  # 操作方式，0是添加，1是修改，2是删除
    account = models.CharField(max_length=20, null=True)  # 账号
    content = models.TextField(null=True)  # 内容
    time = models.IntegerField(null=True)  # 时间
    version = models.IntegerField()  # 版本

    class Meta:
        managed = True
        db_table = 'checktable'



class ImgTable(models.Model):

    md5 = models.CharField(max_length=256, null=True)  # 对文件内容的md5值计算
    paths = models.CharField(max_length=256, null=True)  # 图片的路径
    version = models.IntegerField()  # 数据版本号

    class Meta:
        managed = True
        db_table = 'imgtable'


class User(models.Model):

    type = models.IntegerField()  # 用户类型 0管理员， 1普通用户
    name = models.CharField(max_length=256)  # 用户名
    account = models.CharField(max_length=256)  # 账户
    pwd = models.CharField(max_length=256)  # 密码
    phone = models.CharField(max_length=256)  # 电话
    visible = models.IntegerField()  # 表示是否删除，0不可见 1可见
    audit = models.IntegerField()   # 审核状态 0表示审核中 1表示审核未通过 2审核通过
    version = models.IntegerField()  # 数据版本号

    class Meta:
        managed = True
        db_table = "usertable"


# 版本号表
class VersionTable(models.Model):
    tb_name = models.CharField(max_length=256)  # 表名
    max_version = models.IntegerField()  # 最大版本号

    class Meta:
        managed = True
        db_table = "versiontable"




MP_TABLE = dict(
    simplelib=Simplelib,
    bombinfo=Bombinfo,
    tablecategory=CategoryTable,
    relationtable=RelationTable,
    checklist=CheckTable,
    imgtable=ImgTable,
    usertable=User,
)

import json
from django.core import serializers
def HelpGet(data):
    f = lambda d: dict(id=d['pk'], **d['fields'])
    return [f(d) for d in json.loads(serializers.serialize('json', data))]

    # rt=[]
    # for d in json.loads(serializers.serialize('json', data)):
    #     rt.append(dict(pk=d['pk'],**d['fields']))
    # return rt