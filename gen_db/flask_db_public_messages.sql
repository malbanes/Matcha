create table messages
(
    id          serial
        primary key,
    sender_id   integer,
    receiver_id integer,
    msg         text,
    date_added  double precision
);

alter table messages
    owner to sammy;

create unique index messages_id_uindex
    on messages (id);

grant delete, insert, references, select, trigger, truncate, update on messages to sammy;