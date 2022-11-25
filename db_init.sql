INSERT INTO iis.user (id, username, email_address, login, password_hash, user_type)
VALUES (1, "admin", "admin@gmail.com", "admin", "$2b$12$x6L48qxP1fWpE5QQ18VFke5eoBDnuh2OFthyhZPG688whLnWqJdfO", "administrator");

-- INSERT INTO iis.course (name, description, course_type, price, news, confirmed, users_limit, course_guarantor_id)
-- VALUES ("kurz1", "Popis kurzu 1", 'type1', 2000, "Aktuality kurzu 1", false, 50, 1);
--
-- INSERT INTO iis.course (name, description, course_type, price, news, confirmed, users_limit, course_guarantor_id)
-- VALUES ("kurz2", "Popis kurzu 2", 'type2', 2000, "Aktuality kurzu 2", false, 200, 1);

INSERT INTO iis.course (name, course_type, language, credit_count, points, grade, course_guarantor_id)
VALUES ("Fyzika", 'compulsory', 'czech',  5, 27, "F", 3);

INSERT INTO iis.users_have_registered_courses (user_id, course_name, registration_confirmed) 
VALUES (1, 'kurz2', False);