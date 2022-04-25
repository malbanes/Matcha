create table "ProfilInterest"
(
    id          serial
        constraint profilinterest_pk
            primary key,
    user_id     integer not null
        constraint profilinterest_profil_user_id_fk
            references profil (user_id),
    interest_id integer not null
        constraint profilinterest_interest_id_fk
            references "Interest"
);

alter table "ProfilInterest"
    owner to agu;

grant select, usage on sequence "ProfilInterest_id_seq" to sammy;

create unique index profilinterest_id_uindex
    on "ProfilInterest" (id);

grant delete, insert, references, select, trigger, truncate, update on "ProfilInterest" to sammy;

INSERT INTO public."ProfilInterest" (id, user_id, interest_id) VALUES (2, 28, 10);
INSERT INTO public."ProfilInterest" (id, user_id, interest_id) VALUES (3, 28, 4);
