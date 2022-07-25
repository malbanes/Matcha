create table visites
(
    id          serial
        primary key,
    sender_id   integer default 0,
    receiver_id integer default 0 not null,
    date_added  date    default CURRENT_TIMESTAMP
);

alter table visites
    owner to sammy;

grant select, usage on sequence visites_id_seq to sammy;

create unique index visites_id_uindex
    on visites (id);

grant delete, insert, references, select, trigger, truncate, update on visites to sammy;

INSERT INTO public.visites (id, sender_id, receiver_id, date_added) VALUES (1, 1342, 1122, '2022-06-06');
INSERT INTO public.visites (id, sender_id, receiver_id, date_added) VALUES (2, 1342, 1348, '2022-06-06');
INSERT INTO public.visites (id, sender_id, receiver_id, date_added) VALUES (3, 1342, 527, '2022-06-06');
INSERT INTO public.visites (id, sender_id, receiver_id, date_added) VALUES (4, 1342, 142, '2022-06-06');
INSERT INTO public.visites (id, sender_id, receiver_id, date_added) VALUES (5, 1342, 375, '2022-06-06');
INSERT INTO public.visites (id, sender_id, receiver_id, date_added) VALUES (6, 1342, 432, '2022-06-06');
INSERT INTO public.visites (id, sender_id, receiver_id, date_added) VALUES (7, 34, 3, '2022-06-19');
INSERT INTO public.visites (id, sender_id, receiver_id, date_added) VALUES (8, 34, 1348, '2022-06-19');
INSERT INTO public.visites (id, sender_id, receiver_id, date_added) VALUES (9, 34, 966, '2022-06-20');
INSERT INTO public.visites (id, sender_id, receiver_id, date_added) VALUES (10, 34, 896, '2022-06-20');
INSERT INTO public.visites (id, sender_id, receiver_id, date_added) VALUES (11, 34, 226, '2022-06-20');
INSERT INTO public.visites (id, sender_id, receiver_id, date_added) VALUES (12, 34, 1325, '2022-06-20');
INSERT INTO public.visites (id, sender_id, receiver_id, date_added) VALUES (13, 34, 89, '2022-06-26');