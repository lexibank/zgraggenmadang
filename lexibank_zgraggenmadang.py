# coding=utf-8
from __future__ import unicode_literals, print_function
import re

import attr
from clldutils.path import Path
from pylexibank.dataset import Metadata
from clldutils.misc import slug
from pylexibank.dataset import Dataset as BaseDataset, Language
from pylexibank.util import getEvoBibAsBibtex, pb


@attr.s
class Variety(Language):
    Source = attr.ib(default=None)


class Dataset(BaseDataset):
    dir = Path(__file__).parent
    id = 'zgraggenmadang'
    language_class = Variety

    def cmd_install(self, **kw):
        #wl_data = {}
        wl_data = []
        log = kw['log']
        log.info('building wordlist ...')
        for idx, row in enumerate(self.raw.read_tsv('madang.csv')):
            if idx > 1:
                # get fields for the entry, correcting it if necessary
                _, doculect, concept, counterpart = row
                if counterpart in self.lexemes:
                    counterpart = self.lexemes[counterpart]

                # add to wordlist data
                wl_data.append({
                    'doculect' : doculect,
                    'concept' : concept,
                    'counterpart' : counterpart,
                })

        log.info('... data assembled ...')

        # build CLDF data
        with self.cldf as ds:
            ds.add_sources()

            # add languages, and build dictionary of sources
            ds.add_languages(id_factory=lambda l: l['Name'])
            lang_source = {l['Name']: l['Source'] for l in self.languages}

            for concept in self.concepts:
                ds.add_concept(
                        ID=slug(concept['ENGLISH']),
                        Concepticon_ID=concept['CONCEPTICON_ID'],
                        Name=concept['ENGLISH']
                        )

            for concept in self.conceptlist.concepts.values():
                ds.add_concept(
                    ID=slug(concept.english),
                    Concepticon_ID=concept.concepticon_id,
                    Name=concept.concepticon_gloss
                )

            # add lexemes
            for row in wl_data:
                ds.add_lexemes(
                    Language_ID=row['doculect'],
                    Parameter_ID=slug(row['concept']),
                    Value=row['counterpart'],
                    Source=lang_source[row['doculect']],
                )


    def cmd_download(self, **kw):
        if not self.raw.exists():
            self.raw.mkdir()
        self.raw.write('sources.bib', getEvoBibAsBibtex('Zgraggen1980NA', 'Zgraggen1980RC', 'Zgraggen1980SA', 'Zgraggen1980MA', 'List2014e', **kw))
