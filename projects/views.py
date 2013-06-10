from django.views.generic.edit import DeleteView, UpdateView
from django.core.urlresolvers import reverse_lazy, reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, Http404, get_object_or_404
from django.template import RequestContext
from django.contrib.auth.models import User
from projects.models import Project, Task, FileUpload
from django.contrib.auth.decorators import login_required
from projects.forms import RegistrationForm, LoginForm, ProjectForm, TaskForm
from django.contrib.auth import authenticate, login, logout
from helper_tasks import all_tasks, forhandler
from django.db.models import Q
from django.utils import simplejson
from django.views.decorators.csrf import csrf_exempt
from filetransfers.api import serve_file
import os
from django.conf import settings
import mimetypes
from django.core.servers.basehttp import FileWrapper


def download_course(request, pk):
    file = FileUpload.objects.get(id=pk)
    #
    path = file.file  # Get file path
    the_file = '%s/%s' % (settings.MEDIA_ROOT, path)
    filename = os.path.basename(the_file)
    response = HttpResponse(FileWrapper(open(the_file)), content_type=mimetypes.guess_type(the_file)[0])
    response['Content-Length'] = os.path.getsize(the_file)
    response['Content-Disposition'] = "attachment; filename=%s" % filename
    return response


@login_required
def download_handler(request, pk):
    upload = get_object_or_404(FileUpload, pk=pk)
    return serve_file(request, upload.file)


@login_required
def add_project(request):
    """
        view to display the form to add a new project
    """
    #make sure form was submitted via post
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            form.instance.user_id = request.user.id
            form.save()
            #redirect to home after successful save
            return HttpResponseRedirect('/')
        else:
            context = {'form': form}
            return render_to_response('add_project.html', context, context_instance=RequestContext(request))
    else:
        return render_to_response('add_project.html', {'form': ProjectForm()}, context_instance=RequestContext(request))


@csrf_exempt
@login_required
def add_task(request, project_id):
    """
        view to display the form to add a new task
    """
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            form.instance.user_id = request.user.id
            form.instance.project_id = project_id
            form.save()
            forhandler(request.FILES.getlist('file[]'), project_id, form.instance.id, request)
            #redirect to home after successful save
            #return HttpResponseRedirect('/')
            return HttpResponseRedirect(
                reverse('projects.views.task_detail',
                        kwargs={'task_id': form.instance.id, },
                        ))
        else:
            context = {'form': form}
            return render_to_response('add_task.html', context, context_instance=RequestContext(request))
    else:
        return render_to_response('add_task.html', {'form': TaskForm(), 'project_id': project_id}, context_instance=RequestContext(request))


def ProjectRegistration(request):
        if request.user.is_authenticated():
                return HttpResponseRedirect('/profile/')
        if request.method == 'POST':
                form = RegistrationForm(request.POST)
                if form.is_valid():
                        user = User.objects.create_user(username=form.cleaned_data['username'], email = form.cleaned_data['email'], password = form.cleaned_data['password'])
                        user.save()
                        #drinker = Drinker(user=user, name=form.cleaned_data['name'], birthday=form.cleaned_data['birthday'])
                        #drinker.save()
                        return HttpResponseRedirect('/profile/')
                else:
                        return render_to_response('register.html', {'form': form}, context_instance=RequestContext(request))
        else:
                ''' user is not submitting the form, show them a blank registration form '''
                form = RegistrationForm()
                context = {'form': form}
                return render_to_response('register.html', context, context_instance=RequestContext(request))


def LoginRequest(request):
        if request.user.is_authenticated():
                return HttpResponseRedirect('/profile/')
        if request.method == 'POST':
                form = LoginForm(request.POST)
                if form.is_valid():
                        username = form.cleaned_data['username']
                        password = form.cleaned_data['password']
                        user = authenticate(username=username, password=password)
                        if user is not None:
                                login(request, user)
                                return HttpResponseRedirect('/profile/')

                        else:
                                return render_to_response('login.html', {'user_invalid': "invalid user id or password", 'form':form}, context_instance=RequestContext(request))
                else:
                        return render_to_response('login.html', {'form': form}, context_instance=RequestContext(request))
        else:
                ''' user is not submitting the form, show the login form '''
                form = LoginForm()
                context = {'form': form}
                return render_to_response('login.html', context, context_instance=RequestContext(request))


def LogoutRequest(request):
        logout(request)
        return HttpResponseRedirect('/')


def Project_page(request):
    projects = {}
    if request.user.is_authenticated():
        user = request.user.username
        rel_user = User.objects.get(username=user)
        projects = rel_user.project_set.all()
        return render_to_response('projects.html', {'projects': projects}, context_instance=RequestContext(request))
    return HttpResponseRedirect('/')


@login_required
def task_page(request):
    user = request.user.username
    rel_user = User.objects.get(username=user)
    tasks = rel_user.task_set.all()
    return render_to_response('tasks.html', {'tasks': tasks}, context_instance=RequestContext(request))


@login_required
def individual_task_page(request, project_id):
    user = request.user.username
    project = Project.objects.get(id=project_id)
    tasks = project.task_set.all()
    return render_to_response('individual_tasks.html', {'tasks': tasks, 'project': project}, context_instance=RequestContext(request))


@login_required
def edit_project(request, project_id):
    try:
        project_id = Project.objects.get(id=project_id)
    except User.DoesNotExist:
        raise Http404
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project_id)
        if form.is_valid():
            project_id = form.save()
            return HttpResponseRedirect('/profile/')
    else:
        form = ProjectForm(instance=project_id)
    return render_to_response('update_project.html', {'form': form}, context_instance=RequestContext(request))


@login_required
def project_detail(request, project_id):
    """
        view to display shipment detail, it takes shipment_id and request
    """
    #ensure a project with the project_id passed exists otherwise emit a 404
    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        raise Http404
    context = {'project': project}
    return render_to_response('project_detail.html', context, context_instance=RequestContext(request))


@login_required
def task_detail(request, task_id):
    """
        view to display shipment detail, it takes shipment_id and request
    """
    #ensure a task with the task_id passed exists otherwise emit a 404
    try:
        task = Task.objects.get(id=task_id)
        attachments = task.fileupload_set.all()
    except Task.DoesNotExist:
        raise Http404
    context = {'task': task, 'attachments': attachments}
    return render_to_response('task_detail.html', context, context_instance=RequestContext(request))


#@login_required
class ProjectDelete(DeleteView):
    model = Project
    success_url = reverse_lazy('allprojects')


#@login_required
class TaskDelete(DeleteView):
    model = Task
    success_url = reverse_lazy('alltasks')


class TaskUpdate(UpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'projects/task_update_form.html'
    success_url = '/tasks/'


@login_required
def project_search(request):
    if 'term' in request.GET and request.GET['term']:
        q = request.GET['term']
        ret = []
        user_rel = User.objects.get(username=request.user)
        listado = projects = user_rel.project_set.filter(Q(project_name__icontains=q)).order_by('project_name')
        for l in listado:
                ret.append({'label': l.project_name, 'id': l.id})
        return HttpResponse(simplejson.dumps(ret), mimetype='application/json')
    if 'query' in request.GET and request.GET['query']:
        query = request.GET['query']
        projects = Project.objects.filter(Q(project_name__icontains=query)
                                          | Q(environment__icontains=query)).order_by('project_name')
        context = {'projects': projects, 'query': query}
        return render_to_response('project_search.html', context, context_instance=RequestContext(request))
    else:
        return render_to_response('project_search.html', {'error': 'An error occurred'},
                                  context_instance=RequestContext(request))


@login_required
def delete_file(request, file_id):
        f = FileUpload.objects.get(id=file_id)
        ID = f.task_id
        f.file.delete()
        f.delete()
        return HttpResponseRedirect(
  reverse('projects.views.task_detail',
    kwargs={
      'task_id': ID,
    },
  )
)