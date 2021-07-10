from django_filters import rest_framework as filters
import django_filters
from django.contrib.auth.models import User, Group, Permission
from app import models


class networkAssetsFilter(filters.FilterSet):
    # 模糊过滤
    deviceNumber = django_filters.CharFilter(field_name="deviceNumber", lookup_expr='icontains')
    ip = django_filters.CharFilter(field_name="ip", lookup_expr='icontains')
    mip = django_filters.CharFilter(field_name="mip", lookup_expr='icontains')

    class Meta:
        model = models.networkAssets
        fields = ['deviceNumber', 'ip', 'mip']




