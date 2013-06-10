from django.conf.urls import patterns, include, url
from projects.views import ProjectDelete, TaskDelete, TaskUpdate
from django.contrib.auth.decorators import login_required
import settings
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
                       (r'^register/$', 'projects.views.ProjectRegistration'),
                       (r'^$', 'projects.views.LoginRequest'),
                       url(r'^edit/(?P<project_id>\d+)$', 'projects.views.edit_project', name='editproject'),
                       url(r'^edittask/(?P<pk>\d+)$', login_required(TaskUpdate.as_view()), name='edittask'),
                       (r'^logout/$', 'projects.views.LogoutRequest'),
                       (r'^add_project/$', 'projects.views.add_project'),
                       url(r'^addtask/(?P<project_id>\d+)$', 'projects.views.add_task', name='taskadd'),
                       url(r'^profile/$', 'projects.views.Project_page', name='allprojects'),
                       url(r'^tasks/$', 'projects.views.task_page', name='alltasks'),
                       (r'^detail/(?P<project_id>\d+)$', 'projects.views.project_detail'),
                       (r'^taskdetail/(?P<task_id>\d+)$', 'projects.views.task_detail'),
                       (r'^projecttasks/(?P<project_id>\d+)$', 'projects.views.individual_task_page'),
                       (r'^download/(?P<pk>\d+)$', 'projects.views.download_course'),
                       url(r'^delete/(?P<pk>\d+)$', login_required(ProjectDelete.as_view()), name='delete'),
                       url(r'^imagedelete/(?P<file_id>\d+)$', 'projects.views.delete_file', name='deletefile'),
                       url(r'^deletetask/(?P<pk>\d+)$', login_required(TaskDelete.as_view()), name='deletetask'),
                       url(r'^projectsearch/$', 'projects.views.project_search', name='searchproject'),
    # Examples:individual_task_page
    # url(r'^$', 'projectstat.views.home', name='home'),
    # url(r'^projectstat/', include('projectstat.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes':False}),
)
