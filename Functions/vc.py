import csv
import json
import nltk
from tabulate import tabulate
from collections import Counter, defaultdict
import string
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import re
from polyleven import levenshtein

def generate():
    return 0

def tag_compare(vocabs): #input scheme: [(vocab, vocab_name), (vocab, vocab_name)] - vocab (dict), vocab_name (str)
    #collection of all distinct tags
    tags = []
    for vocab in vocabs:
        for key in vocab[0].keys():
            if key not in tags:
                tags.append(key)
    #systematic comparison of all distinct tags with single vocabs
    vgl = {}
    for tag in tags:
        vgl[tag] = defaultdict(generate)
        sum = 0
        for vocab in vocabs:
            if tag in vocab[0].keys():
                vgl[tag][vocab[1]] = vgl[tag][vocab[1]] + 1
                sum = sum + 1
            else:
                vgl[tag][vocab[1]] = vgl[tag][vocab[1]]
        vgl[tag]["sum"] = sum
    return vgl

def tag_compare_fuzzy(vocabs, distance): #input scheme: [(vocab, vocab_name), (vocab, vocab_name)] - vocab (dict), vocab_name (str)
    #collection of all distinct tags
    tags = []
    for vocab in vocabs:
        for key in vocab[0].keys():
            if key not in tags:
                tags.append(key)
    #systematic comparison of all distinct tags with single vocabs
    vgl = {}
    for tag in tags:
        #print(tag)
        matches = []
        vgl[tag] = defaultdict(generate)
        sum_total = 0
        sum_once = 0
        for vocab in vocabs:
            found = False
            for key in vocab[0].keys():
                if levenshtein(tag, key, distance) < distance:
                    vgl[tag][vocab[1]] = vgl[tag][vocab[1]] + 1
                    matches.append((key, vocab[1]))
                    sum_total = sum_total + 1
                    found = True
                else:
                    vgl[tag][vocab[1]] = vgl[tag][vocab[1]]
            if found == True:
              sum_once = sum_once + 1
        vgl[tag]["sum_total"] = sum_total #number of actual overlaps (more than one per vocab possible)
        vgl[tag]["sum_once"] = sum_once #number of different vocabs
        vgl[tag]["matches"] = matches #pairs of matches + vocabularies they come from
    return vgl

def overlaps_overview(vocabs):
    comp = tag_compare(vocabs)
    sums = []
    for key in comp.keys():
        sums.append(comp[key]["sum"])
    sum_counter = Counter(sums)
    for key in sorted(sum_counter.keys()):
        if key == 1:
            print("No overlaps:", sum_counter[key], "keywords")
        else:
            print("Overlaps between", key, "vocabularies:", sum_counter[key], "keywords")

def overlaps_overview_fuzzy(vocabs, distance):
    comp = tag_compare_fuzzy(vocabs, distance)
    sums = []
    for key in comp.keys():
        sums.append(comp[key]["sum_once"])
    sum_counter = Counter(sums)
    for key in sorted(sum_counter.keys()):
        if key == 1:
            print("No overlaps:", sum_counter[key], "keywords")
        else:
            print("Overlaps between", key, "vocabularies:", sum_counter[key], "keywords")

def vocab_compare(vocab1, vocab2):
    zähler = 0
    for tag1 in vocab1.keys():
        for tag2 in vocab2.keys():
            if tag1 == tag2:
                zähler = zähler + 1
    return zähler

def vocab_compare_fuzzy(vocab1, vocab2, distance):
    zähler = 0
    found = False
    for tag1 in vocab1.keys():
        for tag2 in vocab2.keys():
            if levenshtein(tag1, tag2, distance) < distance:
                found = True
        if found == True: #counts only one match per tag1 - overlaps can be asymmetrical 
            zähler = zähler + 1
    return zähler

def vocab_matrix(vocabs):
    vocabs_dict = {}
    for vocab in vocabs:
        vocabs_dict[vocab[1]] = vocab[0]
    matrix = {}
    for entry in vocabs_dict.keys():
        for other in vocabs_dict.keys():
            titel = entry + "_" + other #e.g. acdh_dc
            count = vocab_compare(vocabs_dict[entry], vocabs_dict[other])
            matrix[titel] = count
    return matrix

def vocab_matrix_fuzzy(vocabs, distance):
    vocabs_dict = {}
    for vocab in vocabs:
        vocabs_dict[vocab[1]] = vocab[0]
    matrix = {}
    for entry in vocabs_dict.keys():
        for other in vocabs_dict.keys():
            titel = entry + "_" + other #e.g. acdh_dc
            count = vocab_compare_fuzzy(vocabs_dict[entry], vocabs_dict[other], distance)
            matrix[titel] = count
    return matrix

#generate table: number of overlaps between compared vocabularies
def table_overlaps(vocabs):
    matrix = vocab_matrix(vocabs)
    tabelle = []
    for vocab in vocabs:
        tabelle.append([vocab[1]])
    headers_tab = ["Vocabulary"]
    for element in tabelle:
        headers_tab = headers_tab + element
    zeile = 0
    for key in matrix.keys():
        tabelle[zeile].append(matrix[key])
        if len(tabelle[zeile]) == (len(vocabs) + 1): 
            zeile = zeile + 1
    print(tabulate(tabelle, headers = headers_tab))

def table_overlaps_fuzzy(vocabs, distance):
    matrix = vocab_matrix_fuzzy(vocabs, distance)
    tabelle = []
    for vocab in vocabs:
        tabelle.append([vocab[1]])
    headers_tab = ["Vocabulary"]
    for element in tabelle:
        headers_tab = headers_tab + element
    zeile = 0
    for key in matrix.keys():
        tabelle[zeile].append(matrix[key])
        if len(tabelle[zeile]) == (len(vocabs) + 1): 
            zeile = zeile + 1
    print(tabulate(tabelle, headers = headers_tab))

#generate table: percentage of overlaps between compared vocabularies
def table_relative(vocabs):
    matrix = vocab_matrix(vocabs)
    tabelle = []
    for vocab in vocabs:
        tabelle.append([vocab[1]])
    headers_tab = ["Vocabulary"]
    for element in tabelle:
        headers_tab = headers_tab + element
    zeile = 0
    for key in matrix.keys():
        tabelle[zeile].append(matrix[key])
        if len(tabelle[zeile]) == (len(vocabs) + 1): 
            zeile = zeile + 1
    tabelle_proz = []
    for row in tabelle:
        nur_zahlen = [x if type(x)==int else 0 for x in row]
        maximum = max(nur_zahlen)
        row_new = [round((x*100/maximum), 2) if type(x)==int else x for x in row]
        tabelle_proz.append(row_new)
    print(tabulate(tabelle_proz, headers = headers_tab))

#generate table: percentage of overlaps between compared vocabularies
def table_relative_fuzzy(vocabs, distance):
    matrix = vocab_matrix_fuzzy(vocabs, distance)
    tabelle = []
    for vocab in vocabs:
        tabelle.append([vocab[1]])
    headers_tab = ["Vocabulary"]
    for element in tabelle:
        headers_tab = headers_tab + element
    zeile = 0
    for key in matrix.keys():
        tabelle[zeile].append(matrix[key])
        if len(tabelle[zeile]) == (len(vocabs) + 1): 
            zeile = zeile + 1
    tabelle_proz = []
    for row in tabelle:
        nur_zahlen = [x if type(x)==int else 0 for x in row]
        maximum = max(nur_zahlen)
        row_new = [round((x*100/maximum), 2) if type(x)==int else x for x in row]
        tabelle_proz.append(row_new)
    print(tabulate(tabelle_proz, headers = headers_tab))

#generate heatmap of vocabularity similarity (= percentage of overlaps)
def heatmap(vocabs):
    matrix = vocab_matrix(vocabs)
    tabelle = []
    for vocab in vocabs:
        tabelle.append([vocab[1]])
    headers_tab = ["Vocabulary"]
    for element in tabelle:
        headers_tab = headers_tab + element
    zeile = 0
    for key in matrix.keys():
        tabelle[zeile].append(matrix[key])
        if len(tabelle[zeile]) == (len(vocabs) + 1): 
            zeile = zeile + 1
    tabelle_proz = []
    for row in tabelle:
        nur_zahlen = [x if type(x)==int else 0 for x in row]
        maximum = max(nur_zahlen)
        row_new = [round((x*100/maximum), 2) if type(x)==int else x for x in row]
        tabelle_proz.append(row_new)
    
    #Zeilen- und Spaltenlabels definieren
    zeilen = []
    for vocab in vocabs:
        zeilen.append(vocab[1])
    spalten = zeilen

    #Daten definieren
    tabelle_proz_zahlen = [] #neue Liste von Listen exkl. Strings notwendig
    for zeile in tabelle_proz:
        nur_zahlen = [x for x in zeile if type(x)!=str]
        tabelle_proz_zahlen.append(nur_zahlen)
    daten = np.array(tabelle_proz_zahlen)

    #Initialisieren von Plots
    fig, heatmap = plt.subplots()
    im = heatmap.imshow(daten, cmap="YlGn")

    #Größe der Abbildung einstellen
    fig.set_figheight(8)
    fig.set_figwidth(10)

    #Labels hinzufügen
    heatmap.set_xticks(np.arange(len(spalten)), labels=spalten)
    heatmap.set_yticks(np.arange(len(zeilen)), labels=zeilen)

    #Spaltenbeschriftung nach oben
    heatmap.tick_params(top=True, bottom=False, labeltop=True, labelbottom=False)

    #Spaltenbeschriftung rotieren
    plt.setp(heatmap.get_xticklabels(), rotation=45, ha="left", rotation_mode="anchor")

    #Loop über Daten --> Werte pro Heatmap-Kästchen anzeigen
    for i in range(len(zeilen)):
        for j in range(len(spalten)):
            text = heatmap.text(j, i, daten[i, j], ha="center", va="center", color="black")

    #Legende (Colorbar) hinzufügen
    legende = heatmap.figure.colorbar(im, ax=heatmap)
    legende.ax.set_ylabel(ylabel="Overlaps in percent", rotation=-90, va="bottom")

    #Titel hinzufügen
    heatmap.set_title("Similarity of vocabularies", fontsize=15)

    #Verbesserung des Layouts
    fig.tight_layout()

    #return fig
    plt.show()
    
#generate heatmap of vocabularity similarity (= percentage of overlaps)
def heatmap_fuzzy(vocabs, distance):
    matrix = vocab_matrix_fuzzy(vocabs, distance)
    tabelle = []
    for vocab in vocabs:
        tabelle.append([vocab[1]])
    headers_tab = ["Vocabulary"]
    for element in tabelle:
        headers_tab = headers_tab + element
    zeile = 0
    for key in matrix.keys():
        tabelle[zeile].append(matrix[key])
        if len(tabelle[zeile]) == (len(vocabs) + 1): 
            zeile = zeile + 1
    tabelle_proz = []
    for row in tabelle:
        nur_zahlen = [x if type(x)==int else 0 for x in row]
        maximum = max(nur_zahlen)
        row_new = [round((x*100/maximum), 2) if type(x)==int else x for x in row]
        tabelle_proz.append(row_new)

    #Zeilen- und Spaltenlabels definieren
    zeilen = []
    for vocab in vocabs:
        zeilen.append(vocab[1])
    spalten = zeilen

    #Daten definieren
    tabelle_proz_zahlen = [] #neue Liste von Listen exkl. Strings notwendig
    for zeile in tabelle_proz:
        nur_zahlen = [x for x in zeile if type(x)!=str]
        tabelle_proz_zahlen.append(nur_zahlen)
    daten = np.array(tabelle_proz_zahlen)

    #Initialisieren von Plots
    fig, heatmap = plt.subplots()
    im = heatmap.imshow(daten, cmap="YlGn")

    #Größe der Abbildung einstellen
    fig.set_figheight(8)
    fig.set_figwidth(10)

    #Labels hinzufügen
    heatmap.set_xticks(np.arange(len(spalten)), labels=spalten)
    heatmap.set_yticks(np.arange(len(zeilen)), labels=zeilen)

    #Spaltenbeschriftung nach oben
    heatmap.tick_params(top=True, bottom=False, labeltop=True, labelbottom=False)

    #Spaltenbeschriftung rotieren
    plt.setp(heatmap.get_xticklabels(), rotation=45, ha="left", rotation_mode="anchor")

    #Loop über Daten --> Werte pro Heatmap-Kästchen anzeigen
    for i in range(len(zeilen)):
        for j in range(len(spalten)):
            text = heatmap.text(j, i, daten[i, j], ha="center", va="center", color="black")

    #Legende (Colorbar) hinzufügen
    legende = heatmap.figure.colorbar(im, ax=heatmap)
    legende.ax.set_ylabel(ylabel="Overlaps in percent", rotation=-90, va="bottom")

    #Titel hinzufügen
    heatmap.set_title("Similarity of vocabularies", fontsize=15)

    #Verbesserung des Layouts
    fig.tight_layout()

    plt.show()

#print tags that appear in at least x vocabularies (+ the respective vocabularies)
def keywords_multiple(vocabs, x):
    comp = tag_compare(vocabs)
    for key in comp.keys():
        if comp[key]["sum"] >= x:
            vocabs_list = []
            for element in comp[key].keys():
                if element == "sum":
                    continue
                if comp[key][element] == 1:
                    vocabs_list.append(element)
            print(key, vocabs_list)

def keywords_multiple_fuzzy(vocabs, x, distance):
    comp = tag_compare_fuzzy(vocabs, distance)
    for key in comp.keys():
        if comp[key]["sum_once"] >= x:
            vocabs_list = []
            for element in comp[key].keys():
                if element == "sum_once":
                    continue
                if comp[key][element] == 1:
                    vocabs_list.append(element)
            print(key, vocabs_list)

#print tags that appear in only one vocabulary (+ the respective vocabulary)
def keywords_single(vocabs, limit):
    comp = tag_compare(vocabs)
    count = {}
    for key in comp.keys():
        if comp[key]["sum"] == 1:
            for element in comp[key].keys():
                if element == "sum":
                  continue
                if comp[key][element] == 1:
                  if element not in count.keys():
                    count[element] = 0
                  else:
                    count[element] += 1
                    if count[element] <= limit:
                      print(key, "(" + element + ")")
            
#print tags that appear in only one vocabulary (+ the respective vocabulary)
def keywords_single_fuzzy(vocabs, limit, distance):
    comp = tag_compare_fuzzy(vocabs, distance)
    count = {}
    for key in comp.keys():
        if comp[key]["sum_once"] == 1:
            for element in comp[key].keys():
                if element == "sum_once":
                  continue
                if comp[key][element] == 1:
                  if element not in count.keys():
                    count[element] = 0
                  else:
                    count[element] += 1
                    if count[element] <= limit:
                      print(key, "(" + element + ")")

#show overlaps between multiple vocabs (= tags that appear in all listed vocabs)
def show_overlaps(vocab_liste):
    for tag in vocab_liste[0]:
        status = 1
        goal = len(vocab_liste)
        for vocab in vocab_liste[1:]:
            if tag in vocab.keys():
                status = status + 1
        if status == goal:
            print(tag)

#check for specific tag
def search(vocabs, word):
    comp = tag_compare(vocabs)
    if word in comp.keys():
        vocabs_list = []
        for element in comp[word].keys():
            if element == "sum":
                continue
            if comp[word][element] == 1:
                vocabs_list.append(element)
        print("The keyword \"" + word + "\" is used in " + str(comp[word]["sum"]) + " different vocabularies, namely in:")
        print(vocabs_list)
    else:
        print("The keyword does not appear in any of the compared vocabularies.")

def search_fuzzy(vocabs, word, distance):
    comp = tag_compare_fuzzy(vocabs, distance)
    if word in comp.keys():
        vocabs_list = []
        for element in comp[word].keys():
            if element == "sum_once" or element == "sum_total" or element == "matches":
                continue
            if comp[word][element] >= 1:
                vocabs_list.append(element)
        print("The keyword \"" + word + "\" is used in " + str(comp[word]["sum_once"]) + " different vocabularies, namely in:")
        print(vocabs_list)
        print("Within the fuzzy matching, it is matched to the following variants:")
        print(comp[word]["matches"])
    else:
        print("The keyword does not appear in any of the compared vocabularies.")

#show all tags for a certain vocab, alphabetically ordered
def show(vocab):
    keywords = [x for x in vocab.keys()]
    keywords_sorted = sorted(keywords)
    for keyword in keywords_sorted:
        print(keyword)

#show_length()
def show_length(vocab):
    print(len(vocab))

#length_overview()
def length_overview(vocabs):
    for vocab in vocabs:
        length = len(vocab[0])
        name = vocab[1]
        print(name + ": " + str(length) + " keywords")

#keywords_distinct()
def keywords_distinct(vocabs):
    tags = []
    for vocab in vocabs:
        for key in vocab[0].keys():
            if key not in tags:
                tags.append(key)
    return(len(tags))

def matches(vocabs, vocab, distance):
    comp = tag_compare_fuzzy(vocabs, distance)
    for key in vocab.keys():
        print(comp[key]["matches"])