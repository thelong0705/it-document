from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from .models import Category


class PostCategoryAPI(APIView):
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = [permissions.IsAuthenticated, ]

    def get(self, request, category_name):
        obj = None
        if category_name == '' or category_name is None:
            created = False
        else:
            obj, created = Category.objects.get_or_create(name=category_name)
        data = {
            "created": created,
            "pk": obj.pk
        }
        return Response(data=data)
