import random
from pathlib import Path
import datetime
import pandas as pd
from wdcuration import (
    query_wikidata,
    render_qs_url,
    NewItemConfig,
    WikidataDictAndKey,
    check_and_save_dict,
)

import yaml

def load_config(filename):
    with open(filename, 'r') as f:
        return yaml.safe_load(f)
    
class WikidataProcessor:

    def __init__(self, reference_on_wd_pid, pid_to_add, data_dir, reference_prefix, heuristic, wikidata_id_style):
        self.reference_on_wd_pid = reference_on_wd_pid
        self.pid_to_add = pid_to_add
        self.data_dir = data_dir
        self.reference_prefix = reference_prefix
        self.heuristic = heuristic
        self.wikidata_id_style = wikidata_id_style

        self.reference2wikidata = self._query_wikidata_for_pid(reference_on_wd_pid)
        self.pid_to_add2wikidata = self._query_wikidata_for_pid(pid_to_add)
        self.reference2new_id_in_wikidata = self._get_reference2new_id_in_wikidata()

    def _query_wikidata_for_pid(self, pid):
        query = f'SELECT DISTINCT ?pid_value (REPLACE(STR(?item), ".*Q", "Q") AS ?qid) WHERE {{ ?item wdt:{pid} ?pid_value. }}'
        results = query_wikidata(query)
        return {a["pid_value"]: a["qid"] for a in results}

    def _get_reference2new_id_in_wikidata(self):
        query = f'SELECT DISTINCT ?reference_id (REPLACE(STR(?item), ".*Q", "Q") AS ?qid) WHERE {{ ?item wdt:{self.reference_on_wd_pid} ?reference_id. ?item wdt:{self.pid_to_add} ?new_id. }}'
        results = query_wikidata(query)
        return {a["reference_id"]: a["qid"] for a in results}

    def _format_id_for_wikidata(self, id):
        if self.wikidata_id_style == "underline":
            return id.replace(":", "_")
        elif self.wikidata_id_style == "drop_prefix":
            return id.split(":")[-1]
        else:
            return id

    def _get_reference2new_id(self, df, ids_to_add):
        reference2new_id = {}
        for id_to_add in ids_to_add:
            row = df[df["id"] == id_to_add]
            xrefs = row["xrefs"].item()
            if isinstance(xrefs, str) and self.reference_prefix in xrefs:
                for xref in xrefs.split("|"):
                    if f"{self.reference_prefix}:" in xref:
                        formatted_xref = self._format_id_for_wikidata(xref)
                        reference2new_id[formatted_xref] = row["id"].item()
        return reference2new_id

    def _generate_qs_triple(self, qid, new_id):
        return f'{qid}|{self.pid_to_add}|"{new_id}"|S887|{self.heuristic}\n'

    def process_data(self, filename="efo_clean.csv"):
        df = pd.read_csv(
            self.data_dir.joinpath(filename),
            dtype={"id": object},
            on_bad_lines="skip",
        )

        current_wikidata_coverage = set(self.pid_to_add2wikidata.keys())
        ids_to_add = sorted(set(df["id"]) - current_wikidata_coverage)
        reference2new_id = self._get_reference2new_id(df, ids_to_add)
        matches_not_in_wikidata = set(reference2new_id) - set(self.reference2new_id_in_wikidata)

        qs = ""
        for reference_term in matches_not_in_wikidata:
            try:
                qid = self.reference2wikidata[reference_term]
                new_id = reference2new_id[reference_term]
                qs += self._generate_qs_triple(qid, new_id)
            except KeyError:
                pass

        return qs

    def save_to_file(self, qs, results_dir):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        filename = f"quickstatements_{self.reference_on_wd_pid}_{self.pid_to_add}_{timestamp}.txt"
        with open(results_dir.joinpath(filename), "w") as f:
            f.write(qs)
        print(render_qs_url(qs))


target_params = ["NCIt"]
skip_prefixes = ["OMIM"] # multimappings
def main():
    HERE = Path(__file__).parent.resolve()
    config = load_config(HERE.joinpath("xref_config.yaml"))

    DATA_DIR = HERE.parent.joinpath("data").resolve()
    RESULTS_DIR = HERE.parent.joinpath("results").resolve()
    pid_to_add = "P11956"

    for params in config['processing_parameters']:
        if params["reference_prefix"] in target_params and params["reference_prefix"] not in skip_prefixes:
          reference_on_wd_pid = params['pid']
          reference_prefix = params['reference_prefix']
          heuristic = params['heuristic']
          wikidata_id_style = params['wikidata_id_style']

          processor = WikidataProcessor(reference_on_wd_pid, pid_to_add, DATA_DIR, reference_prefix, heuristic, wikidata_id_style)
          qs = processor.process_data()
          processor.save_to_file(qs, RESULTS_DIR)


if __name__ == "__main__":
    main()
