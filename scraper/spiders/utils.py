SEARCH_ENDPOINT = "https://side.developpement-durable.gouv.fr/{catalogue}/Portal/Recherche/Search.svc/Search"

LIST_DOCUMENTS_ENDPOINT = "https://side.developpement-durable.gouv.fr/{catalogue}/DigitalCollectionService.svc/ListDigitalDocuments?parentDocumentId={parent_document_id}&start={start}&limit=10&includeMetaDatas=false"

DOWNLOAD_ENDPOINT = "https://side.developpement-durable.gouv.fr/{catalogue})/digitalCollection/DigitalCollectionAttachmentDownloadHandler.ashx?parentDocumentId={parent_document_id}&documentId={document_id}&skipWatermark=true&skipCopyright=true"


AE_CGDD = {  # AE Ministère
    "catalogue": "PAE",
    "scenario_code": "AE-CGDD",
    "year_filter": "_1295",
    "categories": {
        "Saisines cas par cas": 'Field950i_idx:"cours d\'instruction" AND LocalClassification1_idx:"Cas par cas*" AND AgenceCatalogage_idx:"CGDD"',
        "Décisions cas par cas": '(LocalClassification1_idx:"Cas par cas" NOT Field950i_idx:"cours d\'instruction") AND AgenceCatalogage_idx:CGDD',
        "Saisines pour avis": 'Field950i_idx:"cours d\'instruction" AND LocalClassification1_idx:"Avis" AND AgenceCatalogage_idx:CGDD',
        "Avis": '(LocalClassification1_idx:"Avis" NOT Field950i_idx:"cours d\'instruction") AND AgenceCatalogage_idx:CGDD',
        "Saisines cadrage préalable": 'Field950i_idx:"cours d\'instruction" AND LocalClassification1_idx:"Cadrage prealable" AND AgenceCatalogage_idx:CGDD',
        "Cadrages préalables": '(LocalClassification1_idx:"Cadrage prealable" NOT Field950i_idx:"cours d\'instruction") AND AgenceCatalogage_idx:CGDD',
    },
}

REGIONS = [
    "Auvergne-Rhône-Alpes",
    "Bourgogne-Franche Comté",
    "Bretagne",
    "Centre-Val de Loire",
    "Corse",
    "Grand-Est",
    "Guadeloupe",
    "Guyane",
    "Hauts de France",
    "Île de France",
    "Martinique",
    "Mayotte",
    "Normandie",
    "Nouvelle Aquitaine",
    "Occitanie",
    # "Provence-Alpes-Côte d'Azur", # only archives, recent docs on DREAL website https://side.developpement-durable.gouv.fr/pae/autorite-environnementale-paca-new.aspx
]


REGIONS_SPECIAL_CASES = {
    "La Réunion": {
        "catalogue": "REUN",
        "scenario_code": "CATAREUN",
        "year_filter": "_1580",
        "categories": {
            "Avis sur les Projets": 'LocalClassification2_idx:"avis projet"',
            "Avis sur les Plans et Programmes": 'LocalClassification2_idx:"Avis plans*"',
            "Décisions cas par cas Projets": 'LocalClassification2_idx:"cas par cas projet"',
            "Décisions cas par cas Plans et Programmes ": 'LocalClassification2_idx:"cas par cas plan*"',
        },
    },
    "Pays de la Loire": {
        "catalogue": "PAE",
        "scenario_code": "AE-GENERAL",
        "year_filter": "_1722",
        "categories": {
            "Saisines Cas par cas projet": 'Field950i_idx:"cours d\'instruction" AND LocalClassification1_idx:"Cas par cas" AND AgenceCatalogage_idx :"*Pays-de-Loire"',
            "Décisions Cas par cas projet": '(LocalClassification1_idx:"Cas par cas" NOT Field950i_idx:"cours d\'instruction") AND AgenceCatalogage_idx:"-Pays-de-Loire"',
        },
    },
    "Saint-Pierre et Miquelon": {
        "catalogue": "PAE",
        "scenario_code": "AE-GENERAL",
        "year_filter": "_1722",
        "categories": {
            "Tous les Cas par cas projet": 'SubjectLocation_idx:"Saint-Pierre-et-Miquelon" OR AgenceCatalogage_idx:"*Saint-Pierre-et-Miquelon"'
        },
    },
}


HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "en-US,en;q=0.5",
    # 'Accept-Encoding': 'gzip, deflate, br',
    "Referer": "https://side.developpement-durable.gouv.fr/PAE/search.aspx",
    "Content-Type": "application/json; charset=utf-8",
    "X-Requested-With": "XMLHttpRequest",
    "Origin": "https://side.developpement-durable.gouv.fr",
    "DNT": "1",
    "Connection": "keep-alive",
    # 'Cookie': "_syrPrefsGuid=f1fbdace-0dc6-4da8-811b-fccd5e4d5ab0; _syrSessGuid=ca703cfd-a166-41a3-82c9-0f14c01790a5; InstanceST=EXPLOITATION=00040IEaxdUu8Us1jTZzUQVJSM74VzH4PJ5G4UWzvrrku47DEQpj8HBSa+/TImW+5JCeuQeRkm5NMpJWZG3hSuFU=; InstanceCI=EXPLOITATION=ny7j0el-ku6EvRPwlkCS7Kua8rofc8iZnv7cDkYX; ErmesSearch_Default=%7B%22mainScenario%22%3A%22CATALOGUE%22%2C%22mainScenarioText%22%3A%22Catalogue%20g%C3%A9n%C3%A9ral%22%7D; ErmesSearch_PAE=%7B%22mainScenario%22%3A%22AE-CGDD%22%2C%22mainScenarioText%22%3A%22AE%20Minist%C3%A8re%22%2C%22search%22%3A%7B%22query%22%3A%7B%22CloudTerms%22%3A%5B%5D%2C%22ExceptTotalFacet%22%3Atrue%2C%22FacetFilter%22%3A%22%7B%7D%22%2C%22ForceSearch%22%3Atrue%2C%22HiddenFacetFilter%22%3A%22%7B%7D%22%2C%22InitialSearch%22%3Afalse%2C%22Page%22%3A0%2C%22PageRange%22%3A3%2C%22QueryGuid%22%3A%22a3497a68-139e-418a-bd48-b5bfda651b18%22%2C%22QueryString%22%3A%22Field950i_idx%3A%5C%22cours%20d'instruction%5C%22%20AND%20LocalClassification1_idx%3A%5C%22Cas%20par%20cas*%5C%22%20AND%20AgenceCatalogage_idx%3A%5C%22CGDD%5C%22%22%2C%22ResultSize%22%3A10%2C%22ScenarioCode%22%3A%22AE-CGDD%22%2C%22ScenarioDisplayMode%22%3A%22display-standard%22%2C%22SearchContext%22%3A14%2C%22SearchGridFieldsShownOnResultsDTO%22%3A%5B%5D%2C%22SearchLabel%22%3A%22Field950i_idx%3A%5C%22cours%20d'instruction%5C%22%20AND%20LocalClassification1_idx%3A%5C%22Cas%20par%20cas*%5C%22%20AND%20AgenceCatalogage_idx%3A%5C%22CGDD%5C%22%22%2C%22SearchTerms%22%3A%22Field950i_idx%20cours%20d%20instruction%20AND%20LocalClassification1_idx%20Cas%20par%20cas%20AgenceCatalogage_idx%20CGDD%22%2C%22SortField%22%3A%22DateOfInsertion_sort%22%2C%22SortOrder%22%3A0%2C%22TemplateParams%22%3A%7B%22Scenario%22%3A%22%22%2C%22Scope%22%3A%22PAE%22%2C%22Size%22%3Anull%2C%22Source%22%3A%22%22%2C%22Support%22%3A%22%22%2C%22UseCompact%22%3Afalse%7D%2C%22UseSpellChecking%22%3Anull%7D%2C%22sst%22%3A4%7D%7D",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "Sec-GPC": "1",
    # Requests doesn't support trailers
    # 'TE': 'trailers',
}

HEADERS2 = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.5",
    # 'Accept-Encoding': 'gzip, deflate, br',
    "Referer": "https://side.developpement-durable.gouv.fr/PAE/search.aspx",
    "DNT": "1",
    "Connection": "keep-alive",
    # 'Cookie': "_syrPrefsGuid=e7d536cc-b3ef-4550-bf48-aea81c137feb; _syrSessGuid=d9113de1-d105-4e0b-80b9-6cedcc7e3c52; InstanceST=EXPLOITATION=00040Qy1KjajFRUKgCQvsoxYCdw_y4UeOfbQM5Y6VjHBA47DEQpj8HBSa+/TImW+5JCeuQeRkm5NMpJWZG3hSuFU=; InstanceCI=EXPLOITATION=aGpUmPS0pDfiugatwdfPvSdUbdit_8TIPKR4yGm7; ErmesSearch_Default=%7B%22mainScenario%22%3A%22CATALOGUE%22%2C%22mainScenarioText%22%3A%22Catalogue%20g%C3%A9n%C3%A9ral%22%7D; ErmesSearch_PAE=%7B%22mainScenario%22%3A%22AE-GENERAL%22%2C%22mainScenarioText%22%3A%22Autorit%C3%A9%20environnementale%22%2C%22search%22%3A%7B%22query%22%3A%7B%22Id%22%3A%220_OFFSET_0%22%2C%22Index%22%3A1%2C%22NBResults%22%3A54%2C%22PageRange%22%3A3%2C%22SearchQuery%22%3A%7B%22CloudTerms%22%3A%5B%5D%2C%22ExceptTotalFacet%22%3Atrue%2C%22FacetFilter%22%3A%22%7B%7D%22%2C%22ForceSearch%22%3Atrue%2C%22HiddenFacetFilter%22%3A%22%7B%7D%22%2C%22InitialSearch%22%3Afalse%2C%22Page%22%3A0%2C%22PageRange%22%3A3%2C%22QueryGuid%22%3A%220ae170df-449b-444e-b166-f98892abcdf5%22%2C%22QueryString%22%3A%22(LocalClassification1_idx%3A%5C%22Avis%5C%22%20NOT%20Field950i_idx%3A%5C%22cours%20d'instruction%5C%22)%20AND%20AgenceCatalogage_idx%3ACGDD%22%2C%22ResultSize%22%3A10%2C%22ScenarioCode%22%3A%22AE-CGDD%22%2C%22ScenarioDisplayMode%22%3A%22display-standard%22%2C%22SearchContext%22%3A14%2C%22SearchGridFieldsShownOnResultsDTO%22%3A%5B%5D%2C%22SearchLabel%22%3A%22(LocalClassification1_idx%3A%5C%22Avis%5C%22%20NOT%20Field950i_idx%3A%5C%22cours%20d'instruction%5C%22)%20AND%20AgenceCatalogage_idx%3ACGDD%22%2C%22SearchTerms%22%3A%22LocalClassification1_idx%20Avis%20NOT%20Field950i_idx%20cours%20d%20instruction%20AND%20AgenceCatalogage_idx%20CGDD%22%2C%22SortField%22%3A%22DateOfInsertion_sort%22%2C%22SortOrder%22%3A0%2C%22TemplateParams%22%3A%7B%22Scenario%22%3A%22%22%2C%22Scope%22%3A%22PAE%22%2C%22Size%22%3Anull%2C%22Source%22%3A%22%22%2C%22Support%22%3A%22%22%2C%22UseCompact%22%3Afalse%7D%2C%22UseSpellChecking%22%3Anull%7D%7D%2C%22sst%22%3A2%7D%7D",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "Sec-GPC": "1",
}


def make_json_data(
    query_string, scenario_code, year_filter, target_year, result_size=50, page=0
):

    json_data = {
        "query": {
            "CloudTerms": [],
            "ExceptTotalFacet": True,
            "FacetFilter": f'{{"{year_filter}":"{target_year}"}}',
            "ForceSearch": True,
            "HiddenFacetFilter": "{}",
            "InitialSearch": False,
            "Page": page,
            "PageRange": 3,
            "QueryString": query_string,
            "ResultSize": result_size,
            "ScenarioCode": scenario_code,
            "ScenarioDisplayMode": "display-standard",
            "SearchContext": 14,
            "SearchGridFieldsShownOnResultsDTO": [],
            "SortField": "DateOfInsertion_sort",
            "SortOrder": 0,
            # "TemplateParams": {
            #     "Scenario": "",
            #     "Scope": "PAE",
            #     "Size": None,
            #     "Source": "",
            #     "Support": "",
            #     "UseCompact": False,
            # },
            "UseSpellChecking": None,
            # "Url": "https://side.developpement-durable.gouv.fr/PAE/search.aspx#/Search/%28query%3A%28CloudTerms%3A%21%28%29%2CExceptTotalFacet%3A%21t%2CFacetFilter%3A%7B%7D%2CForceSearch%3A%21t%2CHiddenFacetFilter%3A%7B%7D%2CInitialSearch%3A%21f%2CPage%3A0%2CPageRange%3A3%2CQueryGuid%3Aa3497a68-139e-418a-bd48-b5bfda651b18%2CQueryString%3A%27Field950i_idx%3A%22cours%20d%21%27instruction%22%20AND%20LocalClassification1_idx%3A%22Cas%20par%20cas%2A%22%20AND%20AgenceCatalogage_idx%3A%22CGDD%22%27%2CResultSize%3A10%2CScenarioCode%3AAE-CGDD%2CScenarioDisplayMode%3Adisplay-standard%2CSearchContext%3A14%2CSearchGridFieldsShownOnResultsDTO%3A%21%28%29%2CSearchLabel%3A%27Field950i_idx%3A%22cours%20d%21%27instruction%22%20AND%20LocalClassification1_idx%3A%22Cas%20par%20cas%2A%22%20AND%20AgenceCatalogage_idx%3A%22CGDD%22%27%2CSearchTerms%3A%27Field950i_idx%20cours%20d%20instruction%20AND%20LocalClassification1_idx%20Cas%20par%20cas%20AgenceCatalogage_idx%20CGDD%27%2CSortField%3ADateOfInsertion_sort%2CSortOrder%3A0%2CTemplateParams%3A%28Scenario%3A%27%27%2CScope%3APAE%2CSize%3A%21n%2CSource%3A%27%27%2CSupport%3A%27%27%2CUseCompact%3A%21f%29%2CUseSpellChecking%3A%21n%29%29",
        },
        "sst": 4,
    }

    return json_data


def make_region_categories(region):
    """Create the categories and query strings for regional queries"""

    categories = {
        "Saisines Cas par cas projet": f'Field950i_idx:"cours d\'instruction" AND LocalClassification1_idx:"Cas par cas*" AND AgenceCatalogage_idx:"*{region}"',
        "Décisions Cas par cas projet": f'(LocalClassification1_idx:"Cas par cas*" NOT Field950i_idx:"cours d\'instruction") AND AgenceCatalogage_idx:"*{region}"',
    }

    return categories


def make_region_config(region):
    """Create the categories and query strings for regional queries"""

    config = {
        "catalogue": "PAE",
        "scenario_code": "AE-GENERAL",
        "year_filter": "_1722",
        "categories": {
            "Saisines Cas par cas projet": f'Field950i_idx:"cours d\'instruction" AND LocalClassification1_idx:"Cas par cas*" AND AgenceCatalogage_idx:"*{region}"',
            "Décisions Cas par cas projet": f'(LocalClassification1_idx:"Cas par cas*" NOT Field950i_idx:"cours d\'instruction") AND AgenceCatalogage_idx:"*{region}"',
        },
    }

    return config


# "Auvergne-Rhône-Alpes": {
#     "catalogue": "PAE",
#     "scenario_code": "AE-GENERAL",
#     "categories": {
#         "Saisines Cas par cas projet": "Field950i_idx cours d instruction AND LocalClassification1_idx Cas par cas AgenceCatalogage_idx Auvergne Rhone Alpes",
#         "Décisions Cas par cas projet": '(LocalClassification1_idx:"Cas par cas*" NOT Field950i_idx:"cours d\'instruction") AND AgenceCatalogage_idx:"*Auvergne-Rhone-Alpes',
#     },
# },
# "Bourgogne-Franche Comté": {
#     "catalogue": "PAE",
#     "scenario_code": "AE-GENERAL",
#     "categories": {
#         "Saisines Cas par cas projet": 'Field950i_idx:"cours d\'instruction" AND LocalClassification1_idx:"Cas par cas*" AND AgenceCatalogage_idx:"*Bourgogne-Franche-Comte"',
#         "Décisions Cas par cas projet": '(LocalClassification1_idx:"Cas par cas*" NOT Field950i_idx:"cours d\'instruction") AND AgenceCatalogage_idx:"*Bourgogne-Franche-Comte"',
#     },
# },
# "Bretagne": {
#     "catalogue": "PAE",
#     "scenario_code": "AE-GENERAL",
#     "categories": {
#         "Saisines Cas par cas projet": 'Field950i_idx:"cours d\'instruction" AND LocalClassification1_idx:"Cas par cas*" AND AgenceCatalogage_idx:"*Bretagne"',
#         "Décisions Cas par cas projet": "",
#     },
# },
# "region": {
#     "catalogue": "PAE",
#     "scenario_code": "AE-GENERAL",
#     "categories": {
#         "Saisines Cas par cas projet": "",
#         "Décisions Cas par cas projet": "",
#     },
# },
# "region": {
#     "catalogue": "PAE",
#     "scenario_code": "AE-GENERAL",
#     "categories": {
#         "Saisines Cas par cas projet": "",
#         "Décisions Cas par cas projet": "",
#     },
# },
# "region": {
#     "catalogue": "PAE",
#     "scenario_code": "AE-GENERAL",
#     "categories": {
#         "Saisines Cas par cas projet": "",
#         "Décisions Cas par cas projet": "",
#     },
# },
# "region": {
#     "catalogue": "PAE",
#     "scenario_code": "AE-GENERAL",
#     "categories": {
#         "Saisines Cas par cas projet": "",
#         "Décisions Cas par cas projet": "",
#     },
# },
# "region": {
#     "catalogue": "PAE",
#     "scenario_code": "AE-GENERAL",
#     "categories": {
#         "Saisines Cas par cas projet": "",
#         "Décisions Cas par cas projet": "",
#     },
# },
# "region": {
#     "catalogue": "PAE",
#     "scenario_code": "AE-GENERAL",
#     "categories": {
#         "Saisines Cas par cas projet": "",
#         "Décisions Cas par cas projet": "",
#     },
# },


# REGIONS_NEW = {
#     "Auvergne-Rhône-Alpes": {
#         "catalogue": "PAE",
#         "scenario_code": "AE-GENERAL",
#         "categories": {
#             "Saisines Cas par cas projet": 'Field950i_idx:"cours d\'instruction" AND LocalClassification1_idx:"Cas par cas*" AND AgenceCatalogage_idx:"*Auvergne-Rhone-Alpes"',
#             "Décisions Cas par cas projet": '(LocalClassification1_idx:"Cas par cas*" NOT Field950i_idx:"cours d\'instruction") AND AgenceCatalogage_idx:"*Auvergne-Rhone-Alpes"',
#         },
#         "facet_filter": '{"_212":"Préfet de région Auvergne-Rhône-Alpes"}',
#     },
#     "Bourgogne-Franche Comté": {
#         "catalogue": "PAE",
#         "scenario_code": "AE-GENERAL",
#         "categories": {
#             "Saisines Cas par cas projet": 'Field950i_idx:"cours d\'instruction" AND LocalClassification1_idx:"Cas par cas*" AND AgenceCatalogage_idx:"*Bourgogne-Franche-Comte"',
#             "Décisions Cas par cas projet": '(LocalClassification1_idx:"Cas par cas*" NOT Field950i_idx:"cours d\'instruction") AND AgenceCatalogage_idx:"*Bourgogne-Franche-Comte"',
#         },
#         "facet_filter": '{"_212":"Préfet de région Bourgogne-Franche-Comté"}',
#     },
#     "Bretagne": {
#         "catalogue": "PAE",
#         "scenario_code": "AE-GENERAL",
#         "categories": {
#             "Saisines Cas par cas projet": "",
#             "Décisions Cas par cas projet": "",
#         },
#     },
#     "Centre-Val de Loire": {
#         "catalogue": "PAE",
#         "scenario_code": "AE-GENERAL",
#         "categories": {
#             "Saisines Cas par cas projet": "",
#             "Décisions Cas par cas projet": "",
#         },
#     },
#     "Corse": {
#         "catalogue": "PAE",
#         "scenario_code": "AE-GENERAL",
#         "categories": {
#             "Saisines Cas par cas projet": "",
#             "Décisions Cas par cas projet": "",
#         },
#     },
#     "Centre-Val de Loire": {
#         "catalogue": "PAE",
#         "scenario_code": "AE-GENERAL",
#         "categories": {
#             "Saisines Cas par cas projet": "",
#             "Décisions Cas par cas projet": "",
#         },
#     },
#     "Grand-Est": {
#         "catalogue": "PAE",
#         "scenario_code": "AE-GENERAL",
#         "categories": {
#             "Saisines Cas par cas projet": "",
#             "Décisions Cas par cas projet": "",
#         },
#     },
#     "Guadeloupe": {
#         "catalogue": "PAE",
#         "scenario_code": "AE-GENERAL",
#         "categories": {
#             "Saisines Cas par cas projet": "",
#             "Décisions Cas par cas projet": "",
#         },
#     },
#     "Guyane": {
#         "catalogue": "PAE",
#         "scenario_code": "AE-GENERAL",
#         "categories": {
#             "Saisines Cas par cas projet": "",
#             "Décisions Cas par cas projet": "",
#         },
#     },
#     "Hauts de France": {
#         "catalogue": "PAE",
#         "scenario_code": "AE-GENERAL",
#         "categories": {
#             "Saisines Cas par cas projet": "",
#             "Décisions Cas par cas projet": "",
#         },
#     },
#     "Ile de France": {
#         "catalogue": "PAE",
#         "scenario_code": "AE-GENERAL",
#         "categories": {
#             "Saisines Cas par cas projet": "",
#             "Décisions Cas par cas projet": "",
#         },
#     },
#     "Martinique": {
#         "catalogue": "PAE",
#         "scenario_code": "AE-GENERAL",
#         "categories": {
#             "Saisines Cas par cas projet": "",
#             "Décisions Cas par cas projet": "",
#         },
#     },
#     "Mayotte": {
#         "catalogue": "PAE",
#         "scenario_code": "AE-GENERAL",
#         "categories": {
#             "Saisines Cas par cas projet": "",
#             "Décisions Cas par cas projet": "",
#         },
#     },
#     "Normandie": {
#         "catalogue": "PAE",
#         "scenario_code": "AE-GENERAL",
#         "categories": {
#             "Saisines Cas par cas projet": "",
#             "Décisions Cas par cas projet": "",
#         },
#     },
#     "Nouvelle Aquitaine": {
#         "catalogue": "PAE",
#         "scenario_code": "AE-GENERAL",
#         "categories": {
#             "Saisines Cas par cas projet": "",
#             "Décisions Cas par cas projet": "",
#         },
#     },
#     "Occitanie": {
#         "catalogue": "PAE",
#         "scenario_code": "AE-GENERAL",
#         "categories": {
#             "Saisines Cas par cas projet": "",
#             "Décisions Cas par cas projet": "",
#         },
#     },
#     "Pays de la Loire": {
#         "catalogue": "PAE",
#         "scenario_code": "AE-GENERAL",
#         "categories": {
#             "Saisines Cas par cas projet": "",
#             "Décisions Cas par cas projet": "",
#         },
#     },
#     "La Réunion": {
#         "catalogue": "REUN",
#         "scenario_code": "CATAREUN",
#         "categories": {
#             "Avis sur les Projets": 'LocalClassification2_idx:"avis projet"',
#             "Avis sur les Plans et Programmes": 'LocalClassification2_idx:"Avis plans*"',
#             "Décisions cas par cas Projets": 'LocalClassification2_idx:"cas par cas projet"',
#             "Décisions cas par cas Plans et Programmes ": 'LocalClassification2_idx:"cas par cas plan*"',
#         },
#     },
#     "Saint-Pierre et Miquelon": {
#         "catalogue": "PAE",
#         "scenario_code": "AE-CGDD",
#         "categories": {
#             "Tous les Cas par cas projet": 'SubjectLocation_idx:"Saint-Pierre-et-Miquelon" OR AgenceCatalogage_idx:"*Saint-Pierre-et-Miquelon"'
#         },
#     },
# }
