from django.shortcuts import render
import redis
from django.conf import settings
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import generics, status



# simple pooling and validating the connections with redis 
redis_client = redis.Redis.from_url(settings.REDIS_URL)