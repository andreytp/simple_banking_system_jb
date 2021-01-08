import sqlite3

MAIN_MENU: list[str] = ['Create an account',
                        'Log into account', ]

LOGGED_IN_MENU: list[str] = ['Balance',
                             'Log out', ]

BIN = '400000'
cards = {'000000000': '0000',
         }

BALANCE = 0


def find_card(card_number: str) -> dict:
    account_id = card_number[6:15]
    return cards.get(account_id)


def luhn_check(all_card_num):
    digits_sum = 0

    for index, char in enumerate(all_card_num):
        v = int(char)
        if index % 2 == 0:
            v = int(char) * 2
            if v > 9:
                v -= 9
        digits_sum += v

    r = digits_sum % 10
    if r != 0:
        r = 10 - r
    return str(r)


def check_card_num(card_num):
    return luhn_check(card_num[:-1]) == card_num[-1]


def get_full_card_number(card_number):
    all_card_num = BIN + card_number
    return all_card_num + luhn_check(all_card_num)


def get_last_card_num(db_conn):
    cursor = db_conn.cursor()
    cursor.execute('SELECT number FROM card WHERE id in (SELECT max(id) FROM card)')
    result = cursor.fetchall()
    cursor.close()
    if result:
        return result[0][0]
    return BIN + '000000000' + luhn_check(BIN + '000000000')


def create_account(db_conn):
    # last_cards = sorted(cards, reverse=True)[0]
    last_cards = get_last_card_num(db_conn)[6:15]
    next_card_number = f'{(int(last_cards) + 1):09d}'
    import random
    random.seed()
    pin = random.randint(1000, 9999)
    new_full_card_number = get_full_card_number(next_card_number)
    cursor = db_conn.cursor()
    cursor.execute('INSERT INTO card (number, pin) values(?, ?)', (new_full_card_number, pin))
    db_conn.commit()
    cursor.close()
    # cards[next_card_number] = str(pin)

    print('Your card has been created')
    print('Your card number:')
    print(new_full_card_number)
    print('Your card PIN:')
    print(pin)


def print_menu(menu_list: list[str]):
    for number, item in enumerate(menu_list):
        print(f'{number + 1}. {item}')
    print('0. Exit')


def login_into_account(db_conn):
    print('Enter your card number:')
    card_num = input()
    print('Enter your PIN:')
    pin = input()

    cursor = db_conn.cursor()
    cursor.execute("SELECT pin, balance FROM card WHERE number = ? AND pin = ?", (card_num, pin))
    result = cursor.fetchall()

    if not result:
        print('Wrong card number or PIN!')
        return False
    print()
    print('You have successfully logged in!')
    print()
    return logon_actions(db_conn, balance=result[0][1])


def logon_actions(db_conn, balance=None):
    while True:
        print_menu(LOGGED_IN_MENU)

        choice = int(input())

        if choice == 0:
            print('Bye!')
            return True

        if choice == 1:
            print()
            print(f'Balance: {balance if balance else 0}')
            print()

        if choice == 2:
            print()
            print('You have successfully logged out!')
            balance = None
            print()


def main_actions(db_conn):
    while True:
        print_menu(MAIN_MENU)

        choice = int(input())

        if choice == 0:
            print('Bye!')
            break

        if choice == 1:
            create_account(db_conn)
            continue

        if choice == 2:
            if login_into_account(db_conn):
                break
            continue


def init_db():
    conn = sqlite3.connect('card.s3db')
    cur = conn.cursor()
    cur.execute(" CREATE TABLE IF NOT EXISTS card ("
                "id INTEGER PRIMARY KEY,"
                "number TEXT UNIQUE,"
                "pin TEXT,"
                "balance INTEGER DEFAULT 0"
                ")")
    conn.commit()
    cur.close()
    return conn


if __name__ == '__main__':
    conn = init_db()
    main_actions(conn)
    # print(luhn_check('400000844943340'))
