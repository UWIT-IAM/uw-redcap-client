-- Verify seattleflu/schema:roles/enroller/comment on pg

begin;

set local role id3c;

do $$ begin
    if pg_catalog.shobj_description('enroller'::regrole, 'pg_authid') is null then
        raise 'role "enroller" has no comment';
    end if;
end $$;

rollback;
