DROP FUNCTION IF EXISTS get_id_langue;
CREATE OR REPLACE FUNCTION get_id_langue(l langue.nom_langue%TYPE)
    RETURNS SETOF langue.id_langue%TYPE AS
    $$
        SELECT id_langue FROM langue WHERE nom_langue = l
    $$
    LANGUAGE SQL
    STABLE;

DROP FUNCTION IF EXISTS get_id_livre;
CREATE OR REPLACE FUNCTION get_id_livre(l livre.nom_livre%TYPE)
    RETURNS SETOF livre.id_livre%TYPE AS
    $$
        SELECT id_livre FROM livre WHERE nom_livre = l
    $$
    LANGUAGE SQL
    STABLE;
DROP FUNCTION IF EXISTS query_engine;
DROP FUNCTION IF EXISTS tsquery_engine;
CREATE OR REPLACE FUNCTION tsquery_engine(keyword data.traduction%TYPE, langue_base langue.nom_langue%TYPE, offset_num int)
    RETURNS TABLE(
        sens int
    )
    LANGUAGE plpgsql AS
    $tsquery_engine$
    BEGIN
        RETURN QUERY
        SELECT id_data FROM data INNER JOIN (SELECT data.sens,data.id_langue,max(data.date_creation) FROM data
                                WHERE data.sens IN (SELECT DISTINCT data.sens FROM data
                                                        WHERE to_tsvector(data.traduction) @@ to_tsquery(keyword)
                                                        AND id_langue=(select get_id_langue(langue_base))
                                                        ORDER BY data.sens
                                                        LIMIT 25
                                                        OFFSET offset_num) GROUP BY data.sens,data.id_langue) AS tmp 
                                                        ON data.sens=tmp.sens AND data.id_langue=tmp.id_langue AND data.date_creation = tmp.max;
    END
    $tsquery_engine$;

DROP FUNCTION IF EXISTS regex_engine;
CREATE OR REPLACE FUNCTION regex_engine(keyword data.traduction%TYPE, langue_base langue.nom_langue%TYPE, offset_num int)
    RETURNS TABLE(
        sens int
    )
    LANGUAGE plpgsql AS
    $regex_engine$
    BEGIN
        RETURN QUERY
        SELECT id_data FROM data INNER JOIN (SELECT data.sens,data.id_langue,max(data.date_creation) FROM data
                                WHERE data.sens IN (SELECT DISTINCT data.sens FROM data
                                                        WHERE data.traduction ~* keyword
                                                        AND id_langue=(select get_id_langue(langue_base))
                                                        ORDER BY data.sens
                                                        LIMIT 25
                                                        OFFSET offset_num) GROUP BY data.sens,data.id_langue) AS tmp 
                                                        ON data.sens=tmp.sens AND data.id_langue=tmp.id_langue AND data.date_creation = tmp.max;
    END
    $regex_engine$;


DROP FUNCTION IF EXISTS get_result;
CREATE OR REPLACE FUNCTION get_result(keyword data.traduction%TYPE, engine text, langue_base langue.nom_langue%TYPE, offset_num int)
    RETURNS TABLE(
        sens int
    )
    LANGUAGE plpgsql AS
    $get_result$
    BEGIN
            IF engine = 'regex' THEN
                RETURN QUERY
                SELECT * FROM regex_engine(keyword,langue_base,offset_num);
            ELSIF engine = 'tsquery' THEN
                RETURN QUERY
                SELECT * FROM tsquery_engine(keyword,langue_base,offset_num);
            -- ELSE
                -- RAISE 'unknow engine' , engine , now();
            END IF;
    END
    $get_result$;

DROP FUNCTION IF EXISTS search;
CREATE OR REPLACE FUNCTION search(keyword data.traduction%TYPE,engine text, langue_target langue.nom_langue%TYPE, langue_base langue.nom_langue%TYPE, offset_num int)
    RETURNS TABLE(
        nom_langue text,
        traduction text,
        sens int,
        numeroPage int,
        nom_livre text
    )
    LANGUAGE plpgsql AS
    $funcSearch$
    BEGIN
        IF langue_target = 'all' THEN
            RETURN QUERY
            WITH result_research AS (
                SELECT * FROM get_result(keyword,engine,langue_base,offset_num)
            )
            SELECT langue.nom_langue,data.traduction,data.sens,data.numero_page , livre.nom_livre
                            FROM data JOIN livre ON data.id_livre = livre.id_livre
                            JOIN langue ON data.id_langue = langue.id_langue
                            WHERE data.id_data IN  (SELECT * FROM get_result(keyword,engine,langue_base,offset_num)) ORDER BY data.sens;
        ELSE
        RETURN QUERY
            SELECT langue.nom_langue,data.traduction,data.sens,data.numero_page , livre.nom_livre
                            FROM data JOIN livre ON data.id_livre = livre.id_livre  
                            JOIN langue ON data.id_langue = langue.id_langue 
                            WHERE (data.id_langue=(select get_id_langue(langue_base))
                                    OR data.id_langue=(select get_id_langue(langue_target)))
                            AND data.id_data IN (SELECT * FROM get_result(keyword,engine,langue_base,offset_num)) ORDER BY data.sens;    
        END IF;
        END
    $funcSearch$;


DROP FUNCTION IF EXISTS page_engine;
CREATE OR REPLACE FUNCTION page_engine(num_page int , livre livre.nom_livre%TYPE)
    RETURNS TABLE(
        sens int
    )
    LANGUAGE plpgsql AS
    $tsquery_engine$
    BEGIN
        RETURN QUERY
        SELECT id_data FROM data INNER JOIN (SELECT data.sens,data.id_langue,max(data.date_creation) FROM data
                                WHERE data.sens IN (SELECT DISTINCT data.sens FROM data
                                                        WHERE data.numero_page = num_page and data.id_livre = (SELECT get_id_livre(livre))
                                                        ORDER BY data.sens) GROUP BY data.sens,data.id_langue) as tmp 
                                                        on data.sens=tmp.sens and data.id_langue=tmp.id_langue and data.date_creation = tmp.max;
    END
    $tsquery_engine$;

DROP FUNCTION IF EXISTS search_by_page;
CREATE OR REPLACE FUNCTION search_by_page(page int, livre livre.nom_livre%TYPE)
    RETURNS TABLE(
        nom_langue text,
        traduction text,
        sens int
    )
    LANGUAGE plpgsql AS
    $funcSearch$
    BEGIN
        RETURN QUERY
        SELECT langue.nom_langue,data.traduction,data.sens
                        FROM data JOIN langue ON data.id_langue = langue.id_langue
                        WHERE data.id_data IN (select * from page_engine(page,livre)) ORDER BY data.sens;   
        END
    $funcSearch$;
