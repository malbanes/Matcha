create table images
(
    id         serial
        primary key,
    title      varchar(255) not null,
    path       varchar(255) not null,
    profil_id  integer      not null,
    date_added date default CURRENT_TIMESTAMP
);

alter table images
    owner to sammy;

INSERT INTO public.images (id, title, path, profil_id, date_added) VALUES (1, 'Sammy Image', 'https://www.arthurguerin.com/assets/www.png', 1, '2022-03-28');
