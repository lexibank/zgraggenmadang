# coding=utf-8
from __future__ import unicode_literals, print_function
import re

import attr
import lingpy
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
        # read raw contents and build dictionary for lingpy's wl
        wl_data = {}
        header = True
        log = kw['log']
        log.info('building wordlist ...')
        for idx, row in enumerate(self.raw.read_tsv('madang.csv')):
            # get fields for the entry, correcting it if necessary
            _, doculect, concept, counterpart = row
            if counterpart in self.lexemes:
                counterpart = self.lexemes[counterpart]

            # correct fields if necessary; we add the 'TOKEN' column
            # header (missing from madang.csv) here
            if header:
                tokens = 'TOKENS'
                header = False
            else:
                counterpart = re.sub(r'(.*)(\s\(.*\))$', r'\1', counterpart)

                # correct multiple spaces and strip leading&trailing ones
                counterpart = re.sub(r'\s+', ' ', counterpart).strip()

                # tokenize
                tokens = self.tokenizer(None, counterpart, column='IPA')

            # add to wordlist data
            wl_data[idx] = [_, doculect, concept, counterpart, tokens]

        log.info('... data assembled ...')

        wl = lingpy.Wordlist(wl_data, row='concept', col='doculect')

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
            for concept in pb(wl.rows, desc='cldfify'):
                for doculect, value in wl.get_dict(row=concept).items():
                    for idx in value:

                        # add the lexeme
                        ds.add_lexemes(
                                Language_ID=doculect,
                                Parameter_ID=slug(concept),
                                Value=counterpart,
                                Source=lang_source[doculect],
                            )

    def cmd_download(self, **kw):
        if not self.raw.exists():
            self.raw.mkdir()
        self.raw.write('sources.bib', getEvoBibAsBibtex('Zgraggen1980NA', 'Zgraggen1980RC', 'Zgraggen1980SA', 'Zgraggen1980MA', 'List2014e', **kw))
