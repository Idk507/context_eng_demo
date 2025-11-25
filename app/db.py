import sqlite3
import os 
from pathlib import Path 
import argparse


BASE_DIR = Path(__file__).resolve().parent

DB_PATH = Path("./data/context_agent.db")

CREATE_USERS = """
CREATE TABLE IF NOT EXISTS users (
id TEXT PRIMARY KEY,
name TEXT NOT NULL,
email TEXT  );

"""

CREATE_ARTICLES = """
CREATE TABLE IF NOT EXISTS articles (
id TEXT PRIMARY KEY,
title TEXT ,
content TEXT
);

"""

SAMPLE_ARTICLES = [
    ("How to use the Context-Engineered Agent", "This article explains how context engineering works..."),
    ("Scaling LangChain Agents", "Best practices for scaling agents: summarization, dynamic tool selection...")
]


def init_db(path : Path = DB_PATH):
    path.parent.mkdir(parents = True,exist_ok= True)
    conn = sqlite3.connect(path)
    cur = conn.cursor
    cur.executescript(CREATE_USERS)
    cur.executescript(CREATE_ARTICLES)
    cur.executemany("INSERT INTO articles (title, content) VALUES (?, ?)", SAMPLE_ARTICLES)
    conn.commit()
    conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--init",action="store_true")
    args = parser.parse_args()
    if args.init:
        init_db()
        print(f"Database initialized at {DB_PATH}")