import os
import zipfile
import sqlite3
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TALB, APIC
from mutagen.id3 import ID3, ID3NoHeaderError, error
import mutagen

def create_database(db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS economist_zip_info (
            filename TEXT PRIMARY KEY,
            size INTEGER,
            file_count INTEGER
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS economist_article_info (
            zip_filename TEXT,
            mp3_filename TEXT,
            artist TEXT,
            album TEXT,
            title TEXT,
            duration REAL,
            file_size INTEGER,
            PRIMARY KEY (zip_filename, mp3_filename)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS economist_issue_covers (
            zip_filename TEXT PRIMARY KEY,
            cover_path TEXT
        )
    ''')
    conn.commit()
    return conn

def get_zip_info(zip_path):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        file_count = len(zip_ref.namelist())
    size = os.path.getsize(zip_path)
    return size, file_count

def insert_zip_info(conn, filename, size, file_count):
    cursor = conn.cursor()
    cursor.execute('''
        REPLACE INTO economist_zip_info (filename, size, file_count)
        VALUES (?, ?, ?)
    ''', (filename, size, file_count))
    conn.commit()

def extract_id3_info(conn, zip_filename, mp3_filename, id3_data):
    cursor = conn.cursor()
    cursor.execute('''
        REPLACE INTO economist_article_info (zip_filename, mp3_filename, artist, album, title, duration, file_size)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (zip_filename, mp3_filename, id3_data['artist'], id3_data['album'], id3_data['title'], id3_data['duration'], id3_data['file_size']))
    conn.commit()

def insert_cover_info(conn, zip_filename, cover_path):
    cursor = conn.cursor()
    cursor.execute('''
        REPLACE INTO economist_issue_covers (zip_filename, cover_path)
        VALUES (?, ?)
    ''', (zip_filename, cover_path))
    conn.commit()

def save_cover_art(cover_data, cover_dir, zip_filename):
    if not os.path.exists(cover_dir):
        os.makedirs(cover_dir)
    cover_art_filename = f"{os.path.splitext(zip_filename)[0]}.jpg"
    cover_art_path = os.path.join(cover_dir, cover_art_filename)
    with open(cover_art_path, 'wb') as img_file:
        img_file.write(cover_data)
    return cover_art_path

def process_zip_file(conn, zip_path, cover_dir):
    cover_found = False
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for file_info in zip_ref.infolist():
            if file_info.filename.endswith('.mp3'):
                try:
                    with zip_ref.open(file_info.filename) as mp3_file:
                        mp3_data = MP3(mp3_file, ID3=ID3)
                        id3_data = {
                            'artist': mp3_data.get('TPE1', [''])[0],
                            'album': mp3_data.get('TALB', [''])[0],
                            'title': mp3_data.get('TIT2', [''])[0],
                            'duration': mp3_data.info.length,
                            'file_size': file_info.file_size
                        }
                        # Check for cover art and stop if found
                        if not cover_found and 'APIC:' in mp3_data:
                            cover_art = mp3_data['APIC:'].data
                            cover_art_path = save_cover_art(cover_art, cover_dir, os.path.basename(zip_path))
                            insert_cover_info(conn, os.path.basename(zip_path), cover_art_path)
                            cover_found = True
                except (ID3NoHeaderError, error, mutagen.mp3.HeaderNotFoundError):
                    id3_data = {
                        'artist': None,
                        'album': None,
                        'title': None,
                        'duration': None,
                        'file_size': file_info.file_size
                    }
                extract_id3_info(conn, os.path.basename(zip_path), file_info.filename, id3_data)
            #if cover_found:
            #    break  # Stop processing further MP3 files for cover art once found

def enumerate_zip_files(directory, db_name, cover_dir):
    conn = create_database(db_name)
    zip_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.zip'):
                zip_files.append(os.path.join(root, file))

    zip_files.sort()  # Sort the zip files alphabetically

    for zip_path in zip_files:
        print(zip_path)
        size, file_count = get_zip_info(zip_path)
        insert_zip_info(conn, os.path.basename(zip_path), size, file_count)
        process_zip_file(conn, zip_path, cover_dir)

    conn.close()

# Example usage
directory = '/home/pedwards/economist_audio_archives/'
db_name = '/dockerama/dockerama_applications.db'
cover_dir = 'covers'
enumerate_zip_files(directory, db_name, cover_dir)
