# 用于设置model serializers
from rest_framework import viewsets, serializers, status
import os, uuid, time, random
from django.db import transaction
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.hashers import make_password
from app import models


class networkAssetsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.networkAssets
        fields = ["id", "deviceNumber", "ip", "device_type", "port", "address", "createTime", ]
        # depth = 3


class orgAssetsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.orgAssets
        fields = ["id", "title", "desc", ]
