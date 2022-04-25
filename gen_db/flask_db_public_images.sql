create table images
(
    id         serial
        primary key,
    title      varchar(255) not null,
    path       varchar(255) not null,
    profil_id  integer      not null
        constraint images_users_id_fk
            references users,
    date_added date default CURRENT_TIMESTAMP
);

alter table images
    owner to sammy;

grant delete, insert, references, select, trigger, truncate, update on images to agu;

INSERT INTO public.images (id, title, path, profil_id, date_added) VALUES (1, 'Sammy Image', 'https://www.arthurguerin.com/assets/www.png', 1, '2022-03-28');
INSERT INTO public.images (id, title, path, profil_id, date_added) VALUES (3, '9fc8139f0e9b241005a2bc7ff5e7ee7f502d4c093a2500205e0ce61ea57d4eea/Logo_noir_fond_transparent.png', '9fc8139f0e9b241005a2bc7ff5e7ee7f502d4c093a2500205e0ce61ea57d4eea/Logo_noir_fond_transparent.png', 27, '2022-04-24');
INSERT INTO public.images (id, title, path, profil_id, date_added) VALUES (4, '9fc8139f0e9b241005a2bc7ff5e7ee7f502d4c093a2500205e0ce61ea57d4eea/Voodoo-02.jpg', '9fc8139f0e9b241005a2bc7ff5e7ee7f502d4c093a2500205e0ce61ea57d4eea/Voodoo-02.jpg', 27, '2022-04-24');
INSERT INTO public.images (id, title, path, profil_id, date_added) VALUES (6, '9fc8139f0e9b241005a2bc7ff5e7ee7f502d4c093a2500205e0ce61ea57d4eea/Voodoo-02.jpg', '9fc8139f0e9b241005a2bc7ff5e7ee7f502d4c093a2500205e0ce61ea57d4eea/Voodoo-02.jpg', 27, '2022-04-24');
INSERT INTO public.images (id, title, path, profil_id, date_added) VALUES (8, '87aa3ddef63abf5f088752b8d40d5fff3aa47e5176fde1bc7e0eada3d787c424/Voodoo-02.jpg', '87aa3ddef63abf5f088752b8d40d5fff3aa47e5176fde1bc7e0eada3d787c424/Voodoo-02.jpg', 28, '2022-04-25');
