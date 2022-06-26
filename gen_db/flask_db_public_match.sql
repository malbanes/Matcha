create table match
(
    id        serial
        constraint match_pk
            primary key,
    user_id   integer not null,
    match_id  integer not null,
    position  integer          default 0,
    is_filter boolean          default false,
    score     double precision default 0
);

alter table match
    owner to agu;

grant usage on sequence match_id_seq to sammy;

create unique index match_id_uindex
    on match (id);

