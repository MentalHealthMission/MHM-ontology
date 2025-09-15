# Raw demo data

These CSVs represent the “pre-ontology” slice used in the presentation demo.

- `steps.csv`: daily total steps
  - Columns: `date` (YYYY-MM-DD), `steps` (unitless count)
- `sleep.csv`: daily sleep minutes
  - Columns: `date` (YYYY-MM-DD), `sleep_minutes` (QUDT unit: Minute)
 - `location.csv`: daily distance from home (km)
  - Columns: `date` (YYYY-MM-DD), `km_from_home` (QUDT unit: KiloM)

Provenance linkage in `../demo.ttl`:

- Raw files are `prov:Entity` with `dcterms:format` and `prov:atLocation`.
- `odim:A_RawExport` (`odim:DataTransferEvent`) `prov:generated` the CSVs.
- `odim:A_Import` (`odim:DataTransferEvent`) `prov:used` the CSVs and `odim:wasGeneratedBy` each observation.
- Travel detection uses `DeviceLocationEstimate` observations (derived from `location.csv`) to compute a `odim:EventWindow` for travel.

The demo avoids CSVW/RML for clarity; it shows provenance and units without extra machinery.
