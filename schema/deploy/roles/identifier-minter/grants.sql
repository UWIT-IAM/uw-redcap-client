-- Deploy seattleflu/schema:roles/identifier-minter/grants to pg
-- requires: warehouse/identifier
-- requires: roles/identifier-minter/create

begin;

set local role id3c;

-- This change is designed to be sqitch rework-able to make it easier to update
-- the grants for this role.

grant connect on database :"DBNAME" to "identifier-minter";

grant usage
   on schema warehouse
   to "identifier-minter";

grant select
   on warehouse.identifier_set
   to "identifier-minter";

grant select, insert
   on warehouse.identifier
   to "identifier-minter";

commit;
