# -*- coding: utf-8 -*-
# Copyright: Damien Elmes <anki@ichi2.net>
# Derived Program Author: Alejandro Alvarado
# License: GNU AGPL, version 3 or later; 
# http://www.gnu.org/licenses/agpl.html

# Read card information from a file
# and use Anki exporters to create
# an .apkg package to import into Anki
# desktop.

import sys, os, tempfile, re

sys.path.append("../.")

from anki import Collection as aopen
from anki.exporting import *
from tests.shared import getEmptyCol

def main():
    # Takes two files, the first will be 
    # the input file and the second will 
    # be the .apkg file location
    try:
        assert(os.path.isfile(sys.argv[1]))
        assert(os.path.isfile(sys.argv[2]))
        export_from_file(sys.argv[1], sys.argv[2])

    except IndexError:
        print("Requires a file path name to read")
    except AssertionError:
        print("Argument is not a file path")
    
def export_from_file(in_file, out_file):
    # Use the existing exporting tools
    # from Anki to create .apkg package
    
    deck = getEmptyCol()

    # Rename the deck
    # (Not working, still puts cards in Default)
    deck_id = deck.decks.id('Default')
    deck.decks.rename(deck.decks.get(deck_id), 'ClojureFunctions')

    # Add some custom fields and views
    deck = add_custom_model(deck)

    deck = add_cards_to_deck(in_file, deck)

    exporter = AnkiPackageExporter(deck)
    exporter.exportInto(out_file)

def add_cards_to_deck(in_file, deck):
    # Opens the file and creates individual
    # flashcards.
    pattern = re.compile(r"name: (.*) url: (.*) args: (.*) docstring:(.*)")
    
    with open(in_file, 'r') as open_file:
        for line in open_file:
            result = pattern.search(line)

            if not result == None:                
                note = deck.newNote()
                note['Function'] = result.group(1)
                note['URL'] = result.group(2)
                note['Usage'] = result.group(3)
                note['Docstring'] = result.group(4)
                deck.addNote(note)
            else:
                print("Could not add: ", line)

    return deck

def add_custom_model(col):
    # This will add a new fields to the collection.
    # The fields are needed for custom clojure information.
    models = col.models
    model = models.new("Clojure")
    
    models = add_fields(["Function", "Usage",
                         "Docstring", "URL"],
                        models, model)
    
    template = models.newTemplate("Card 1")
    
    #Format each field on the flashcard
    function = "{{Function}}<br><br>"
    url = "{{URL}}<br>"
    usage = "{{Usage}}<br><br>"
    docstring = "{{Docstring}}<br>"
    back_side = "{{FrontSide}}\n\n<hr id=answer>\n\n"
    template['qfmt'] = function + url
    template['afmt'] = back_side + usage + docstring 
    models.addTemplate(model, template)
    models.add(model)
    
    col.models = models
    return col


def add_fields(fields, models, model):
    # Creates and adds the custom fields

    for field in fields:
        new_field = models.newField(field)
        models.addField(model, new_field)

    return models

if __name__ == '__main__':
    main()
