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
    owner to sammy;

grant select, usage on sequence notifications_id_seq to sammy;

create unique index notifications_id_uindex
    on notifications (id);

grant delete, insert, references, select, trigger, truncate, update on notifications to sammy;

INSERT INTO public.notifications (id, sender_id, receiver_id, notif_type, content, is_read, date_added) VALUES (1, 34, 896, 1, 1, false, 1655678480.442186);
INSERT INTO public.notifications (id, sender_id, receiver_id, notif_type, content, is_read, date_added) VALUES (2, 34, 226, 1, 1, false, 1655679069.57356);
INSERT INTO public.notifications (id, sender_id, receiver_id, notif_type, content, is_read, date_added) VALUES (3, 34, 1325, 1, 1, false, 1655679116.323657);
INSERT INTO public.notifications (id, sender_id, receiver_id, notif_type, content, is_read, date_added) VALUES (4, 34, 89, 1, 1, false, 1656270847.19475);