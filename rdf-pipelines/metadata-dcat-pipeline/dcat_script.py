"""This pipeline is based on SimPhoNy-OSP instead of RDF-Pipeline due to whatever histroical reasons.
"""
import os
import re
from typing import Callable, Dict

from openpyxl import load_workbook
from openpyxl.worksheet.worksheet import Worksheet
from rdflib import URIRef
from simphony_osp.namespaces import dcat2, dcterms
from simphony_osp.tools import export_file

from manual_mapping import map_hardness_meta, map_tensile_meta


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
FOLDER = {
    'tensile_sheets': os.path.join(BASE_DIR, "input", "tensile_sheets"),
    'hardness_sheets': os.path.join(BASE_DIR, "input", "hardness_sheets"),
    'output': os.path.join(BASE_DIR, "output"),
}
CATALOG_API = "https://dsms.stream-dataspace.net/catalog"
DATASET_API = "https://dsms.stream-dataspace.net/dataset"
DEBUG = os.getenv("DEBUG", "").capitalize() == "True"


def main():

    annotate_DCAT(FOLDER['tensile_sheets'], re.compile("STREAM_(\w+)_IWM_TensileTest.xlsx"), map_tensile_meta)

    annotate_DCAT(FOLDER['hardness_sheets'], re.compile("STREAM_(\w+)_IWM_BrinellIndentation.xlsx") , map_hardness_meta)


def annotate_DCAT(sheets_dir:str, fname_pattern:re.Pattern, mapping:Callable[[Worksheet], Dict]):

    # tensile test data file
    for fname in os.listdir(sheets_dir):
        # derive id
        matched = fname_pattern.match(fname)
        if matched is None:
            continue
        dataset_id = matched.group(1)
        print(f"annotating dataset {dataset_id}")

        # load the meta data sheet
        wb = load_workbook(filename=os.path.join(sheets_dir, fname))
        # NOTE: hard-coded knolwedge of sheet name
        meta_ws = wb["user_variables"]

        # annotate
        annotation = mapping(meta_ws)
        annotation.update({dcterms.identifier: dataset_id})
        dataset = dcat2.Dataset(iri=URIRef(f"{DATASET_API}/{dataset_id}"))
        for pred, obj in annotation.items():
            dataset[pred] += obj
        catalog = dcat2.Catalog(iri=URIRef(CATALOG_API))
        catalog.connect(dataset, rel=dcat2.dataset)

        # generate an RDF file
        export_file(
            catalog.session,
            file=os.path.join(FOLDER['output'], f"{dataset_id}.ttl"),
            format="text/turtle",
            all_triples=True
        )

        # test with one datasheet
        if DEBUG:
            break


if __name__ == "__main__":
    main()
