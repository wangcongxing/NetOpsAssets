from django.db import models
import uuid


# Create your models here.

def newguid():
    return str(uuid.uuid4())


device_level_choices = (
    (0, "网点设备"),
    (1, "核心设备"),
)
device_state_choices = ((0, "在用"),
                        (1, "备用"), (2, "停用"),)


# 授权登录用户
class loginUserInfo(models.Model):
    username = models.CharField(max_length=255, default="", blank=True, null=True, verbose_name="用户名", )
    password = models.TextField(max_length=5000, default="", blank=True, null=True, verbose_name="密码", )
    createTime = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    lastTime = models.DateTimeField(auto_now=True, verbose_name="修改时间")
    creator = models.CharField(max_length=255, default="", blank=True, null=True, verbose_name="创建者", )
    editor = models.CharField(max_length=255, default="", blank=True, null=True, verbose_name="修改者", )

    class Meta:
        verbose_name = verbose_name_plural = '登录用户'


# 资产组织架构

class orgAssets(models.Model):
    title = models.CharField(verbose_name='菜单名称', max_length=255, default="", null=True, blank=True, )

    parent = models.ForeignKey('self', verbose_name='所属一级菜单', help_text='null表示不是菜单，否则为二级菜单', null=True, blank=True,
                               related_name='children', on_delete=models.CASCADE)
    sort = models.IntegerField(verbose_name='显示顺序', default=1)

    desc = models.TextField(verbose_name='描述', max_length=50000, blank=True, default="")

    createTime = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    lastTime = models.DateTimeField(auto_now=True, verbose_name="修改时间")
    creator = models.CharField(max_length=255, default="", blank=True, null=True, verbose_name="创建者", )
    editor = models.CharField(max_length=255, default="", blank=True, null=True, verbose_name="修改者", )

    def __str__(self):  # 循环查找父菜单返回字符串 self-parent-parent
        return self.title

    class MPTTMeta:
        parent_attr = 'parent'

    class Meta:
        verbose_name = verbose_name_plural = '资产组织架构'


# 网络设备 需要组织架构 跑批统一由Nornir负责
class networkAssets(models.Model):
    orgassets = models.ForeignKey(orgAssets, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="物理位置",
                                  related_name="orgassets")
    deviceNumber = models.CharField(max_length=255, default="", blank=True, null=True, verbose_name="设备编号", )
    ip = models.GenericIPAddressField(max_length=255, default="", blank=True, null=True, verbose_name="IP", )
    mip = models.GenericIPAddressField(max_length=255, default="", blank=True, null=True, verbose_name="管理IP", )
    deviceType = models.CharField(max_length=255, null=True, blank=True, verbose_name="设备类型", )
    deviceLevel = models.IntegerField(null=True, blank=True, verbose_name="设备等级",
                                       choices=device_level_choices)
    port = models.IntegerField(verbose_name="端口", blank=True, null=True, default=22)
    address = models.TextField(max_length=5000, default="", blank=True, null=True, verbose_name="位置详情", )
    username = models.CharField(verbose_name="用户名", max_length=255, blank=True, null=True, default="")
    password = models.CharField(verbose_name="密码", max_length=255, blank=True, null=True, default="")
    logicAddress = models.CharField(max_length=255, default="", blank=True, null=True, verbose_name="逻辑位置", )
    dState = models.CharField(max_length=255, default="", blank=True, null=True, verbose_name="设备状态",
                              choices=device_state_choices)
    islogin = models.CharField(max_length=255, default="", blank=True, null=True, verbose_name="连接状态", )
    principal = models.TextField(max_length=5000, default="", blank=True, null=True, verbose_name="负责人", )
    desc = models.TextField(max_length=5000, default="", blank=True, null=True, verbose_name="描述", )
    createTime = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    lastTime = models.DateTimeField(auto_now=True, verbose_name="修改时间")
    creator = models.CharField(max_length=255, default="", blank=True, null=True, verbose_name="创建者", )
    editor = models.CharField(max_length=255, default="", blank=True, null=True, verbose_name="修改者", )

    class Meta:
        verbose_name = verbose_name_plural = '网络设备'
