#!/usr/bin/env python

from django.contrib.auth.models import User
from projects.models import *


def all_tasks(list, request):
    print list
    for i in list:
        #extension = i.content_type
        print request.FILES


def forhandler(list, project_id, task_id, request):
    for i in list:
        filename = i
        extension = filename.content_type
        print i
        newdoc = FileUpload(project_id=project_id, task_id=task_id, file=filename, filetype=extension)
        newdoc.save()