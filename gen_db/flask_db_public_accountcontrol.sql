create table accountcontrol
(
    id           serial
        constraint accountcontrol_pk
            primary key,
    blocked      boolean,
    fake         boolean,
    from_user_id integer
        constraint accountcontrol_users_id_fk
            references users,
    to_user_id   integer
        constraint accountcontrol_users_id_fk_2
            references users
);

alter table accountcontrol
    owner to sammy;

grant select, update, usage on sequence accountcontrol_id_seq to sammy;

create unique index accountcontrol_id_uindex
    on accountcontrol (id);

grant delete, insert, references, select, trigger, truncate, update on accountcontrol to sammy;

INSERT INTO public.accountcontrol (id, blocked, fake, from_user_id, to_user_id) VALUES (5, true, false, 1342, 40);
INSERT INTO public.accountcontrol (id, blocked, fake, from_user_id, to_user_id) VALUES (6, true, false, 1342, 30);
INSERT INTO public.accountcontrol (id, blocked, fake, from_user_id, to_user_id) VALUES (7, true, false, 34, 3);
INSERT INTO public.accountcontrol (id, blocked, fake, from_user_id, to_user_id) VALUES (2, false, true, 1342, 34);