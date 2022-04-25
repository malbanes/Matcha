create table users
(
    id         serial
        primary key,
    username   varchar(255)          not null,
    password   varchar(255)          not null,
    date_added date    default CURRENT_TIMESTAMP,
    first_name varchar(255),
    last_name  varchar(255),
    email      varchar(255),
    confirmed  boolean default false not null
);

alter table users
    owner to sammy;

create unique index users_username_uindex
    on users (username);

create unique index users_email_uindex
    on users (email);

grant delete, insert, references, select, trigger, truncate, update on users to agu;

INSERT INTO public.users (id, username, password, date_added, first_name, last_name, email, confirmed) VALUES (1, 'test', '$2a$06$nPJNCAAV1YHn9D68XsMlNeE8jNfikyI3AuuGuqvWg2e9VPlHaWI2W', '2022-03-28', 'Sammy', 'Test', 'test@test.com', true);
INSERT INTO public.users (id, username, password, date_added, first_name, last_name, email, confirmed) VALUES (3, 'Yop', '$2a$06$iUptzf5jgyOQK9SGkC8xhO0RGpzOnNUDR/I5DaGKYprh8eoDDSFiq', '2022-03-29', 'Hello', 'Yop', 'hello@test.com', true);
INSERT INTO public.users (id, username, password, date_added, first_name, last_name, email, confirmed) VALUES (9, 'hey@hey.com', '$2a$06$wFl7dMsDAdmuq7/8UxRNa.Sa.816yFDjm/uz7W2EPeizo9Qd0a1ku', '2022-04-04', 'hey@hey.com', 'hey@hey.com', 'hey@hey.com', false);
INSERT INTO public.users (id, username, password, date_added, first_name, last_name, email, confirmed) VALUES (10, 'hey@test.com', '$2a$06$EAk3AoLZfm0LZVo7wQIL.ODPNU.O4t1xZl1a5BIpSRpHa/62xxCdO', '2022-04-04', 'hey@test.com', 'hey@test.com', 'hey@test.com', true);
INSERT INTO public.users (id, username, password, date_added, first_name, last_name, email, confirmed) VALUES (27, 'aguagu', '$2a$06$iIFxGfI28HGUIfNd.1yLnusCO8XBCr83gVv0G75oV7OpUN8E2Tw2K', '2022-04-19', 'n', 'bbbbb', 'a.guerin@me.com', true);
INSERT INTO public.users (id, username, password, date_added, first_name, last_name, email, confirmed) VALUES (28, 'arthurg2', '$2a$06$/Ly18UzWcZP0Aq0x3xQc1e3ilIZ.898gKsYf6/.rKBNrnrRjML87y', '2022-04-25', 'Arthur', 'YOYOYO', 'a.guerin@icloud.com', true);
