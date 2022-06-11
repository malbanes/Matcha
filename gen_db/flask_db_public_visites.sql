create table visites
(
    id          serial
        primary key,
    sender_id   integer default 0,
    receiver_id integer default 0 not null,
    date_added  date    default CURRENT_TIMESTAMP
);

alter table visites
    owner to agu;

create unique index visites_id_uindex
    on visites (id);

grant delete, insert, references, select, trigger, truncate, update on visites to sammy;

INSERT INTO public.visites (id, sender_id, receiver_id, date_added) VALUES (1, 1342, 1122, '2022-06-06');
INSERT INTO public.visites (id, sender_id, receiver_id, date_added) VALUES (2, 1342, 1348, '2022-06-06');
INSERT INTO public.visites (id, sender_id, receiver_id, date_added) VALUES (3, 1342, 527, '2022-06-06');
INSERT INTO public.visites (id, sender_id, receiver_id, date_added) VALUES (4, 1342, 142, '2022-06-06');
INSERT INTO public.visites (id, sender_id, receiver_id, date_added) VALUES (5, 1342, 375, '2022-06-06');
INSERT INTO public.visites (id, sender_id, receiver_id, date_added) VALUES (6, 1342, 432, '2022-06-06');
