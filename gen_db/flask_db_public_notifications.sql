create table notifications
(
    id          serial
        primary key,
    sender_id   integer,
    receiver_id integer,
    notif_type  integer,
    content     integer,
    is_read     boolean default false,
    date_added  double precision
);

alter table notifications
    owner to agu;

create unique index notifications_id_uindex
    on notifications (id);

grant delete, insert, references, select, trigger, truncate, update on notifications to sammy;

