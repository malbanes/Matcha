create table visites
(
    id             serial
            primary key,
    sender_id       integer default 0,
    receiver_id integer default 0 not null,
    date_added date default CURRENT_TIMESTAMP
);

alter table visites
    owner to agu;

create unique index visites_id_uindex
    on visites (id);

grant delete, insert, references, select, trigger, truncate, update on visites to sammy;