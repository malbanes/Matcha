create table likes
(
    id          serial
        primary key,
    sender_id   integer default 0,
    receiver_id integer default 0 not null,
    date_added  date    default CURRENT_TIMESTAMP
);

alter table likes
    owner to sammy;

grant select, usage on sequence likes_id_seq to sammy;

create unique index likes_id_uindex
    on likes (id);

grant delete, insert, references, select, trigger, truncate, update on likes to sammy;