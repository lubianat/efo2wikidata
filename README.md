

# Step by step connection of an ontology to Wikidata


1 - Create a property on Wikidata to host the identifier: https://www.wikidata.org/wiki/Property:P11956

2 - Verify the license of the ontology to see what can be migrated. 

This is a gray area. If the ontology is CC0, everything can be connected. 

If it is CC-BY or under some other license, reuse is unclear. 

Some ontologists might disagree wheter the subclass hierarchy is protected by IP law, and it might be disputed. 

Labels and identifiers should, however, not be liable to claims of IP. IDs are non-creative alpha-numeric products and labels are, if done correctly, a pragmatic capture of terms widely used by the community. 

The cross-references in an ontology are also in a gray area.

The general rule is to proceed with caution and common sense, trying to respect the desires of all stakeholders as well as possible. 


3 - Create a Mix'n'Match catalog for manual curation of entries.

Step by step: 

- Run the bash with ROBOT code to generate a Mix'n'Match ready spreadsheet. 

- Go to https://mix-n-match.toolforge.org/#/import and add the catalog


4 - Select a set of high-quality cross-references in the ontology that are already mapped to Wikidata. 

Automatically map terms that have this high quality 1:1 correspondente. The mappings/cross-refeences may be modelled in different ways in the ontology. 


5 - If the ontology is CC0 or there is an authorization for importing the subclass structure, proceed with filling the gaps using the wdcuration workflow.