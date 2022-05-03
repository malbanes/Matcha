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
    owner to agu;

create unique index accountcontrol_id_uindex
    on accountcontrol (id);

