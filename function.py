import sqlite3

connect = sqlite3.connect('dbase.db', check_same_thread=False)
cursor = connect.cursor()

resull = cursor.execute('''
 CREATE TABLE IF NOT EXISTS
 "users"
 ("id" INTEGER NOT NULL,
 "tg_id" INTEGER NOT NULL,
 primary key("id" AUTOINCREMENT)
 )''')

resull = cursor.execute('''
 CREATE TABLE IF NOT EXISTS
 "categories"
 ("id" INTEGER NOT NULL,
 "name" TEXT NOT NULL,
    "value" TEXT NOT NULL,
 primary key("id" AUTOINCREMENT)
 )''')

resull = cursor.execute('''
 CREATE TABLE IF NOT EXISTS
 "subscribes"
 ("user_id" INTEGER NOT NULL,
 "category_id" INTEGER NOT NULL,
 FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
 FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
 )''')
connect.commit()
cursor.execute('''INSERT INTO categories (name) VALUES("sports")''')
cursor.execute('''INSERT INTO categories (name) VALUES("business")''')
cursor.execute('''INSERT INTO categories (name) VALUES("entertainment")''')
cursor.execute('''INSERT INTO categories (name) VALUES("general")''')
cursor.execute('''INSERT INTO categories (name) VALUES("technology")''')
connect.commit()


def searchUserCategory(user_id):
    connect = sqlite3.connect('dbase.db', check_same_thread=False)
    cursor = connect.cursor()
    return cursor.execute('''SELECT categories.name
        FROM subscribes 
        INNER JOIN categories ON subscribes.category_id = categories.id
        WHERE subscribes.user_id = ?
        ''',(user_id,)).fetchall()


def findCategory(name):
    connect = sqlite3.connect('dbase.db', check_same_thread=False)
    cursor = connect.cursor()
    return cursor.execute('''SELECT id
        FROM categories 
        WHERE name = ?
        ''',(name,)).fetchone()

def findCategoryName(category_id):
    connect = sqlite3.connect('dbase.db', check_same_thread=False)
    cursor = connect.cursor()
    return cursor.execute('''SELECT value
    FROM categories
    WHERE id = ?
    ''',(category_id,)).fetchone()


def deleteSubscribes(tg_id,id_category):
    connect = sqlite3.connect('dbase.db', check_same_thread=False)
    cursor = connect.cursor()
    cursor.execute('''DELETE FROM subscribes 
        WHERE user_id = ?
        AND category_id = ?
        ''', (tg_id, id_category))
    connect.commit()
    return "Вы отписались"

def findUserSubscribes(user_id):
    connect = sqlite3.connect('dbase.db', check_same_thread=False)
    cursor = connect.cursor()
    return cursor.execute('''SELECT categories.name FROM subscribes
    INNER JOIN categories ON categories.id = subscribes.category_id
    WHERE subscribes.user_id = ?
    ''',(user_id,)).fetchall()

def findUserId(tg_id):
    print(tg_id)
    connect = sqlite3.connect('dbase.db', check_same_thread=False)
    cursor = connect.cursor()
    return cursor.execute('''SELECT id
    FROM users
    WHERE tg_id = ?
    ''', (tg_id,)).fetchone()

cursor.close()