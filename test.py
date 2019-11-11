def test_valid(cldf_dataset, cldf_logger):
    assert cldf_dataset.validate(log=cldf_logger)


def test_forms(cldf_dataset):
    # check one specific form to make sure columns, values are correct.
    # 118700	matepi	all	ɛgirɛ
    f = [f for f in cldf_dataset["FormTable"] if f["Local_ID"] == "118700"]
    assert len(f) == 1
    assert f[0]["Parameter_ID"] == "4_all"
    assert f[0]["Language_ID"] == "matepi"
    assert f[0]["Form"] == "ɛgirɛ"


def test_languages(cldf_dataset):
    # siroi,siroi,siro1249,Siroi,,,,,,Zgraggen1980RC
    f = [f for f in cldf_dataset["LanguageTable"] if f["ID"] == "siroi"]
    assert len(f) == 1
    assert f[0]["Name"] == "siroi"
    assert f[0]["Glottocode"] == "siro1249"
    assert f[0]["Glottolog_Name"] == "Siroi"


def test_parameters(cldf_dataset):
    f = [f for f in cldf_dataset["ParameterTable"] if f["ID"] == "16_siblingdifferentsexyounger"]
    assert len(f) == 1
    assert f[0]["Name"] == "sibling different sex, younger"
    assert f[0]["Concepticon_ID"] == "3040"
    assert f[0]["Concepticon_Gloss"] == "DIFFERENT-SEX YOUNGER SIBLING"


def test_sources(cldf_dataset):
    assert len(cldf_dataset.sources) == 4
