create table location
(
    id         serial
        constraint location_pk
            primary key,
    latitude   double precision default 0.00,
    longitude  double precision default 0.00,
    date_modif date,
    city       char(255)
);

alter table location
    owner to agu;

grant select, usage on sequence location_id_seq to sammy;

create unique index location_id_uindex
    on location (id);

grant delete, insert, references, select, trigger, truncate, update on location to sammy;

INSERT INTO public.location (id, latitude, longitude, date_modif, city) VALUES (0, 0, 0, null, null);
INSERT INTO public.location (id, latitude, longitude, date_modif, city) VALUES (1, 48.83637, 2.30648, '2022-04-19', 'Paris - 75015                                                                                                                                                                                                                                                  ');
INSERT INTO public.location (id, latitude, longitude, date_modif, city) VALUES (2, 48.83637, 2.30648, '2022-04-19', 'Paris - 75015                                                                                                                                                                                                                                                  ');
INSERT INTO public.location (id, latitude, longitude, date_modif, city) VALUES (3, 48.83637, 2.30648, '2022-04-19', 'Paris - 75015                                                                                                                                                                                                                                                  ');
