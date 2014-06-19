#!/bin/bash

#set -x

curl \
  -d"@postbody.xml" \
  -H 'soapaction: "http://www.sjofartsverket.se/webservice/VaderService/ViVaData.wsdl/GetViVaDataTH"' \
  -H 'Content-Type: text/xml; charset=utf-8' \
  -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.114 Safari/537.36' \
  "http://161.54.134.239/vivadata.asmx"
