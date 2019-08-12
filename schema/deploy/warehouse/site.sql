-- Deploy seattleflu/schema:warehouse/site to pg
-- requires: warehouse/schema

begin;

set local role id3c;

set local search_path to warehouse;

create table site (
    site_id integer primary key generated by default as identity,
    identifier text not null unique,
    details jsonb,

    constraint site_identifier_is_unique_case_insensitively
        exclude (lower(identifier) with =)
);

create index site_details_idx on site using gin (details jsonb_path_ops);

comment on table site is 'A real-world or virtual/logical location where individuals are encountered';
comment on column site.site_id is 'Internal id of this site';
comment on column site.identifier is 'External identifier for this site; case-preserving but must be unique case-insensitively';
comment on column site.details is 'Additional information about this site which does not have a place in the relational schema';

commit;
