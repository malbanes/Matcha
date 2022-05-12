create table messages
(
    id             serial
            primary key,
    sender_id       integer,
    receiver_id integer,
    msg text,
    date_added float
);

alter table likes
    owner to agu;

create unique index messages_id_uindex
    on messages (id);

grant delete, insert, references, select, trigger, truncate, update on likes to sammy;