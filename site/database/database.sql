DROP TABLE IF EXISTS langue CASCADE;
CREATE TABLE langue(
    id serial primary key,
    nom text
);


DROP TABLE IF EXISTS data CASCADE;
CREATE TABLE data(
    id serial primary key,
    langue int,
    sens text, -- text aléatoire (commun a une même traduction)
    mots text
);

