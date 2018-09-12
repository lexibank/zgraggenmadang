# coding=utf-8
from __future__ import unicode_literals, print_function
import re

import attr
import lingpy
from clldutils.path import Path
from pylexibank.dataset import Metadata
from pylexibank.dataset import Dataset as BaseDataset, Language
from pylexibank.util import getEvoBibAsBibtex

# Whether to use lexstat to cluster cognates (allowing to
# align them)
USE_LEXSTAT = False


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
                # remove parentheses with part-of-speech information;
                # we are not using clldutils here because all other
                # parentheses are actually sound information (manually
                # checked, there might be errors!)
                counterpart = re.sub(r'(.*)(\s\(.*\))$', r'\1', counterpart)

                # correct multiple spaces and strip leading&trailing ones
                counterpart = re.sub(r'\s+', ' ', counterpart).strip()

                # tokenize
                tokens = self.tokenizer(None, counterpart, column='IPA')

            # add to wordlist data
            wl_data[idx] = [_, doculect, concept, counterpart, tokens]

        log.info('... data assembled ...')

        # build lingpy wordlist and check cognancy; the parameters
        # are from Mattis internal notes, an alternative is lexstat with the
        # (also high) threshold of 0.8
        wl = lingpy.Wordlist(wl_data, row='concept', col='doculect')
        log.info('... Wordlist initialized ...')
        lex = lingpy.LexStat(wl, segments='tokens', check=True, apply_checks=True, cldf=True)
        log.info('... LexStat initialized ...')
        if USE_LEXSTAT:
            lex.cluster(method='sca', threshold=0.5)
        log.info('... done')

        # build CLDF data
        with self.cldf as ds:
            ds.add_sources()
            # add languages, and build dictionary of sources
            ds.add_languages(id_factory=lambda l: l['Name'])
            lang_source = {l['Name']: l['Source'] for l in self.languages}

            # add concepts; the set for this dataset is actually
            # a bit different from the Z'graggen list that was
            # already in concepticon, so we must use the local
            # concept mapping
            for concept in self.concepts:
                ds.add_concept(
                    ID=concept['ENGLISH'],
                    Concepticon_ID=concept['CONCEPTICON_ID'],
                    Name=concept['CONCEPTICON_GLOSS'],
                )

            # add lexemes
            for concept in wl.rows:
                for doculect, value in wl.get_dict(row=concept).items():
                    for idx in value:
                        if USE_LEXSTAT:
                            cogid = lex[idx, 'scaid']
                        else:
                            cogid = None

                        # use an empty counterpart (and a `tokens` list with a
                        # single "unknown" value) if the current counterpart
                        # does not exist
                        if lex[idx, 'counterpart'] is None:
                            counterpart = ''
                            tokens = ['0']
                        else:
                            counterpart = lex[idx, 'counterpart']
                            tokens = lex[idx, 'tokens']

                        # add the lexeme
                        for row in ds.add_lexemes(
                            Language_ID=doculect,
                            Parameter_ID=concept,
                            Value=counterpart,
                            Source=lang_source[doculect],
                            Segments = tokens):
                            if USE_LEXSTAT:
                                ds.add_cognate(
                                    lexeme=row,
                                    Cognateset_ID='%s-%s' % (concept, cogid),
                                    Source=['List2014e'],
                                    Alignment_Source='List2014e')
                            else:
                                ds.add_cognate(
                                    lexeme=row,
                                    Cognateset_ID='%s-%s' % (concept, cogid),
                                    Source=[],
                                    Alignment_Source=None)

            if USE_LEXSTAT:
                ds.align_cognates()

    def cmd_download(self, **kw):
        if not self.raw.exists():
            self.raw.mkdir()
        self.raw.write('sources.bib', getEvoBibAsBibtex('Zgraggen1980NA', 'Zgraggen1980RC', 'Zgraggen1980SA', 'Zgraggen1980MA', 'List2014e', **kw))
