# coding=UTF-8
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse, Http404
import urllib
from xml.dom import minidom


def create_woeid(place):
    woeid=place.childNodes[0].childNodes[0].data
    typename=place.childNodes[1].childNodes[0].data
    typecode = place.childNodes[1].attributes['code'].value
    name=place.childNodes[2].childNodes[0].data
    try:
        country=place.childNodes[3].childNodes[0].data
    except:
        country=''
    try:
        admin1=place.childNodes[4].childNodes[0].data
        admin1type=place.childNodes[4].attributes['type'].value
    except:
        admin1=admin1type=''
    try:
        admin2=place.childNodes[5].childNodes[0].data
        admin2type=place.childNodes[5].attributes['type'].value
    except:
        admin2=admin2type=''
    try:
        admin3=place.childNodes[6].childNodes[0].data
        admin3type=place.childNodes[6].attributes['type'].value
    except:
        admin3=admin3type=''
    try:
        locality1=place.childNodes[7].childNodes[0].data
    except:
        locality1=''
    try:
        locality2=place.childNodes[8].childNodes[0].data
    except:
        locality2=''
    try:
        postal=place.childNodes[9].childNodes[0].data
    except:
        postal=''
    #centroid
    lat = place.childNodes[10].childNodes[0].childNodes[0].data
    lon = place.childNodes[10].childNodes[1].childNodes[0].data
    #bbox
    nelat = place.childNodes[11].childNodes[0].childNodes[0].childNodes[0].data
    nelon = place.childNodes[11].childNodes[0].childNodes[1].childNodes[0].data
    swlat = place.childNodes[11].childNodes[1].childNodes[0].childNodes[0].data
    swlon = place.childNodes[11].childNodes[1].childNodes[1].childNodes[0].data

    return {
        'woeid':woeid,
        'type': typename,
        'name':name,
        'country':country,
        'admin1':admin1,
        'admin1type':admin1type,
        'admin2':admin2,
        'admin2type':admin2type,
        'admin3':admin3,
        'admin3type':admin3type,
        'locality1':locality1,
        'locality2':locality2,
        'postal': postal,
        'lat':lat,
        'lon': lon,
        'nelat': nelat,
        'nelon':nelon,
        'swlat':swlat,
        'swlon':swlon
        }
        
def getDetail(woeid):
    url = "http://where.yahooapis.com/v1/place/%s?appid=%s" % (woeid, settings.API_KEY)
    f = urllib.urlopen(url)
    dom = minidom.parse(f)
    place = dom.getElementsByTagName('place')[0]
    w = create_woeid(place)
    return w

def getCollection(woeid, type):
    url = "http://where.yahooapis.com/v1/place/%s/%s;count=0?appid=%s&view=long" % (woeid, type, settings.API_KEY)
    f = urllib.urlopen(url)
    dom = minidom.parse(f)
    locations=[]
    for place in dom.getElementsByTagName('place'):
        print place
        locations.append(create_woeid(place))
    return locations
    
def getlocation(place_name):
    params = urllib.urlencode({'q': 'select * from geo.places where text="%s"' % place_name})
    f = urllib.urlopen('http://query.yahooapis.com/v1/public/yql?%s' % params)
    dom = minidom.parse(f)
    locations=[]
    for place in dom.getElementsByTagName('place'):
        locations.append(create_woeid(place))
    return locations

def getdetails(woeid):
    # Burn, YQL, burn! (I cannot believe that this works :))
    yql= 'select * from yql.query.multi where queries = "'+\
        'select * from geo.places where woeid = ' + woeid + ';' +\
        'select * from geo.places.ancestors where descendant_woeid = ' + woeid + ';' +\
        'select * from geo.places.belongtos where member_woeid = ' + woeid + ';' +\
        'select * from geo.places.children where parent_woeid = ' + woeid + ';' +\
        'select * from geo.places.neighbors where neighbor_woeid = ' + woeid + ';' +\
        'select * from geo.places.parent where child_woeid = ' + woeid + ';' +\
        'select * from geo.places.siblings where sibling_woeid = ' + woeid + '"'
    params = urllib.urlencode({
        'format': 'xml',
        'q': yql, 
        'env':'store://datatables.org/alltableswithkeys'
        })
    url = 'http://query.yahooapis.com/v1/public/yql?%s' % params
    f = urllib.urlopen(url)
    dom = minidom.parse(f)
    results = dom.getElementsByTagName('results')
    place = create_woeid(results[0].childNodes[0].childNodes[0])
    parent = []
    for p in results[6].getElementsByTagName('place'):
        parent.append(create_woeid(p))
    ancestors = []
    for p in results[2].getElementsByTagName('place'):
        ancestors.append(create_woeid(p))
    belongtos = []
    for p in results[3].getElementsByTagName('place'):
        belongtos.append(create_woeid(p))
    neighbours = []
    for p in results[5].getElementsByTagName('place'):
        neighbours.append(create_woeid(p))
    children = []
    for p in results[4].getElementsByTagName('place'):
        children.append(create_woeid(p))
    siblings = []
    for p in results[7].getElementsByTagName('place'):
        siblings.append(create_woeid(p))
    return (place, parent, ancestors, belongtos, neighbours, children, siblings)


def home(request):
    return render_to_response('app/home.html', locals(), context_instance=RequestContext(request))

def search(request, query):
    locations = getlocation(query)
    return render_to_response('app/search.html', locals(), context_instance=RequestContext(request))

def search_form(request):
    if request.method == 'POST':
        return HttpResponseRedirect(reverse("search", args=[request.POST['query']]))
    return render_to_response('app/home.html', locals(), context_instance=RequestContext(request))

def woeid(request, woeid):
    place, parent, ancestors, belongtos, neighbours, children, siblings = getdetails(woeid)
    return render_to_response('app/woeid.html', locals(), context_instance=RequestContext(request))

def woeid_collection(request, woeid, type):
    place=getDetail(woeid)
    locations = getCollection(woeid, type)
    return render_to_response('app/search.html', locals(), context_instance=RequestContext(request))
