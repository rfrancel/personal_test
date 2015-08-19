#!/usr/bin/env python
# -*- coding: cp1252 -*-

import os
import glob
import urllib
import urllib2
import shutil
import json
import pprint
import xml.etree.ElementTree as ET
import zipfile
import datetime
import hashlib
import md5

##################################################### INSTRUCTIONS FOR USE #######################################################
##                                                                                                                              ##
##                  WARNING: The script won't work before the table bod.public.dataset is filled                                ##
##                                                                                                                              ##
## 1. Create a temporary folder on your desktop with the spatial data that you want to add to the data folder                   ##
## 2. Launch the script                                                                                                         ##
## 3. The scripts asks you the technical name of the layer (ex. ch.are.agglomerationen_isolierte_staedte)                       ##
## 4. The script asks for the folder where the spatial data is to be found (the folder that you just created during step 1)     ##
## 5. A ew folder with your layer name is present in the data.geo.admin.ch folder:                                              ##
##                                                                                                                              ##
##                                                                                                                              ##
##################################################################################################################################
################################################## Part 1: Create the data folder ################################################
##################################################################################################################################

##Create Opener
proxy_http = urllib2.ProxyHandler({"http":"http://proxy-bvcol.admin.ch:8080"})
proxy_https = urllib2.ProxyHandler({"https":"http://proxy-bvcol.admin.ch:8080"})
opener = urllib2.build_opener(
    urllib2.HTTPHandler(),
    urllib2.HTTPSHandler(),
    proxy_http,
    proxy_https)
urllib2.install_opener(opener)

## Define the layername and check if it exists
layer_name_check = False

while layer_name_check == False:
    print("Enter the techninal name of the layer ")
    layer_name = raw_input("(Ex: ch.are.agglomerationen_isolierte_staedte) ")

    ## Create URL to xml for the layer, check if the reponse xml adds with layer.
    url_xml = "http://www.geocat.ch/geonetwork/srv/ger/q?fast=index&from=1&to=10&sortBy=relevance&sortOrder=undefined&any={0}&similarity=1.0&type=dataset&similarity=undefined&relation=within".format(layer_name)
    xml = urllib2.urlopen(url_xml)
    tree = ET.parse(xml)
    root = tree.getroot()
    metadata = root.find('metadata')

    if metadata is None:
        layer_name_check = False
        exit_question = raw_input("This layer does not exist or the table bod.public.dataset has not been filled.\nIf you want to exit the program, press 'E'.\nIf you want to try again, press 'C'")
        if exit_question.lower() == "e":
            exit()
    else:
        layer_name_check = True

## Create new folder with technical name and data folder, remove old one if already exists
    
dest_path = 'N:/5-kogis/5-KOGIS/51-BGDI/5105-Geodienste/5105-04-GeoportalBund/5105-04-02-data_geo_admin_ch/5105-04-02-05-Ordnerstruktur/data.geo.admin.ch/{0}'.format(layer_name)

if os.path.exists(dest_path):
    try:
        shutil.rmtree(dest_path)
    except OSError as e:
        message = str(e) + "\nFolder is probably open. Please close it before running the script again."
        print message
        exit()
        
os.mkdir(dest_path)
os.mkdir("{0}/data".format(dest_path))
data_folder = "{0}/data".format(dest_path)

#Copy licence.txt to data folders
src_licence = "N:/5-kogis/5-KOGIS/51-BGDI/5105-Geodienste/5105-04-GeoportalBund/5105-04-02-data_geo_admin_ch/5105-04-02-02-templates/licence.txt"
dest_licence = "{0}/licence.txt".format(data_folder)
shutil.copy2(src_licence, dest_licence)

## Define spatial data path
print("Enter the path to the spatial data folder")
srcdir = raw_input("(Ex: I:/BGDI/01_Originaldaten/bund/are/_Rohdaten/ch.are.agglomerationen-isolierte_staedte_20140506) ")

if os.path.exists(srcdir) == False:
    print 'This folder does not exist.'
    srcdir = raw_input("Enter the path of the folder containing the spatial data")

#Copy all the files from the data to the new data file
src_files = os.listdir(srcdir)

for filename in src_files:
   full_srcname = os.path.join(srcdir, filename)
   full_destname = "{0}/{1}".format(data_folder, filename)
   shutil.copy2(full_srcname, full_destname)

#Read xml to find id to print metadata files

for id_l in root.iter('id'):
    id_layer = id_l.text

#print pdf good directory
os.chdir(data_folder)

filename_pdf = "Metadata_PDF.pdf"
url_pdf = "http://www.geocat.ch/geonetwork/srv/ger/metadata.print?id={0}".format(id_layer)

with open('Metadata_PDF.pdf', 'wb') as f:
    f.write(urllib2.urlopen(url_pdf).read())
    f.close()

#print ISO xml
filename_xml_iso = "Metadata_xml_iso19139.xml"
url_xml_iso = "http://www.geocat.ch/geonetwork/srv/ger/xml_iso19139?id={0}".format(id_layer)

with open('Metadata_xml_iso19139.xml', 'wb') as f:
    f.write(urllib2.urlopen(url_xml_iso).read())
    f.close()

#print GM03 xml
filename_gm03 = "Metadata_gm03.xml"
url_gm03 = "http://www.geocat.ch/geonetwork/srv/ger/gm03.xml?id={0}".format(id_layer)

with open('Metadata_gm03.xml', 'wb') as f:
    f.write(urllib2.urlopen(url_gm03).read())
    f.close()


##################################################################################################################################
#################################################### Part 2: Create zipfile ######################################################
##################################################################################################################################

os.chdir(dest_path)

zf = zipfile.ZipFile('data.zip', 'w')

for name in glob.glob("data/*"):
    zf.write(name, os.path.basename(name), zipfile.ZIP_DEFLATED)

zf.close()

##################################################################################################################################
##################################### Part 3: Create readme.txt and complete the folder ##########################################
##################################################################################################################################

zf=zipfile.ZipFile("data.zip")

##First lines of the readme file
with open ("readme.txt", "w") as file:
    file.write("http://map.geo.admin.ch/?layers={0}\n".format(layer_name))
    file.write("\nDATA:ZIP\n")
    file.write("="*115)
    file.write("\nFILE NAME \t\t DATE\t\t\t PACKED SIZE\t\t SIZE\t\t PATH\n")
    file.write("="*115)
    file.write("\n")

##Fill with content info

for info in zf.infolist():
    with open ("readme.txt", "a") as file:
        file.write("\n{0}\t{1}\t\t{2}\t\t{3}".format(info.filename, datetime.datetime(*info.date_time), info.compress_size, info.file_size))

##Complete readme file
with open ("readme.txt", "a") as file:
    file.write("\n")
    file.write("="*115)
    file.write("\n")

## Add MD5Checksum:
    
mdchecksum = hashlib.md5(open("readme.txt", "rb").read()).hexdigest()
    
with open ("readme.txt", "a") as file:
    file.write("\nMD5Checksum: {0}".format(mdchecksum))


##################################################################################################################################
################################## Part 4: Remove uncompressed data folder and copy index ########################################
##################################################################################################################################

shutil.rmtree(data_folder)

## Copy index to folder

src_index = "N:/5-kogis/5-KOGIS/51-BGDI/5105-Geodienste/5105-04-GeoportalBund/5105-04-02-data_geo_admin_ch/5105-04-02-02-templates/index.html"
dest_index = "{0}/index.html".format(dest_path)

shutil.copy2(src_index, dest_index)
