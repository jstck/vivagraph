#!/usr/bin/env python

import datetime
import os

xmlfilename="cache/data.xml"

def fullfile(filename):
  return os.path.join(os.path.dirname(os.path.realpath(__file__)), filename)

def checkForUpdate(filename,maxage=3600):
  ff = fullfile(filename)

  if not os.path.exists(ff):
    return True

  timestamp = os.path.getmtime(ff)
  return datetime.datetime.fromtimestamp(timestamp+maxage)<datetime.datetime.now()


def makerequest(tidfom, tidtom, platsid=17):
  timeformat="%Y-%m-%dT%H:%M:%S+02:00"
  body="""
<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"><s:Body xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema"><GetViVaDataTH xmlns="http://www.sjofartsverket.se/webservice/VaderService/ViVaData.wsdl"><PlatsId>%(platsid)d</PlatsId><ViVaTyp>14</ViVaTyp><TidFOM>%(tidFOM)s</TidFOM><TidTOM>%(tidTOM)s</TidTOM></GetViVaDataTH></s:Body></s:Envelope>
"""
  data = {
    "platsid": platsid,
    "tidFOM": tidfom.strftime(timeformat),
    "tidTOM": tidtom.strftime(timeformat)
  }

  return body.strip() % data

def doRequest(days=7):
  import urllib2

  tom = datetime.datetime.now()
  fom1 = tom - datetime.timedelta(days=days)

  #Cut off to whole hour
  fom = datetime.datetime(fom1.year,fom1.month,fom1.day,fom1.hour)

  postbody = makerequest(fom,tom)

  url="http://161.54.134.239/vivadata.asmx"
  headers={
    'soapaction': '"http://www.sjofartsverket.se/webservice/VaderService/ViVaData.wsdl/GetViVaDataTH"',
    'Content-Type': 'text/xml; charset=utf-8',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.114 Safari/537.36',
    'Accept-Encoding': 'gzip,deflate,sdch'
  }
  req = urllib2.Request(url, postbody, headers)
  response = urllib2.urlopen(req)

  return response.read()

def handleResponse(response):
  import matplotlib
  matplotlib.use("Agg")
  import matplotlib.pyplot as plt
  import xml.etree.ElementTree as ET


  xmlroot = ET.fromstring(response)
  xml = ET.ElementTree(xmlroot)
  xml.write(fullfile(xmlfilename))

  #Uglily grab all the ViVaPoint nodes
  nodes = xml.findall('*/*/*/*')

  times = []
  values = []

  for node in nodes:
    val = float(node.get("Data"))
    t = datetime.datetime.strptime(node.get("Tid"), "%Y-%m-%dT%H:%M:%S")
    times.append(t)
    values.append(val)

  maxval = max(values)
  minval = min(values)

  #Plot things!
  fig, ax = plt.subplots()

  ax.plot_date(times, values, '-')

  ax.autoscale_view()
  ax.grid(True)

  fig.autofmt_xdate()

  plt.savefig(fullfile("cache/plot.png"))

def doUpdate():
  if checkForUpdate(xmlfilename):
    xmldata = doRequest()
    if xmldata is not None:
      handleResponse(xmldata)

def index(req):
  from mako.template import Template
  doUpdate()
  req.content_type = "text/html; charset=UTF-8"
  req.send_http_header()

  tpl = Template(filename=fullfile("template.html"), input_encoding="utf-8")
  req.write(tpl.render_unicode().encode('utf-8', 'replace'))

if __name__ == "__main__":
  doUpdate()
