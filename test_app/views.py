from http.client import HTTPResponse
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from . import models



# These variables define the SPARQL endpoints which will be accessed
sparql_endpoint_1 = 'http://localhost:7200/repositories/test_repo'
sparql_endpoint_2 = 'http://localhost:7200/repositories/test_repo/statements'


# Index page: This page currently returns a simple string response

def index(request):
    return HttpResponse('Hello world')


# Model 1: This model queries a SPARQL endpoint, and constructs a turtle-output with 
# the results of this query. The queries themselves are defined query1.html.

def model1a(request):
    return render(request, 'page1.html')

def model1b(request):
    query_construct = request.POST.get('construct')
    query_where = request.POST.get('where')
    output = models.getData1(sparql_endpoint_1, query_construct, query_where)
    return render(request, 'page1.html', {'output':output})


# Model 2: This model queries a SPARQL endpoint. It currently does not function.

def model2a(request):
    output = models.getData2(sparql_endpoint_1)
    return HttpResponse(output, content_type="text/plain")


# Model 3: This model facilitates writing a triple to the a SPARQL endpoint. The triple
# is currently hardcoded to have 'bot' as predicate.

def model3a(request):
    return render(request, 'page3.html')

def model3b(request):
    subject = request.POST.get('subj')
    predicate = request.POST.get('pred')
    object = request.POST.get('obj')
    output = models.getData3(sparql_endpoint_1, sparql_endpoint_2, subject, predicate, object)
    return render(request, 'page3.html', {'output':output})










### UNUSED CODE ###

# m1_query_construct = '?Building bot:hasStorey ?Storey'
# m1_query_where = '?Building bot:hasStorey ?Storey'
# def model1(request):
    # answer1 = models.getData1(sparql_endpoint_1)
    # render(request, 'page1.html', {'output':answer1}
    # return HttpResponse(answer1, content_type="text/plain")

### 

# sparql_endpoint_3 = 'https://www.w3.org/People/Berners-Lee/card'
# def model2(request):
    # answer2 = models.getData2(sparql_endpoint_3)
    # return HttpResponse(answer2, content_type="text/plain")

###