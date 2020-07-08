"""bomb_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from BombApp.views import *
from BombApp.search import *
urlpatterns = [
    # path('admin/', admin.site.urls),
    path('checkversion', checkversion),
    path('addcategory', addcategory),
    path('addlib', addlib),
    path('addexplosion', addexplosion),
    path('editcategory', editcategory),
    path('editlib', editlib),
    path('editexplosion', editexplosion),
    path('uploadimg', uploadimg),
    path('addrelation', addrelation),
    path('audittags', audittags),
    path('registerrequest', registerrequest),
    path('login', login),
    path('registeruser', registeruser),
    path('audituser', audituser),
    path('edituserinfo', edituserinfo),
    path('deleteuser', deleteuser),
    path('deletecategory', deletecategory),
    path('TezImg', TezImg),
    path('boomRelevanceInf', boomRelevanceInf),
    path('simpleRelevanceInf', simpleRelevanceInf),
    path('nodeTimeBomb', nodeTimeBomb),
    path('simClassify', simClassify),
    path('bombClassify', bombClassify),
    path('moleculeFormat', moleculeFormat),
    path('mixtureIngredient', mixtureIngredient),
]
