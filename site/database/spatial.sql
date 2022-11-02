-- à faire utilisateur postgres
CREATE EXTENSION postgis;
-- à faire par utilisateur lexika
DROP TABLE IF EXISTS test;
CREATE TABLE test(
    id int PRIMARY KEY,
    geom geometry(POLYGON, 0)
);
CREATE INDEX ON test USING GIST ( geom ); 

INSERT INTO test
VALUES (1, ST_MakeEnvelope(0, 0, 10, 20)),
    (2, ST_MakeEnvelope(0, 10, 20, 20)),
    (3, ST_MakeEnvelope(20, 20, 30, 30)),
    (4, ST_MakeEnvelope(20, 0, 30, 20));

-- tous les rectangles
SELECT test.*,
    st_area(geom) AS area
FROM test;

-- les intersections
SELECT t1.id,
    t2.id,
    ST_Intersection(t1.geom, t2.geom) AS geom,
    ST_Area(ST_Intersection(t1.geom, t2.geom)) AS area
FROM test t1
    JOIN test t2 ON ST_Intersects(t1.geom, t2.geom)
WHERE t1.id <> t2.id;