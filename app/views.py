from django.db import transaction
from django.shortcuts import render
from rest_framework.decorators import action
from rest_framework import viewsets, serializers, status
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import RetrieveAPIView
from rest_framework.pagination import PageNumberPagination
from app import models, modelFilters, modelSerializers, modelPermission
from utils import APIResponseResult
from utils.CustomViewBase import CustomViewBase
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.hashers import make_password
from django.db.models import Q
from rest_framework.views import APIView
import os, uuid, time
from rest_framework_jwt.settings import api_settings
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect

import json
from datetime import datetime, timedelta
from django.db import transaction
from rest_framework import generics, mixins, views, viewsets
from django_filters import rest_framework as filters
import ast

# Create your views here.

ENV_PROFILE = os.getenv("ENV")
if ENV_PROFILE == "pro":
    from NetOpsAssets import pro_settings as config
elif ENV_PROFILE == "test":
    from NetOpsAssets import test_settings as config
else:
    from NetOpsAssets import settings as config


# 默认数据初始化
class opsBaseInitDB(APIView):
    authentication_classes = ()
    permission_classes = ()

    def get(self, request, *args, **kwargs):
        # 新建超级用户
        # 新建超级用户
        superUser, ctime = User.objects.update_or_create(
            defaults={'username': 'admin', 'is_staff': True, 'is_active': True, 'is_superuser': True,
                      'first_name': '管理员',
                      'password': make_password("admin@123")}, username='admin')
        superUser = superUser.username
        assetsJson = []
        with open(os.path.join(config.BASE_DIR, 'initConf', "assets.json"), "r") as f:
            assetsJson = json.load(f)
        for item in assetsJson:
            ccm, cc = models.networkAssets.objects.update_or_create(
                defaults={"deviceNumber": item["deviceNumber"], "ip": item["ip"], "mip": item["mip"],
                          "port": item["port"], "device_type": item["device_type"],
                          'creator': superUser, 'editor': superUser},
                ip=item["ip"])

        orgAssetsJson = []
        with open(os.path.join(config.BASE_DIR, 'initConf', "orgAssets.json"), "r") as f:
            orgAssetsJson = json.load(f)
        for item in orgAssetsJson:
            p, c = models.orgAssets.objects.update_or_create(
                defaults={"title": item["title"], 'creator': superUser, 'editor': superUser},
                id=int(item["id"]))
            if "children" in item.keys():
                children = item["children"]
                for sitem in children:
                    pp, cc = models.orgAssets.objects.update_or_create(
                        defaults={"title": sitem["title"], "parent": p, 'creator': superUser, 'editor': superUser},
                        id=int(sitem["id"]))
                    if "children" in sitem.keys():
                        schildren = sitem["children"]
                        for ssitem in schildren:
                            models.orgAssets.objects.update_or_create(
                                defaults={"title": ssitem["title"], "parent": pp, 'creator': superUser, 'editor': superUser},
                                id=int(ssitem["id"]))

        return HttpResponse("<h1>数据库初始化成功</h1>")


class networkAssetsViewSet(CustomViewBase):
    queryset = models.networkAssets.objects.all().order_by('id')
    serializer_class = modelSerializers.networkAssetsSerializer
    filter_class = modelFilters.networkAssetsFilter
    ordering_fields = ('id',)  # 排序


def get_child_menu(childs):
    children = []
    if childs:
        for child in childs:
            data = {"id": child.id,"title": child.title, "children": []}
            _childs = models.orgAssets.objects.filter(parent=child)
            if _childs:
                data["children"] = get_child_menu(_childs)
            children.append(data)
    return children


class orgAssetsViewSet(CustomViewBase):
    queryset = models.orgAssets.objects.all().order_by('sort')
    serializer_class = modelSerializers.orgAssetsSerializer
    ordering_fields = ('id',)  # 排序

    # 返回左侧菜单
    @action(methods=['get', 'post'], detail=False, url_path='left_org')
    def left_org(self, request, *args, **kwargs):
        # 获得用户权限
        user_id = request.user["user_id"]
        tree = []
        firstmenus = models.orgAssets.objects.filter(parent=None).order_by('sort')
        # print(menus.query)
        for menu in firstmenus:
            menu_data = {"id": menu.id, "title": menu.title, }
            childs = models.orgAssets.objects.filter(parent=menu).order_by('sort')
            if childs:
                menu_data["children"] = get_child_menu(childs)
            tree.append(menu_data)
        # tree = [x for x in tree if x["list"] != []]
        return APIResponseResult.APIResponse(0, 'success', results=tree)
