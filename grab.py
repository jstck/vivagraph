#!/usr/bin/env python

import xml.etree.ElementTree as ET
import datetime
import matplotlib.pyplot as plt

xmltree = ET.parse('test.xml')

#Uglily grab all the ViVaPoint nodes
nodes = xmltree.findall('*/*/*/*')

times = []
values = []

for node in nodes:
  val = float(node.get("Data"))
  t = datetime.datetime.strptime(node.get("Tid"), "%Y-%m-%dT%H:%M:%S")
  times.append(t)
  values.append(val)
  #print "%s: %.1f" % (t.strftime("%Y-%m-%d %H:%M:%S"), val)
maxval = max(values)
minval = min(values)


#print maxval,minval

fig, ax = plt.subplots()

ax.plot_date(times, values, '-')

ax.autoscale_view()
ax.grid(True)

fig.autofmt_xdate()

plt.savefig("test.png")
