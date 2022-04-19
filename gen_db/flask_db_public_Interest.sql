create table "Interest"
(
    id      serial
        constraint interest_pk
            primary key,
    hashtag char(255) not null
);

alter table "Interest"
    owner to agu;

grant select, usage on sequence "Interest_id_seq" to sammy;

create unique index interest_id_uindex
    on "Interest" (id);

grant delete, insert, references, select, trigger, truncate, update on "Interest" to sammy;

INSERT INTO public."Interest" (id, hashtag) VALUES (1, 'reading                                                                                                                                                                                                                                                        ');
INSERT INTO public."Interest" (id, hashtag) VALUES (2, 'writing                                                                                                                                                                                                                                                        ');
INSERT INTO public."Interest" (id, hashtag) VALUES (3, 'painting                                                                                                                                                                                                                                                       ');
INSERT INTO public."Interest" (id, hashtag) VALUES (4, 'swimming                                                                                                                                                                                                                                                       ');
INSERT INTO public."Interest" (id, hashtag) VALUES (5, 'singing                                                                                                                                                                                                                                                        ');
INSERT INTO public."Interest" (id, hashtag) VALUES (6, 'dancing                                                                                                                                                                                                                                                        ');
INSERT INTO public."Interest" (id, hashtag) VALUES (7, 'guitar                                                                                                                                                                                                                                                         ');
INSERT INTO public."Interest" (id, hashtag) VALUES (8, 'piano                                                                                                                                                                                                                                                          ');
INSERT INTO public."Interest" (id, hashtag) VALUES (9, 'violin                                                                                                                                                                                                                                                         ');
INSERT INTO public."Interest" (id, hashtag) VALUES (10, 'cycling                                                                                                                                                                                                                                                        ');
INSERT INTO public."Interest" (id, hashtag) VALUES (11, 'hiking                                                                                                                                                                                                                                                         ');
INSERT INTO public."Interest" (id, hashtag) VALUES (12, 'running                                                                                                                                                                                                                                                        ');
INSERT INTO public."Interest" (id, hashtag) VALUES (13, 'soccer                                                                                                                                                                                                                                                         ');
INSERT INTO public."Interest" (id, hashtag) VALUES (14, 'computer                                                                                                                                                                                                                                                       ');
INSERT INTO public."Interest" (id, hashtag) VALUES (15, 'blogging                                                                                                                                                                                                                                                       ');
INSERT INTO public."Interest" (id, hashtag) VALUES (16, 'drawing                                                                                                                                                                                                                                                        ');
