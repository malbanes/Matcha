create table messages
(
    id             serial
            primary key,
    sender_id       integer,
    receiver_id integer,
    msg text,
    date_added float
);

alter table messages
    owner to agu;

create unique index messages_id_uindex
    on messages (id);

grant delete, insert, references, select, trigger, truncate, update on messages to sammy;