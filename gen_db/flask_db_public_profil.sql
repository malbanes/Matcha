create table profil
(
    id             serial
        constraint profil_pk
            primary key,
    user_id        integer               not null
        constraint profil_users_id_fk
            references users,
    genre_id       integer default 0     not null,
    orientation_id integer default 0     not null,
    location_id    integer default 0     not null
        constraint profil_location_id_fk
            references location,
    age            date,
    bio            text,
    image_profil   integer default 0     not null,
    score          integer,
    is_online      boolean default false not null,
    last_log       date
);

alter table profil
    owner to agu;

grant select, usage on sequence profil_id_seq to sammy;

create unique index profil_id_uindex
    on profil (id);

create unique index profil_user_id_uindex
    on profil (user_id);

grant delete, insert, references, select, trigger, truncate, update on profil to sammy;

INSERT INTO public.profil (id, user_id, genre_id, orientation_id, location_id, age, bio, image_profil, score, is_online, last_log) VALUES (1, 3, 1, 2, 0, '2007-04-01', '"hey . hey hey"', 0, null, false, '2022-04-17');
INSERT INTO public.profil (id, user_id, genre_id, orientation_id, location_id, age, bio, image_profil, score, is_online, last_log) VALUES (3, 27, 0, 0, 3, null, null, 0, null, false, '2022-04-19');
