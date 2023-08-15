# from https://github.com/lubianat/obo_to_mixnmatch/blob/main/src/get_all_entities.sh

mkdir data 

wget -nc -O data/$1.owl  https://data.bioontology.org/ontologies/EFO/submissions/253/download?apikey=8b5b7825-538d-40e0-9e9e-5ab9274a9aeb


robot export --input data/$1.owl \
  --header "ID|LABEL|IAO_0000115|hasDbXref|subClassOf [ID]|hasExactSynonym" \
  --export data/$1.csv

grep -v "obsolete" data/$1.csv | grep -i ^http://www.ebi.ac.uk/efo/EFO_  > data/$1_clean_temp.csv

sed -i '1s/^/id,name,description,xrefs,parents,aliases\n /' data/$1_clean_temp.csv

awk -F, -v OFS=, '{sub("http://www.ebi.ac.uk/efo/EFO_", "", $1)} 1' data/efo_clean_temp.csv > data/efo_clean.csv
