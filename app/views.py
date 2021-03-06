from enum import unique
from http.client import HTTPResponse
from msilib.schema import File
from operator import contains
from timeit import repeat
from tokenize import Name
from tracemalloc import stop
from urllib import request
from django import views
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from rdflib import Namespace
from datetime import datetime
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from . import models
import collections, os, sys

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

############################
### Authentication views ###
############################

def login(request):
    if request.user.is_authenticated:
        return redirect('app:index')
    else:
        welcome_message = 'Welcome, please log in using your credentials.'
        return render(request, 'auth/login.html', {'welcome_message':welcome_message})

def login_proceed(request):
    input_username = request.POST.get('username')
    input_password = request.POST.get('password')
    output = models.login_model(request, input_username, input_password)
    if output == 'success':
        first_name = request.user.get_short_name()
        username = request.user.get_username()
        unique_user_id = models.rq_user_id(username)
        request.session['unique_user_id'] = unique_user_id
        return redirect('app:index')
    else:
        welcome_message = 'Welcome, please log in using your credentials.'
        return render(request, 'auth/login.html', {'output':output, 'welcome_message':welcome_message})

def register(request):
    roles = models.rq_roles()
    return render(request, 'auth/register.html', {'roles':roles})
    
def register_proceed(request):
    first_name = request.POST.get('first_name')
    last_name = request.POST.get('last_name')
    email = request.POST.get('email')
    phone_number = request.POST.get('phone_number')
    role = request.POST.get('role')
    roles = models.rq_roles()
    if role not in roles:
        models.add_roles(role)
    username = request.POST.get('email')
    password = request.POST.get('password')
    models.register_model(username, email, password, first_name, last_name, phone_number, role)
    success_message = 'Your account has successfully been created, please log in using your credentials.'
    return render(request, 'auth/login.html', {'welcome_message':success_message})

def logout(request):
    models.logout_model(request)
    return render(request, 'auth/logout.html')

######################
### Settings views ###
######################

@login_required
def settings(request):
    first_name = request.user.get_short_name()
    full_name = request.user.get_full_name()
    email = request.user.get_username()
    user_info = models.rq_settings1(email)
    sparql_endpoint_1 = models.sparql_endpoint_1
    sparql_endpoint_2 = models.sparql_endpoint_2
    document_storage_location = models.document_storage_location
    aim_default_namespace = models.aim_default_namespace
    org_default_namespace = models.o_oms
    current_org = models.current_org
    welcome_message = 'Welcome {}!'.format(first_name)
    return render(request, 'settings/settings.html', {'welcome_message':welcome_message,'first_name':first_name, 'full_name':full_name, 'email':email, 'user_info':user_info, 'sparql_endpoint_1':sparql_endpoint_1, 'sparql_endpoint_2':sparql_endpoint_2, 'document_storage_location':document_storage_location, 'aim_default_namespace':aim_default_namespace, 'org_default_namespace':org_default_namespace, 'current_org':current_org})

@login_required
def edit_org(request):
    first_name = request.user.get_short_name()
    current_org = models.current_org
    existing_users = models.rq_actor3()
    return render(request, 'settings/edit_org.html', {'first_name':first_name, 'current_org':current_org, 'existing_users':existing_users})

@login_required
def edit_org_add(request):
    first_name = request.user.get_short_name()
    roles = models.rq_roles()
    return render(request, 'settings/edit_org_add.html', {'first_name':first_name, 'roles':roles})

@login_required
def edit_org_add_proceed(request):
    first_name = request.user.get_short_name()
    actor_name = request.POST.get('name')
    actor_email = request.POST.get('email')
    actor_phone_number = request.POST.get('phone_number')
    actor_role = request.POST.get('role')
    roles = models.rq_roles()
    if actor_role not in roles:
        models.add_roles(actor_role)
    models.org_add_actor(actor_name, actor_email, actor_phone_number, actor_role)
    message = 'User {} has been added succesfully'.format(actor_name)
    existing_users = models.rq_actor3()
    return render(request, 'settings/edit_org.html', {'first_name':first_name, 'message':message, 'existing_users':existing_users})

@login_required
def edit_org_edit(request):
    first_name = request.user.get_short_name()
    actor_id = request.POST.get('actor_id')
    actor_name = request.POST.get('actor_name')
    actor_email = request.POST.get('actor_email')
    actor_organization = request.POST.get('actor_organization')
    actor_phone_number = request.POST.get('actor_phone_number')
    actor_role = request.POST.get('actor_role')
    roles = models.rq_roles()
    return render(request, 'settings/edit_org_edit.html', {'first_name':first_name, 'actor_id':actor_id, 'actor_name':actor_name, 'actor_email':actor_email, 'actor_organization':actor_organization, 'actor_phone_number':actor_phone_number, 'actor_role':actor_role, 'roles':roles})

@login_required
def edit_org_edit_proceed(request):
    first_name = request.user.get_short_name()
    actor_id = request.POST.get('id')
    actor_name = request.POST.get('name')
    actor_phone_number_new = request.POST.get('phone_number_new')
    actor_phone_number_old = request.POST.get('phone_number_old')
    actor_role_new = request.POST.get('role_new')
    actor_role_old = request.POST.get('role_old')
    roles = models.rq_roles()
    if actor_role_new not in roles:
        models.add_roles(actor_role_new)
    models.org_edit_actor(actor_id, actor_phone_number_new, actor_phone_number_old, actor_role_new, actor_role_old)
    message = 'User {} has been edited succesfully'.format(actor_name)
    existing_users = models.rq_actor3()
    return render(request, 'settings/edit_org.html', {'first_name':first_name, 'message':message, 'existing_users':existing_users})


########################
### Index page views ###
########################

@login_required
def index(request):
    first_name = request.user.get_short_name()
    welcome_message = 'Welcome {}!'.format(first_name)
    aim_count = models.rq_index_aim_count()
    aims = models.rq_index_aim()
    data_drops = models.rq_index_dd()
    return render(request, 'index.html', {'first_name':first_name, 'welcome_message':welcome_message, 'aim_count':aim_count, 'aims':aims, 'data_drops':data_drops})

##########################
### Data request views ###
##########################

@login_required
def content(request):
    first_name = request.user.get_short_name()
    existing_aims = models.rq_aim()
    return render(request, 'rq/content.html', {'first_name':first_name, 'existing_aims':existing_aims})

### Data request views: instances ###

@login_required
def instance_aim_content(request):
    first_name = request.user.get_short_name()
    if 'aim_namespace' in request.POST:
        aim_namespace = request.POST.get('aim_namespace')
        request.session['aim_namespace'] = aim_namespace
        aim_name = request.POST.get('aim_name')
        request.session['aim_name'] = aim_name
    else:
        aim_namespace = request.session.get('aim_namespace')
        aim_name = request.session.get('aim_name')
    bot, bot_relations = models.rq_aim_bot(aim_namespace)
    documents = models.rq_aim_documents(aim_namespace)
    events = models.rq_aim_events(aim_namespace)
    return render(request, 'rq/instance/aim_content.html', {'first_name':first_name, 'aim_name':aim_name, 'aim_namespace':aim_namespace, 'bot':bot, 'bot_relations':bot_relations, 'documents':documents, 'events':events})

@login_required
def instance_aim_dd(request):
    first_name = request.user.get_short_name()
    aim_namespace = request.session.get('aim_namespace')
    aim_name = request.session.get('aim_name')
    data_drops = models.rq_aim_datadrops1(aim_namespace)
    documents = models.rq_aim_datadrops2(aim_namespace)
    events = models.rq_aim_datadrops3(aim_namespace)
    return render(request, 'rq/instance/aim_dd.html', {'first_name':first_name, 'aim_name':aim_name, 'aim_namespace':aim_namespace, 'data_drops':data_drops, 'documents':documents, 'events':events})

@login_required
def instance_event(request):
    first_name = request.user.get_short_name()
    aim_namespace = request.session.get('aim_namespace')
    aim_name = request.session.get('aim_name')
    instance = request.POST.get('event')
    event_data = models.rq_event1(aim_namespace, instance)
    superevents = models.rq_event4(aim_namespace, instance)
    subevents = models.rq_event5(aim_namespace, instance)
    data_drops = models.rq_event6(aim_namespace, instance)
    return render(request, 'rq/instance/event.html', {'first_name':first_name, 'aim_name':aim_name, 'event_data':event_data, 'superevents':superevents, 'subevents':subevents, 'data_drops':data_drops})

@login_required
def instance_document(request):
    first_name = request.user.get_short_name()
    aim_namespace = request.session.get('aim_namespace')
    aim_name = request.session.get('aim_name')
    instance = request.POST.get('document')
    instance_name = request.POST.get('document_name')
    document_data = models.rq_document1(aim_namespace, instance)
    prev_versions = models.rq_document2(aim_namespace, document_data)
    newer_versions = models.rq_document4(aim_namespace, document_data)
    data_drops = models.rq_document6(aim_namespace, instance)
    data_drops2 = models.rq_document7(aim_namespace, instance)
    bot = models.rq_document8(aim_namespace, instance)
    return render(request, 'rq/instance/document.html', {'first_name':first_name, 'aim_name':aim_name, 'instance_name':instance_name, 'document_data':document_data, 'prev_versions':prev_versions, 'newer_versions':newer_versions, 'data_drops':data_drops, 'data_drops2':data_drops2, 'bot':bot})

@login_required
def instance_document_download(request):
    file_path = os.path.join(request.POST.get('path'))
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response

@login_required
def instance_document_download2(request, file_path):
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response

@login_required
def instance_actor(request):
    first_name = request.user.get_short_name()
    aim_namespace = request.session.get('aim_namespace')
    aim_name = request.session.get('aim_name')
    instance = request.POST.get('actor')
    actor_name = request.POST.get('actor_name')
    actors = models.rq_actor1(aim_namespace, instance)
    data_drops = models.rq_actor2(aim_namespace, instance)
    return render(request, 'rq/instance/actor.html', {'first_name':first_name, 'aim_name':aim_name, 'actor_name':actor_name, 'actors':actors, 'data_drops':data_drops})

@login_required
def instance_bot(request):
    first_name = request.user.get_short_name()
    aim_namespace = request.session.get('aim_namespace')
    aim_name = request.session.get('aim_name')
    instance = request.POST.get('instance')
    instance_name = request.POST.get('instance_name')
    instance_type = request.POST.get('instance_type')
    instance_data = models.rq_bot1(aim_namespace, instance)
    instance_documents = models.rq_bot2(aim_namespace, instance)
    parent_instances = models.rq_bot3(aim_namespace, instance)
    child_instances = models.rq_bot4(aim_namespace, instance)
    return render(request, 'rq/instance/bot.html', {'first_name':first_name, 'aim_name':aim_name, 'instance':instance, 'instance_name':instance_name, 'instance_type':instance_type, 'instance_data':instance_data, 'instance_documents':instance_documents, 'parent_instances':parent_instances, 'child_instances':child_instances})

@login_required
def instance_datadrop(request):
    first_name = request.user.get_short_name()
    aim_namespace = request.session.get('aim_namespace')
    aim_name = request.session.get('aim_name')
    instance = request.POST.get('data_drop')
    data_drops = models.rq_datadrop1(aim_namespace, instance)
    documents = models.rq_datadrop2(aim_namespace, instance)
    events = models.rq_datadrop3(aim_namespace, instance)
    return render(request, 'rq/instance/data_drop.html', {'first_name':first_name, 'aim_name':aim_name, 'data_drops':data_drops, 'documents':documents, 'events':events})

### Data request views: search ###

@login_required
def search_start(request):
    first_name = request.user.get_short_name()
    existing_aims = models.rq_aim()
    return render(request, 'rq/search_start.html', {'first_name':first_name, 'existing_aims':existing_aims})

### Data request views: custom sparql query ###

@login_required
def sparql_query_1(request):
    first_name = request.user.get_short_name()
    new_query = True
    nss_oms = models.nss_oms
    return render(request, 'rq/sparql_query.html', {'first_name':first_name, 'new_query':new_query, 'nss_oms':nss_oms})

@login_required
def sparql_query_2(request):
    first_name = request.user.get_short_name()
    new_query = False
    nss_oms = models.nss_oms
    query = request.POST.get('query')
    output = models.rq_sparql_query(query)
    return render(request, 'rq/sparql_query.html', {'first_name':first_name, 'new_query':new_query, 'nss_oms':nss_oms, 'query':query, 'output':output,})

#######################
### Data drop views ###
#######################

@login_required
def dd_welcome(request):
    first_name = request.user.get_short_name()
    current_dd_start_time = request.session.get('current_dd_start_time', None)
    duration_dd_check = models.dd_check_session_duration(current_dd_start_time)
    if duration_dd_check == True:
        disabled = ''
    else:
        disabled = 'disabled'
    return render(request, 'dd/dd_welcome.html', {'first_name':first_name, 'disabled':disabled})

@login_required
def dd_continue(request):
    first_name = request.user.get_short_name()
    request.session['new_dd'] = False
    o_aim = request.session.get('o_aim', None)
    aim_name = request.session.get('aim_name')
    existing_events_check = models.rq_event2(o_aim)
    if existing_events_check == []:
        disabled = 'disabled'
    else:
        disabled = ''
    visibility_status = 'submit'
    return render(request, 'dd/dd_select_event.html', {'first_name':first_name, 'aim_name':aim_name, 'disabled':disabled, 'visibility_status':visibility_status})

@login_required
def dd_select_aim(request):
    first_name = request.user.get_short_name()
    request.session['new_dd'] = True
    existing_aims = models.rq_aim()
    check = []
    return render(request, 'dd/dd_select_aim.html', {'first_name':first_name, 'existing_aims':existing_aims, 'check':check})

@login_required
def dd_select_existing_aim(request):
    first_name = request.user.get_short_name()
    request.session['o_aim'] = request.POST.get('aim_namespace')
    o_aim = request.session.get('o_aim', None)
    aim_name = models.rq_current_aim(o_aim)
    request.session['aim_name'] = aim_name
    new_dd = request.session.get('new_dd', None)
    if new_dd == True:
        user_id = request.session.get('unique_user_id', None)
        unique_dd_id = models.dd_create(o_aim, user_id)
        request.session['unique_dd_id'] = unique_dd_id
        request.session['current_dd_start_time'] = datetime.now().strftime("%Y-%m-%dT%H:%M")
    else:
        unique_dd_id = request.session.get('unique_dd_id', None)
    existing_events_check = models.rq_event2(o_aim)
    if existing_events_check == []:
        disabled = 'disabled'
    else:
        disabled = ''
    visibility_status = 'hidden'
    return render(request, 'dd/dd_select_event.html', {'first_name':first_name, 'aim_name':aim_name, 'output':unique_dd_id, 'disabled':disabled, 'visibility_status':visibility_status})

@login_required
def dd_create_new_aim_1(request):
    first_name = request.user.get_short_name()
    return render(request, 'dd/dd_create_new_aim.html', {'first_name':first_name})

@login_required
def dd_create_new_aim_2(request):
    first_name = request.user.get_short_name()
    aim_name = request.POST.get('aim_name')
    o_aim = models.dd_new_aim(aim_name)
    request.session['o_aim'] = o_aim
    user_id = request.session.get('unique_user_id', None)
    unique_dd_id = models.dd_create(o_aim, user_id)
    request.session['unique_dd_id'] = unique_dd_id
    request.session['current_dd_start_time'] = datetime.now().strftime("%Y-%m-%dT%H:%M")
    existing_events = models.rq_event2(o_aim)
    existing_actors = models.rq_actor3()
    return render(request, 'dd/dd_create_new_event.html', {'first_name':first_name, 'aim_name':aim_name, 'existing_events':existing_events, 'existing_actors':existing_actors})

@login_required
def dd_select_existing_event_1(request):
    first_name = request.user.get_short_name()
    o_aim = request.session.get('o_aim', None)
    aim_name = request.session.get('aim_name')
    existing_events = models.rq_event2(o_aim)
    return render(request, 'dd/dd_select_existing_event.html', {'first_name':first_name, 'aim_name':aim_name, 'existing_events':existing_events})

@login_required
def dd_select_existing_event_2(request):
    first_name = request.user.get_short_name()
    o_aim = request.session.get('o_aim', None)
    aim_name = request.session.get('aim_name')
    unique_dd_id = request.session.get('unique_dd_id', None)
    unique_event_id = request.POST.get('event')
    output = models.dd_event2(o_aim, unique_dd_id, unique_event_id)
    return render(request, 'dd/dd_upload_file.html', {'first_name':first_name, 'aim_name':aim_name, 'output':output})

@login_required
def dd_create_new_event_1(request):
    first_name = request.user.get_short_name()
    o_aim = request.session.get('o_aim', None)
    aim_name = request.session.get('aim_name')
    existing_events = models.rq_event2(o_aim)
    existing_actors = models.rq_actor3()
    return render(request, 'dd/dd_create_new_event.html', {'first_name':first_name, 'aim_name':aim_name, 'existing_events':existing_events, 'existing_actors':existing_actors})

@login_required
def dd_create_extra_event_1(request):
    first_name = request.user.get_short_name()
    o_aim = request.session.get('o_aim', None)
    aim_name = request.session.get('aim_name')
    existing_events = models.rq_event2(o_aim)
    existing_actors =models.rq_actor3()
    event_type = request.POST.get('event_type')
    event_description = request.POST.get('event_description')
    startdatetime = request.POST.get('startdatetime')
    enddatetime = request.POST.get('enddatetime')
    related_actor = request.POST.get('related_actor')
    super_event = request.POST.get('super_event')
    unique_dd_id = request.session.get('unique_dd_id', None)
    output = models.dd_event1(o_aim, event_type, event_description, startdatetime, enddatetime, related_actor, super_event, unique_dd_id)
    return render(request, 'dd/dd_create_new_event.html', {'output':output, 'aim_name':aim_name, 'first_name':first_name, 'existing_events':existing_events, 'existing_actors':existing_actors})

@login_required
def dd_create_new_event_2(request):
    first_name = request.user.get_short_name()
    o_aim = request.session.get('o_aim', None)
    aim_name = request.session.get('aim_name')
    event_type = request.POST.get('event_type')
    event_description = request.POST.get('event_description')
    startdatetime = request.POST.get('startdatetime')
    enddatetime = request.POST.get('enddatetime')
    related_actor = request.POST.get('related_actor')
    super_event = request.POST.get('super_event')
    unique_dd_id = request.session.get('unique_dd_id', None)
    output = models.dd_event1(o_aim, event_type, event_description, startdatetime, enddatetime, related_actor, super_event, unique_dd_id)
    return render(request, 'dd/dd_upload_file.html', {'output':output, 'aim_name':aim_name, 'first_name':first_name})

@login_required
def dd_upload_file_1(request):
    first_name = request.user.get_short_name()
    aim_name = request.session.get('aim_name')
    return render(request, 'dd/dd_upload_file.html', {'first_name':first_name, 'aim_name':aim_name})

@login_required
def dd_upload_file_2(request):
    first_name = request.user.get_short_name()
    aim_name = request.session.get('aim_name')
    uploaded_file = request.FILES['file']
    file_name = uploaded_file.name
    file_type = file_name.rsplit('.', 1)[1]
    file_size = uploaded_file.size
    if file_type == 'ifc' or file_type == 'pdf' or file_type == 'csv' or file_type == 'png' or file_type == 'jpg' or file_type == 'jpeg' or file_type == 'pcd' or file_type == 'txt':
        o_aim = request.session.get('o_aim', None)
        file_name_no_type = file_name.split(".")[0]
        file_exists_check = [f for f in os.listdir(models.document_storage_location) if f.startswith(file_name_no_type) and f.endswith(file_type)]
        timestamp = datetime.now().strftime("%Y-%m-%dT%H.%M.%S")
        file_name_rev = str(file_name_no_type+'_'+timestamp+'.'+file_type)
        file_system = FileSystemStorage()
        file_system.save(file_name_rev, uploaded_file)
        file_location = str(models.document_storage_location+'/'+file_name_rev)
    else:
        error_message = 'This file type cannot be uploaded. Please upload a file of one of the following types: ifc, pdf, csv, png, jpeg, pcd, txt.'
        return render(request, 'dd/dd_upload_file.html', {'first_name':first_name, 'error_message':error_message})
    if 'copy_in_original_format' in request.FILES:
        copy_in_original_format = request.FILES['copy_in_original_format']
        copy_name = copy_in_original_format.name
        copy_name_no_type = copy_name.split(".")[0]
        copy_type = copy_name.split(".")[1].lower()
        copy_name_rev = str(copy_name_no_type+'_'+timestamp+'.'+copy_type)
        file_system.save(copy_name_rev, copy_in_original_format)
        copy_location = str(models.document_storage_location+'/'+copy_name_rev)
    else:
        copy_name = None
        copy_type = None
        copy_location = None
    if file_exists_check != []:
        prev_version = models.dd_prev_version_check(file_exists_check, o_aim)
    else:
        prev_version = None
    message = 'The document has successfully been uploaded. Please enrich the documents metadata in order to make sure it will be stored correctly.'
    existing_actors = models.rq_actor3()
    output = models.dd_document1(o_aim, file_name_rev, file_type, file_location, copy_name, copy_type, copy_location, prev_version)
    return render(request, 'dd/dd_enrich_file.html', {'first_name':first_name, 'aim_name':aim_name, 'message':message, 'output':output, 'existing_actors':existing_actors})

@login_required
def dd_upload_file_3(request):
    first_name = request.user.get_short_name()
    o_aim = request.session.get('o_aim', None)
    aim_name = request.session.get('aim_name')
    unique_dd_id = request.session.get('unique_dd_id', None)
    unique_document_id = request.POST.get('unique_document_id')
    document_type = request.POST.get('document_type')
    document_storage_location = request.POST.get('document_storage_location')
    document_description = request.POST.get('document_description')
    document_unique_identifier = request.POST.get('document_unique_identifier')
    document_creation_software = request.POST.get('document_creation_software')
    document_creation_software_version = request.POST.get('document_creation_software_version')
    preservation_until_date = request.POST.get('preservation_until_date')
    content_type_documentation = request.POST.get('content_type_documentation')
    content_type_geometrical = request.POST.get('content_type_geometrical')
    content_type_alphanumerical = request.POST.get('content_type_alphanumerical')
    document_status = request.POST.get('document_status')
    responsible_actor = request.POST.get('responsible_actor')
    if 'prev_version_id' in request.POST:
        prev_version_id = request.POST.get('prev_version_id')
        prev_version_status = request.POST.get('prev_version_status')
    else:
        prev_version_id = None
        prev_version_status = None
    models.dd_document2(o_aim, unique_dd_id, unique_document_id, document_description, document_unique_identifier, document_creation_software, document_creation_software_version, preservation_until_date, content_type_documentation, content_type_geometrical, content_type_alphanumerical, document_status, prev_version_id, prev_version_status, responsible_actor)
    if document_type == 'ifc':
        request.session['unique_document_id'] = unique_document_id
        request.session['document_storage_location'] = document_storage_location
        model_data, relations, existing_data, intersections = models.dd_ifc1a(o_aim, document_storage_location)
        type_check = []
        if any(a.type == 'Site' for a in existing_data):
            type_check.append('Site')
        if any(a.type == 'Building' for a in existing_data):
            type_check.append('Building')
        if any(a.type == 'Storey' for a in existing_data):
            type_check.append('Storey')
        if any(a.type == 'Space' for a in existing_data):
            type_check.append('Space')
        # if any(a.type == 'Element' for a in existing_data):
        #         type_check.append('Element')
        return render(request, 'dd/dd_ifc.html', {'first_name':first_name, 'aim_name':aim_name, 'model_data':model_data, 'existing_data':existing_data, 'intersections':intersections, 'relations':relations, 'type_check':type_check})
    else:
        if unique_dd_id == None:
            disabled = 'disabled'
        else:
            disabled = ''
        return render(request, 'dd/dd_end.html', {'first_name':first_name, 'aim_name':aim_name, 'disabled':disabled})

@login_required
def dd_upload_file_4(request):
    first_name = request.user.get_short_name()
    o_aim = request.session.get('o_aim', None)
    aim_name = request.session.get('aim_name')
    document_storage_location = request.session.get('document_storage_location', None)
    related_original = request.POST.get('related_original')
    related_new = request.POST.get('related_new')
    models.dd_ifc1(o_aim, related_original, related_new)
    model_data, relations, existing_data, intersections = models.dd_ifc1a(o_aim, document_storage_location)
    type_check = []
    if any(a.type == 'IFCSITE' for a in existing_data):
        type_check.append('Site')
    if any(a.type == 'IFCBUILDING' for a in existing_data):
        type_check.append('Building')
    if any(a.type == 'IFCBUILDINGSTOREY' for a in existing_data):
        type_check.append('Storey')
    if any(a.type == 'IFCSPACE' for a in existing_data):
        type_check.append('Space')
    return render(request, 'dd/dd_ifc.html', {'first_name':first_name, 'aim_name':aim_name, 'model_data':model_data, 'existing_data':existing_data, 'intersections':intersections, 'related_new_guid':related_new, 'type_check':type_check})

@login_required
def dd_upload_file_5(request):
    first_name = request.user.get_short_name()
    o_aim = request.session.get('o_aim', None)
    aim_name = request.session.get('aim_name')
    unique_document_id = request.session.get('unique_document_id', None)
    document_storage_location = request.session.get('document_storage_location', None)
    unique_dd_id = request.session.get('unique_dd_id', None)
    model_data, relations, existing_data, intersections = models.dd_ifc1a(o_aim, document_storage_location)
    models.dd_ifc2(o_aim, unique_document_id, model_data, intersections)
    models.dd_ifc3(o_aim, model_data, relations)
    if unique_dd_id == None:
        disabled = 'disabled'
    else:
        disabled = ''
    success = 'Your ifc-model has been succesfully uploaded and processed.'
    return render(request, 'dd/dd_end.html', {'first_name':first_name, 'aim_name':aim_name, 'disabled':disabled, 'message':success})

@login_required
def dd_end(request):
    request.session['aim_name'] = None
    request.session['unique_dd_id'] = None
    request.session['current_dd_start_time'] = None
    return redirect('app:index')

def ifc_viewer(request):
    return render(request, 'ifc_viewer.html')
















########################
### test environment ###
########################

# @login_required
# def search_results(request):
#     first_name = request.user.get_short_name()
#     type = 'ddss:Maintenance'
#     output = models.rq_model5(type)
#     return render(request, 'rq/instance.html', {'first_name':first_name, 'output':output})

# from . import serializers
# from rest_framework import serializers, viewsets, generics

# def write_ontology(request):
#     welcome_message = models.model_write_ontology()
#     return render(request, 'index.html', {'welcome_message':welcome_message})
