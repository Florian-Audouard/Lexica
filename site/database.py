import psycopg

# import asyncio

# select mots from data where langue=(select id from langue where nom='pije') and mots ~* '^(\w{3,})\1';

from dotenv import dotenv_values
import os

import urllib.parse
from tqdm import tqdm


os.chdir(os.path.dirname(__file__))

config = dotenv_values(".env")

filename_schema = "database/database.sql"

options = urllib.parse.quote_plus("--search_path=modern,public")
CONN_PARAMS = f"postgresql://{config['USER']}:{config['PASSWORD']}@{config['HOST']}:{config['PORT']}/{config['DATABASE']}?options={options}"  # pylint: disable=line-too-long


def reset_table():
    with psycopg.connect(CONN_PARAMS) as conn:
        with conn.cursor() as cur:
            with open(filename_schema, "r", encoding="utf-8") as file:
                cur.execute(file.read())


def add_langue(cur, langue):
    cur.execute(f"INSERT INTO langue (nom) VALUES ('{langue}');")


def add_line(cur, line, liste_langue):
    liste_line = line.split(";")
    requete = f"""
        WITH aleatoire AS(
            SELECT gen_random_uuid() AS val
        )
        INSERT INTO data (langue , sens , mots) VALUES 
        """
    for langue, mot in zip(liste_langue, liste_line):
        if mot != "":
            mot = mot.replace("'", "''")
            requete += f"""
            ((SELECT id FROM langue WHERE nom='{langue}'),(SELECT (val) FROM aleatoire),'{mot}'),"""
    requete = requete[0 : len(requete) - 1]
    cur.execute(requete)


def modifData(langue, text, sens):
    with psycopg.connect(CONN_PARAMS) as conn:
        with conn.cursor() as cur:
            # todo row trigger after insert
            cur.execute(
                f"INSERT INTO data (langue,sens, mots) VALUES((select id from langue where nom='{langue}'),'{sens}','{text}') ON CONFLICT (langue,sens) DO UPDATE SET  mots='{text}';"
            )


def search(
    keyword,
    langue="all",
    langueBase="français",
):
    res = []
    with psycopg.connect(CONN_PARAMS) as conn:
        with conn.cursor() as cur:
            # todo argument a la place {} ~ a la place de like
            # todo https://www.postgresql.org/docs/current/functions-matching.html#FUNCTIONS-POSIX-REGEXP
            # enfin https://www.postgresql.org/docs/current/pgtrgm.html
            # peut etre https://www.postgresql.org/docs/current/fuzzystrmatch.html
            # apres https://www.postgresql.org/docs/current/textsearch.html
            cur.execute(
                """
                SELECT sens FROM data 
                    WHERE dmetaphone(mots) = dmetaphone(%(keyword)s) AND langue=(select id_langue(%(langueBase)s));""",
                {"keyword": keyword, "langueBase": langueBase},
            )
            # si erreur avec similarity
            # GRANT ALL ON DATABASE lexica TO lexica;
            liste = cur.fetchall()
            for element in liste:
                element = element[0]
                if langue == "all":
                    cur.execute(
                        "SELECT nom,mots,sens FROM data JOIN langue ON data.langue = langue.id WHERE sens=%(element)s;",
                        {"element": element},
                    )
                else:
                    cur.execute(
                        """SELECT nom,mots,sens FROM data JOIN langue ON data.langue = langue.id 
                                WHERE (langue=(select id_langue(%(langueBase)s)) 
                                    OR langue=(select id_langue(%(langue)s))) AND sens=%(element)s;""",
                        {
                            "langueBase": langueBase,
                            "langue": langue,
                            "element": element,
                        },
                    )

                res.append(cur.fetchall())

    return res


def insertFromCSV(filename="outputfr.csv"):
    reset_table()
    liste_langue = [
        "français",
        "pije",
        "fwâi",
        "nemi 1 (Temala)",
        "nemi 2 (côte est)",
        "jawe",
    ]

    with psycopg.connect(CONN_PARAMS) as conn:
        with conn.cursor() as cur:
            for langue in liste_langue:
                add_langue(cur, langue)
            with open(filename, "r") as file:
                liste_line = file.readlines()
                with tqdm(total=len(liste_line)) as pbar:
                    for line in liste_line:
                        add_line(cur, line.replace("\n", ""), liste_langue)
                        pbar.update()


if __name__ == "__main__":
    insertFromCSV()
