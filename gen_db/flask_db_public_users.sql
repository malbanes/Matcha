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

INSERT INTO public.users (id, username, password, date_added, first_name, last_name, email, confirmed) VALUES (1, 'test', '$2a$06$nPJNCAAV1YHn9D68XsMlNeE8jNfikyI3AuuGuqvWg2e9VPlHaWI2W', '2022-03-28', 'Sammy', 'Test', 'test@test.com', true);
INSERT INTO public.users (id, username, password, date_added, first_name, last_name, email, confirmed) VALUES (3, 'Yop', '$2a$06$iUptzf5jgyOQK9SGkC8xhO0RGpzOnNUDR/I5DaGKYprh8eoDDSFiq', '2022-03-29', 'Hello', 'Yop', 'hello@test.com', true);
INSERT INTO public.users (id, username, password, date_added, first_name, last_name, email, confirmed) VALUES (9, 'hey@hey.com', '$2a$06$wFl7dMsDAdmuq7/8UxRNa.Sa.816yFDjm/uz7W2EPeizo9Qd0a1ku', '2022-04-04', 'hey@hey.com', 'hey@hey.com', 'hey@hey.com', false);
INSERT INTO public.users (id, username, password, date_added, first_name, last_name, email, confirmed) VALUES (10, 'hey@test.com', '$2a$06$EAk3AoLZfm0LZVo7wQIL.ODPNU.O4t1xZl1a5BIpSRpHa/62xxCdO', '2022-04-04', 'hey@test.com', 'hey@test.com', 'hey@test.com', true);
INSERT INTO public.users (id, username, password, date_added, first_name, last_name, email, confirmed) VALUES (27, 'agu42', '$2a$06$O/BM0qiePMmT9qNQqtdWfOXmrD2dDXTIzC28IgRCmEyBv33OXHut2', '2022-04-19', 'arthur', 'g', 'arguerin@student.42.fr', true);
