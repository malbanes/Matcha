create table search
(
    id             serial
            primary key,
    user_id       integer default 0 not null,
    list_id       integer default 0 not null,
);

alter table search
    owner to agu;

create unique index search_id_uindex
    on search (id);

grant delete, insert, references, select, trigger, truncate, update on search to sammy;