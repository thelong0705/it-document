from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions, status
from .models import Category
from it_document.utils import unslugify


class PostCategoryAPI(APIView):
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = [permissions.IsAuthenticated, ]

    def get(self, request, category_name):
        if category_name == '' or category_name is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        category_name = unslugify(category_name)
        obj, created = Category.objects.get_or_create(name=category_name)
        data = {
            "created": created,
            "pk": obj.pk
        }
        return Response(data=data)

