# -*- coding: utf-8 -*-

import json
import sqlite3
import sys
import unicodedata

def select_deck():
    decks = []
    for row in c.execute('SELECT decks FROM col'):
        deks = json.loads(row[0])
        for key in deks:
            d_id = deks[key]['id']
            d_name = deks[key]['name']
            decks.append((d_id, d_name))

    print('Which deck would you like to use?\n')

    for i in range(len(decks)):
        print(' ['+str(i)+'] '+decks[i][1])
    inp = int(input('\n'))
    return decks[inp]

conn = sqlite3.connect('collection.anki2')
c = conn.cursor()

deck_tpl = select_deck()
deck_id = deck_tpl[0]
anki_cards = []
kanji = []

for row in c.execute('SELECT sfld FROM notes WHERE id IN (SELECT nid FROM cards WHERE did IS ' + str(deck_id) + ')'):
    voc = row[0]
    anki_cards.append(voc)
    for i in range(0, len(row[0])):
        char = voc[i]
        try:
            if(unicodedata.name(char).find('CJK UNIFIED IDEOGRAPH') >= 0):
                if(not char in kanji):
                    kanji.append(char)
        except ValueError:
            pass

if len(sys.argv) > 1:
    min_len = sys.argv[1]
else:
    min_len = 0

kanji_required = False
kanji_only = False
kana_only = False
if len(sys.argv) > 2:
    if sys.argv[2] == 'kr':
        kanji_required = True
    if sys.argv[2] == 'ko':
        kanji_only = True
    if sys.argv[2] == 'nk':
        kana_only = True

f = open('word_list')
of = open('output', 'w')
i = -1
for line in f:
    i+=1
    w = line.rstrip().replace(u'\ufeff', '')
    if len(w) < int(min_len):
        continue
    writable = True
    has_kanji = False
    for char in w:
        has_other = False
        if unicodedata.name(char).find('CJK UNIFIED IDEOGRAPH') >= 0:
            has_kanji = True
            if not char in kanji:
                writable = False
                break
        else:
            has_other = True
            break
    if kanji_only and has_other:
        continue
    if kanji_required and not has_kanji:
        continue
    if kana_only and has_kanji:
        continue
    if not writable:
        continue

    in_anki = False
    for voc in anki_cards:
        if w in voc:
            in_anki = True
            break
    if not in_anki:
        of.write(str(i) + ': ' + w + '\n')
f.close()
of.close()
