from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mysite.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^truco/', include('truco.urls'), name = 'truco'),
    url(r'^admin/', include(admin.site.urls)),
)

#from django.conf.urls import patterns, include, url
#from django.contrib import admin

#urlpatterns = patterns('',
#    url(r'^truco/', include('truco.urls', namespace="truco")),
#    url(r'^admin/', include(admin.site.urls)),
#)
