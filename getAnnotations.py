# -- coding: utf-8 --

import sys
import re
import urllib2
import urllib
import json
import os
import pandas
from pprint import pprint
from string import punctuation

def strip_punctuation(s):
    return ''.join(c for c in s if c not in punctuation)

files, videoIDs, categories, transcripts = [], [], [], []
# get information about the video
for file in os.listdir("../transcripts/"):
    files.append(file)
    videoIDs.append(re.findall(".+(?=_)", file)[0])
    categories.append(re.findall("\_([0-9])", file)[0].strip("_"))
    # get contents of transcript
    with open("../transcripts/" + str(file), 'r') as f:
        try:
            raw = f.read()
            # remove timestamp and newlines
            text = strip_punctuation(re.sub("[0-9]+:[0-9]+", " ", str(raw)).replace('\n', ' ').replace('\r', ''))
            text = re.sub('[^a-zA-Z ]+', '', text).strip()
        except:
            text = None
        transcripts.append(text)

transcriptDF = pandas.DataFrame(
    {'videoIDs': videoIDs,
     'categories': categories,
     'transcripts' : transcripts
    })

transcriptDF.to_csv("formatted_transcripts.csv")

REST_URL = "http://data.bioontology.org"
API_KEY = "ecb74532-a618-42b9-8a05-d5e7761ac7db"

def get_json(url):
    opener = urllib2.build_opener()
    opener.addheaders = [('Authorization', 'apikey token=' + API_KEY)]
    return json.loads(opener.open(url).read())

def print_annotations(annotations, get_class=True):
    for result in annotations:


        print "Annotation details"
        for annotation in result["annotations"]:
            print "\tfrom: " + str(annotation["from"])
            print "\tto: " + str(annotation["to"])
            print "\tmatch type: " + annotation["matchType"]

        if result["hierarchy"]:
            print "\n\tHierarchy annotations"
            for annotation in result["hierarchy"]:
                class_details = get_json(annotation["annotatedClass"]["links"]["self"])
                pref_label = class_details["prefLabel"] or "no label"
                print "\t\tClass details"
                print "\t\t\tid: " + class_details["@id"]
                print "\t\t\tprefLabel: " + class_details["prefLabel"]
                print "\t\t\tontology: " + class_details["links"]["ontology"]
                print "\t\t\tdistance from originally annotated class: " + str(annotation["distance"])

    print "\n\n"

def divide(silly):
    mid=(len(silly) + 1) / 2
    firstHalf = silly[:mid]
    secondHalf = silly[mid:]
    return firstHalf + secondHalf

IDs, cuis, ontology, labels, start, end = [], [], [], [], [], []

for index, row in transcriptDF.iterrows():
    # call NCBO annotator API
    print(row['videoIDs'])
    try:
        annotations = get_json(REST_URL + "/annotator?" +
                                        "ontologies=SNOMEDCT&" +
                                          "semantic_types={T033,T046,T184,T037,T040}&text=" + urllib2.quote(row['transcripts']))
        # create for each annotation, collect data
        for result in annotations:
            class_details = get_json(result["annotatedClass"]["links"]["self"]) if True else result["annotatedClass"]
            IDs.append(row['videoIDs']),
            cuis.append(str(class_details["cui"])),
            ontology.append(re.findall("([A-Z-0-9])\w+", class_details["links"]["ontology"])),
            labels.append(str(class_details["prefLabel"]))
            counter = 0
            for annotation in result["annotations"]:
                while counter < 1:
                    start.append(str(annotation["from"]))
                    end.append(str(annotation["to"]))
                    counter+=1

            print(str(class_details["prefLabel"]))
    # if string is too long
    except:
        try:
            cut_transcript = divide(row['transcripts'])
            annotations = get_json(REST_URL + "/annotator?" +
                                   "ontologies=SNOMEDCT&" +
                                   "semantic_types={T033,T046,T184,T037,T040}&text=" + urllib2.quote(
                cut_transcript[0]))
            # create for each annotation, collect data
            for result in annotations:
                class_details = get_json(result["annotatedClass"]["links"]["self"]) if True else result[
                    "annotatedClass"]
                IDs.append(row['videoIDs']),
                cuis.append(str(class_details["cui"])),
                ontology.append(re.findall("([A-Z-0-9])\w+", class_details["links"]["ontology"])),
                labels.append(str(class_details["prefLabel"]))
                counter = 0
                for annotation in result["annotations"]:
                    while counter < 1:
                        start.append(str(annotation["from"]))
                        end.append(str(annotation["to"]))
                        counter += 1
                print(str(class_details["prefLabel"]))
            annotations = get_json(REST_URL + "/annotator?" +
                                   "ontologies=SNOMEDCT&" +
                                   "semantic_types={T033,T046,T184,T037,T040}&text=" + urllib2.quote(
                cut_transcript[1]))
            # create for each annotation, collect data
            for result in annotations:
                class_details = get_json(result["annotatedClass"]["links"]["self"]) if True else result[
                    "annotatedClass"]
                IDs.append(row['videoIDs']),
                cuis.append(str(class_details["cui"])),
                ontology.append(re.findall("([A-Z-0-9])\w+", class_details["links"]["ontology"])),
                labels.append(str(class_details["prefLabel"]))
                counter = 0
                for annotation in result["annotations"]:
                    while counter < 1:
                        start.append(str(annotation["from"]))
                        end.append(str(annotation["to"]))
                        counter += 1
                print(str(class_details["prefLabel"]))
        except Exception, e:
            print str(e)
            continue


# create pandas dataframe with information about each annotation
annotationsDF = pandas.DataFrame(
    {'videoID': IDs,
     'ontology': ontology,
     'cui': cuis,
     'prefLabel' : labels,
     'start': start,
     'end': end
    })
annotationsDF.to_csv("annotationsDF.csv")
