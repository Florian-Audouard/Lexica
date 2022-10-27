"""_summary_

    Returns:
        _type_: _description_
    """

import os
import urllib.parse
import psycopg

from dotenv import dotenv_values
from tqdm import tqdm

# import asyncio

# select mots from data
# where langue=(select id from langue where nom='pije') and mots ~* '^(\w{3,})\1';
os.chdir(os.path.dirname(__file__))

config = dotenv_values(".env")

FILENAME_SHEMA = "database/database.sql"

options = urllib.parse.quote_plus("--search_path=modern,public")
CONN_PARAMS = f"postgresql://{config['USER']}:{config['PASSWORD']}@{config['HOST']}:{config['PORT']}/{config['DATABASE']}?options={options}"  # pylint: disable=line-too-long


def reset_table():
    """_summary_"""
    with psycopg.connect(CONN_PARAMS) as conn:  # pylint: disable=not-context-manager
        with conn.cursor() as cur:
            with open(FILENAME_SHEMA, "r", encoding="utf-8") as file:
                cur.execute(file.read())


def add_langue(cur, langue):
    """_summary_

    Args:
        cur (_type_): _description_
        langue (_type_): _description_
    """
    cur.execute("INSERT INTO langue (nom) VALUES (%(langue)s);", {"langue": langue})


def add_line(cur, line, liste_langue, count):
    """_summary_

    Args:
        cur (_type_): _description_
        langue (_type_): _description_
    """
    liste_line = line.split(";")
    num_page = liste_line[len(liste_line) - 1]
    del liste_line[len(liste_line) - 1]
    requete = "INSERT INTO data (langue , sens , mots , numeroPage) VALUES "
    for langue, mot in zip(liste_langue, liste_line):
        if mot != "":
            mot = mot.replace("'", "''")
            requete += f"""
            ((select id_langue('{langue}')),'{count}','{mot}','{num_page}'),"""
    requete = requete[0 : len(requete) - 1] + ";"
    cur.execute(requete)


def modif_data(langue, text, sens):
    """_summary_

    Args:
        cur (_type_): _description_
        langue (_type_): _description_
    """
    with psycopg.connect(CONN_PARAMS) as conn:  # pylint: disable=not-context-manager
        with conn.cursor() as cur:
            # todo row trigger after insert
            cur.execute(
                """INSERT INTO data (langue , sens , mots , numeroPage)
                        VALUES((select id_langue(%(langue)s)),%(sens)s,%(text)s,
                        (SELECT DISTINCT numeroPage FROM data where sens=%(sens)s))""",
                {
                    "langue": langue,
                    "text": text,
                    "sens": sens,
                },
            )


def search(keyword, langue, langue_base, offset):
    """_summary_

    Args:
        cur (_type_): _description_
        langue (_type_): _description_
    """
    res = []
    with psycopg.connect(CONN_PARAMS) as conn:  # pylint: disable=not-context-manager
        with conn.cursor() as cur:
            # argument a la place {} ~ a la place de like
            # https://www.postgresql.org/docs/current/functions-matching.html#FUNCTIONS-POSIX-REGEXP
            # enfin https://www.postgresql.org/docs/current/pgtrgm.html
            # peut etre https://www.postgresql.org/docs/current/fuzzystrmatch.html
            # apres https://www.postgresql.org/docs/current/textsearch.html

            # * REGEXP
            # cur.execute(
            #     """
            #     SELECT DISTINCT count(sens) FROM data
            #         WHERE mots ~* %(keyword)s
            #         AND langue=(select id_langue(%(langueBase)s))""",
            #     {
            #         "keyword": keyword,
            #         "langueBase": langue_base,
            #     },
            # )
            # count = cur.fetchone()[0]
            # print(count)
            # cur.execute(
            #     """
            #     SELECT DISTINCT sens FROM data
            #         WHERE mots ~* %(keyword)s
            #         AND langue=(select id_langue(%(langueBase)s))
            #         ORDER BY sens
            #         LIMIT 25
            #         OFFSET %(offset)s;
            #         """,
            #     {
            #         "keyword": keyword,
            #         "langueBase": langue_base,
            #         "offset": offset,
            #     },
            # )

            # * TSQUERY
            cur.execute(
                """
                SELECT DISTINCT count(sens) FROM data
                    WHERE to_tsvector(mots) @@ to_tsquery(%(keyword)s)
                    AND langue=(select id_langue(%(langueBase)s))""",
                {
                    "keyword": keyword,
                    "langueBase": langue_base,
                },
            )
            count = cur.fetchone()[0]
            print(count)
            cur.execute(
                """
                SELECT DISTINCT sens FROM data
                    WHERE to_tsvector(mots) @@ to_tsquery(%(keyword)s)
                    AND langue=(select id_langue(%(langueBase)s))
                    ORDER BY sens
                    LIMIT 25
                    OFFSET %(offset)s;
                    """,
                {
                    "keyword": keyword,
                    "langueBase": langue_base,
                    "offset": offset,
                },
            )

            # * METAPHONE
            # cur.execute(
            #     """
            #     SELECT DISTINCT count(sens) FROM data
            #         WHERE dmetaphone(mots) = dmetaphone(%(keyword)s)
            #         AND langue=(select id_langue(%(langueBase)s))""",
            #     {
            #         "keyword": keyword,
            #         "langueBase": langue_base,
            #     },
            # )
            # count = cur.fetchone()[0]
            # print(count)
            # cur.execute(
            #     """
            #     SELECT DISTINCT sens FROM data
            #         WHERE dmetaphone(mots) = dmetaphone(%(keyword)s)
            #         AND langue=(select id_langue(%(langueBase)s))
            #         ORDER BY sens
            #         LIMIT 25
            #         OFFSET %(offset)s;
            #         """,
            #     {
            #         "keyword": keyword,
            #         "langueBase": langue_base,
            #         "offset": offset,
            #     },
            # )

            # * SIMILARITY
            # cur.execute(
            #     """
            #     SELECT DISTINCT count(sens) FROM data
            #         WHERE similarity(mots,%(keyword)s) > 0.3
            #         AND langue=(select id_langue(%(langueBase)s))""",
            #     {
            #         "keyword": keyword,
            #         "langueBase": langue_base,
            #     },
            # )
            # count = cur.fetchone()[0]
            # print(count)
            # cur.execute(
            #     """
            #     SELECT sens,similarity(mots,%(keyword)s),mots FROM data
            #         WHERE similarity(mots,%(keyword)s) > 0.3
            #         AND langue=(select id_langue(%(langueBase)s))
            #         ORDER BY sens
            #         LIMIT 25
            #         OFFSET %(offset)s;
            #         """,
            #     {
            #         "keyword": keyword,
            #         "langueBase": langue_base,
            #         "offset": offset,
            #     },
            # )
            liste = cur.fetchall()
            for sens in liste:
                sens = sens[0]
                if langue == "all":
                    cur.execute(
                        """SELECT nom,mots,sens,numeroPage 
                            FROM data JOIN langue ON data.langue = langue.id
                            WHERE data.id IN
                            (SELECT max(data.id) AS id FROM data
                                WHERE sens=%(sens)s GROUP BY langue);""",
                        {"sens": sens},
                    )
                else:

                    cur.execute(
                        """SELECT nom,mots,sens,numeroPage FROM data JOIN langue ON data.langue = langue.id
                            WHERE (langue=(select id_langue(%(langueBase)s))
                                    OR langue=(select id_langue(%(langue)s)))
                                AND data.id IN
                            (SELECT max(data.id) AS id FROM data
                                WHERE sens=%(sens)s GROUP BY langue);""",
                        {
                            "langueBase": langue_base,
                            "langue": langue,
                            "sens": sens,
                        },
                    )

                res.append(cur.fetchall())

    return [res, count]


def history(sens, langue):
    with psycopg.connect(CONN_PARAMS) as conn:  # pylint: disable=not-context-manager
        with conn.cursor() as cur:
            cur.execute(
                """SELECT date_creation,mots FROM data
                    WHERE sens=%(sens)s and langue=(select id_langue(%(langue)s))
                    ORDER BY date_creation desc;""",
                {"sens": sens, "langue": langue},
            )
            return cur.fetchall()


def list_langue():
    with psycopg.connect(CONN_PARAMS) as conn:  # pylint: disable=not-context-manager
        with conn.cursor() as cur:
            cur.execute("SELECT nom FROM langue;")
            tempory = cur.fetchall()
            res = []
            for langue in tempory:
                res.append(langue[0])
            return res


def insert_from_csv(filename="output.csv"):
    """_summary_

    Args:
        filename (str, optional): _description_. Defaults to "output.csv".
    """
    filename = "release/" + filename
    reset_table()
    liste_langue = [
        "français",
        "pije",
        "fwâi",
        "nemi 1 (Temala)",
        "nemi 2 (côte est)",
        "jawe",
    ]

    with psycopg.connect(CONN_PARAMS) as conn:  # pylint: disable=not-context-manager
        with conn.cursor() as cur:
            for langue in liste_langue:
                add_langue(cur, langue)
            with open(filename, "r", encoding="utf-8") as file:
                liste_line = file.readlines()
                with tqdm(total=len(liste_line)) as pbar:
                    count = 0
                    for line in liste_line:
                        add_line(cur, line.replace("\n", ""), liste_langue, count)
                        count += 1
                        pbar.update()


if __name__ == "__main__":
    insert_from_csv()
