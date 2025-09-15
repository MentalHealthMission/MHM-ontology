# Raw demo data

These CSVs represent the “pre-ontology” slice used in the presentation demo.

- `steps.csv`: daily total steps
  - Columns: `date` (YYYY-MM-DD), `steps` (unitless count)
- `sleep.csv`: daily sleep minutes
  - Columns: `date` (YYYY-MM-DD), `sleep_minutes` (QUDT unit: Minute)

Provenance linkage in `../demo.ttl`:

- Raw files are `prov:Entity` with `dcterms:format` and `prov:atLocation`.
- `odim:A_RawExport` (`odim:DataTransferEvent`) `prov:generated` the CSVs.
- `odim:A_Import` (`odim:DataTransferEvent`) `prov:used` the CSVs and `odim:wasGeneratedBy` each observation.

The demo avoids CSVW/RML for clarity; it shows provenance and units without extra machinery.
