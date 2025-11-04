# Dev guide

This document summarizes the development process for this repository, which works as follows:

1.  It calls `pg_dump` to create a `.sql` file using the `ermrest` user.
2.  The generated `.sql` file is manually modified to remove unnecessary information (we only care about table definitions, keys, and foreign keys). The result is saved as `dump.sql`.
3.  It uses `@dbml/core` to convert the `dump.sql` to `output.dbml`.

Because of the first step, this script must be called on the same machine where the database is running. We might be able to improve this step, but regardless, we should be able to create a similar `dump.sql` by iterating over the schemas and tables using `deriva-py` without having to connect directly to the database.


The following is an example of what we need from the `.sql` file:

```sql
-- table definitions
CREATE TABLE bio.acquisition (
   "RID" public.ermrest_rid DEFAULT _ermrest.urlb32_encode(nextval('_ermrest.rid_seq'::regclass)) NOT NULL,
   "RCT" public.ermrest_rct DEFAULT now() NOT NULL,
   "RMT" public.ermrest_rmt DEFAULT now() NOT NULL,
   "RCB" public.ermrest_rcb DEFAULT _ermrest.current_client(),
   "RMB" public.ermrest_rmb DEFAULT _ermrest.current_client(),
   experiment text NOT NULL,
   id text NOT NULL,
   timepoint text,
   number_of_samples integer,
   multiplexing boolean DEFAULT false,
   delivered_at timestamp with time zone,
   instrument text,
   instrument_protocol text,
   instrument_settings jsonb,
   data_processing_protocol text,
   data_processing_config jsonb,
   qc_pre_acquisition jsonb,
   qc_post_acquisition jsonb,
   run_id text,
   notes public.markdown,
   hpc_path text,
   validated_sdrf_samplesheet boolean,
   acquisition_status text DEFAULT 'Run delivered'::text NOT NULL
);
CREATE TABLE bio.acquisition_sample (
   "RID" public.ermrest_rid DEFAULT _ermrest.urlb32_encode(nextval('_ermrest.rid_seq'::regclass)) NOT NULL,
   "RCT" public.ermrest_rct DEFAULT now() NOT NULL,
   "RMT" public.ermrest_rmt DEFAULT now() NOT NULL,
   "RCB" public.ermrest_rcb DEFAULT _ermrest.current_client(),
   "RMB" public.ermrest_rmb DEFAULT _ermrest.current_client(),
   acquisition text NOT NULL,
   sample text NOT NULL
);

-- key definitions
ALTER TABLE ONLY bio.acquisition
   ADD CONSTRAINT "acquisition_RID_key" UNIQUE ("RID");
ALTER TABLE ONLY bio.acquisition
   ADD CONSTRAINT acquisition_id_key UNIQUE (id);

-- foreign key definitions
ALTER TABLE ONLY bio.acquisition
   ADD CONSTRAINT acquisition_acquisition_status_fkey FOREIGN KEY (acquisition_status) REFERENCES vocab.acquisition_status(name) ON UPDATE CASCADE ON DELETE SET NULL;
ALTER TABLE ONLY bio.acquisition
   ADD CONSTRAINT acquisition_data_processing_protocol_fkey FOREIGN KEY (data_processing_protocol) REFERENCES bio.protocol("RID") ON UPDATE CASCADE ON DELETE SET NULL;
```
