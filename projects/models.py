from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User


class Project(models.Model):
    user = models.ForeignKey(User)
    project_name = models.CharField(max_length=100)
    environment = models.CharField(max_length=30)

    def __unicode__(self):
        return self.project_name


class Task(models.Model):
    user = models.ForeignKey(User)
    project = models.ForeignKey(Project)
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=200)

    def __unicode__(self):
        return self.name


class FileUpload(models.Model):
    project = models.ForeignKey(Project)
    task = models.ForeignKey(Task)
    file = models.FileField(upload_to='documents/%Y/%m/%d')
    filetype = models.CharField(max_length=20)

    def __unicode__(self):
        return self.file


class Skills(models.Model):
    name = models.CharField(max_length=20)
    desc = models.TextField(verbose_name='Description')

    def __unicode__(self):
        return self.name


#def do_something(sender, instance, **kwargs):
#    # the object which is saved can be accessed via kwargs 'instance' key.
#    project.new = Project.objects.get_or_create(user=instance)
#    print 'the object is now saved.'
#post_save.connect(do_something, User)