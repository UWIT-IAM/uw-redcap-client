-- Verify seattleflu/schema:warehouse/site on pg

begin;

set local role id3c;

select pg_catalog.has_table_privilege('warehouse.site', 'select');

rollback;
