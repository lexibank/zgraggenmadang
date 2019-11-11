from pathlib import Path

import attr
from clldutils.misc import slug
from pylexibank import Language
from pylexibank.dataset import Dataset as BaseDataset
from pylexibank.util import progressbar

# In this dataset (madang.csv), the concepts are named according
# to https://transnewguinea.org so the file ./etc/concepts.csv is
# used to rename these to match the original concepts found in
# Zgraggen.
CONCEPT_REMAPPING = {
    "afraid": "be afraid",
    "arrow": "arrow (arrow a)",
    "arrow-barred": "barred arrow (arrow b)",
    "arrow-hooked": "hooked arrow (arrow c)",
    "arrow-pronged": "pronged arrow (arrow d)",
    "axe": "axe (stone)",
    "axe-iron": "axe (iron)",
    "betelpepper": "betel pepper vine",
    "bowstring": "rope (of bow)",
    "breast": "breast (woman)",
    "calf": "calf (of leg)",
    "chicken-tame": "chicken (tame)",
    "chicken-wild": "chicken (wild)",
    "coconut-palm": "coconut tree",
    "day-after-tomorrow": "day after tomorrow",
    "day-before-yesterday": "day before yesterday",
    "daybreak": "day break",
    "drum": "signal drum",
    "face-forehead": "face (forehead)",
    "faeces": "excrement",
    "fell-tree": "fell (a tree)",
    "firelight": "light (of fire)",
    "fish-spear": "fish spear",
    "fly-sp": "fly (n)",
    "flying-fox": "flying fox",
    "forest": "woods",
    "g-string": "G-string",
    "ground-possum": "possum (ground)",
    "how-many": "how many",
    "i": "I",
    "in": "inside (the house)",
    "left-arm": "left (arm)",
    "lungs": "lung",
    "net-bag": "netbag",
    "old": "old (of humans)",
    "plate": "wooden plate",
    "pot": "saucepan (clay pot)",
    "right-arm": "right (arm)",
    "root": "root (of tree)",
    "short-piece-wood": "piece of wood",
    "shrub": "shrub (tanget)",
    "sibling-opposite-sex-older": "sibling different sex, older",
    "sibling-opposite-sex-younger": "sibling different sex, younger",
    "sibling-same-sex-older": "sibling same sex, older",
    "sibling-same-sex-younger": "sibling same sex, younger",
    "singapore-taro": "singapore taro",
    "skirt": "grass skirt",
    "slow": "slowly",
    "sore-wound": "sore",
    "spear-n": "spear",
    "stomach": "stomach (guts)",
    "stump": "stump (of tree)",
    "sugarcane": "sugar cane",
    "tail": "tail (of dog)",
    "thunder": "thundering",
    "to-bathe": "bathe (itr)",
    "to-be": "be",
    "to-be-hungry": "hungry",
    "to-be-sick": "be sick",
    "to-bite": "bite",
    "to-blow": "blow (on fire)",
    "to-boil": "boil",
    "to-break": "break (across)",
    "to-burn": "burn",
    "to-bury": "bury",
    "to-buy-sell-barter": "buy",
    "to-call-out": "call out",
    "to-carry": "carry (on back)",
    "to-chop": "chop (with axe)",
    "to-come": "come",
    "to-cough": "cough",
    "to-cry": "cry",
    "to-cut": "cut (with knife)",
    "to-dance": "dance",
    "to-die": "die",
    "to-dig": "dig",
    "to-do-make": "make",
    "to-eat": "eat",
    "to-fall": "fall (tree)",
    "to-fasten": "fasten",
    "to-fight": "fight (hit)",
    "to-fill": "fill up (water)",
    "to-fly": "fly (v)",
    "to-give": "give",
    "to-go": "go",
    "to-go-down": "go down",
    "to-go-up": "go up",
    "to-hear": "hear",
    "to-hold": "hold",
    "to-jump": "jump",
    "to-kill": "kill",
    "to-laugh": "laugh",
    "to-look": "look for",
    "to-plant": "plant",
    "to-pour-out": "pour out (liquid)",
    "to-pull": "pull",
    "to-push": "push",
    "to-put": "put",
    "to-roast": "roast",
    "to-run": "run",
    "to-scratch": "scratch (skin)",
    "to-see": "see (tr)",
    "to-sharpen": "sharpen a bow",
    "to-shoot": "shoot",
    "to-sit": "sit down",
    "to-sleep": "sleep",
    "to-smell": "smell",
    "to-split": "split",
    "to-stand": "stand",
    "to-swallow": "swallow",
    "to-sweat": "sweat",
    "to-swell": "swell up (skin)",
    "to-take": "take",
    "to-talk": "talk to (tr)",
    "to-tear": "tear",
    "to-think": "think",
    "to-throw": "throw (stone)",
    "to-tie": "tie",
    "to-turn": "turn (oneself)",
    "to-vomit": "vomit",
    "to-walk": "walk",
    "to-wash": "wash (tr)",
    "to-watch": "watch (itr)",
    "to-work": "work",
    "tree-possum": "possum (tree)",
    "tree-top": "top (of tree)",
    "trunk": "trunk (of tree)",
}


@attr.s
class CustomLanguage(Language):
    Source = attr.ib(default=None)


class Dataset(BaseDataset):
    dir = Path(__file__).parent
    id = "zgraggenmadang"
    language_class = CustomLanguage

    def cmd_download(self, args):
        pass

    def cmd_makecldf(self, args):
        args.writer.add_sources()
        languages = args.writer.add_languages(
            id_factory=lambda l: l["Name"], lookup_factory=lambda l: (l["Name"], l["Source"])
        )
        sources = {k[0]: k[1] for k in languages}  # language: source map
        concepts = args.writer.add_concepts(
            id_factory=lambda c: c.id.split("-")[-1] + "_" + slug(c.english), lookup_factory="Name"
        )
        for row in progressbar(self.raw_dir.read_csv("madang.csv", dicts=True, delimiter="\t")):
            concept = CONCEPT_REMAPPING.get(row["CONCEPT"], row["CONCEPT"])
            args.writer.add_forms_from_value(
                Local_ID=row["ID"],
                Language_ID=row["DOCULECT"],
                Parameter_ID=concepts[concept],
                Value=row["COUNTERPART"],
                Source=sources[row["DOCULECT"]],
            )
