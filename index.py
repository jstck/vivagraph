#!/usr/bin/env python

import datetime


xmlfilename="cache/data.xml"

def checkForUpdate(filename,maxage=3600):
  import os
  if not os.path.exists(filename):
    return True

  timestamp = os.path.getmtime(filename)
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
  import matplotlib.pyplot as plt
  import xml.etree.ElementTree as ET


  xmlroot = ET.fromstring(response)
  xml = ET.ElementTree(xmlroot)
  xml.write(xmlfilename)

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

  plt.savefig("cache/plot.png")


if checkForUpdate(xmlfilename):
  xmldata = doRequest()
  if xmldata is not None:
    handleResponse(xmldata)
