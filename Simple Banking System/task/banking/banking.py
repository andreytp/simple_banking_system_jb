import sqlite3

MAIN_MENU: list[str] = ['Create an account',
                        'Log into account', ]

LOGGED_IN_MENU: list[str] = ['Balance',
                             'Add income',
                             'Do transfer',
                             'Close account',
                             'Log out', ]


class Cards:
    BIN = '400000'

    def __init__(self):
        self.db_conn = self._init_db()
        self.card = None
        self.is_login = False
        self.balance = None

    @staticmethod
    def get_full_card_number(card_number):
        all_card_num = Cards.BIN + card_number
        return all_card_num + luhn_check(all_card_num)

    @staticmethod
    def _init_db():
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

    def get_last_card_num(self):
        result = self.select('SELECT number FROM card'
                             ' WHERE id in '
                             '  (SELECT max(id) '
                             '    FROM card)')
        if result:
            return result[0][0]
        return Cards.BIN + '000000000' + luhn_check(Cards.BIN + '000000000')

    def select(self, querytext, params=None):
        cursor = self.db_conn.cursor()
        if params:
            cursor.execute(querytext, params)
        else:
            cursor.execute(querytext)

        result = cursor.fetchall()
        cursor.close()
        return result

    def change_query(self, querytext, params=None):
        cursor = self.db_conn.cursor()
        if params:
            cursor.execute(querytext, params)
        else:
            cursor.execute(querytext)

        self.db_conn.commit()
        cursor.close()

    def create_account(self):
        last_cards = self.get_last_card_num()[6:15]
        next_card_number = f'{(int(last_cards) + 1):09d}'
        import random
        random.seed()
        pin = random.randint(1000, 9999)
        new_full_card_number = self.get_full_card_number(next_card_number)
        self.change_query('INSERT INTO card (number, pin) values(?, ?)', (new_full_card_number, pin))

        print('Your card has been created')
        print('Your card number:')
        print(new_full_card_number)
        print('Your card PIN:')
        print(pin)

    def login_into_account(self):
        print('Enter your card number:')
        card_num = input()
        print('Enter your PIN:')
        pin = input()

        result = self.select("SELECT pin, balance "
                             "FROM card "
                             "WHERE number = ? AND pin = ?", (card_num, pin))

        if not result:
            print('Wrong card number or PIN!')
            return False

        self.card = card_num
        self.balance = result[0][1]
        self.is_login = True

        print()
        print('You have successfully logged in!')
        print()
        return True

    def logout(self):
        self.change_query('UPDATE card '
                          'SET balance = ? '
                          'WHERE number = ?', (self.balance, self.card))
        self.card = None
        self.is_login = False
        self.balance = None

    def add_income(self):
        if not self.is_login:
            return
        print('Enter income:')
        income = int(input())
        self.balance += income
        self.change_query('UPDATE card '
                          'SET balance = ? '
                          'WHERE number = ?', (self.balance, self.card,))
        print('Income was added!')

    def do_transfer(self):
        if not self.is_login:
            return
        print('Transfer')
        print('Enter card number')
        card_num = input()

        if card_num == self.card:
            print("You can't transfer money to the same account!")
            return

        if not check_card_num(card_num):
            print("Probably you made a mistake in the card number. Please try again!")
            return

        result = self.select("SELECT balance FROM card WHERE number = ?", (card_num,))

        if not result:
            print("Such a card does not exist.")
            return

        print('Enter how much money you want to transfer:')
        money = int(input())

        if money > self.balance:
            print('Not enough money!')
            return

        self.balance -= money

        transfer_balance = money + result[0][0]

        self.change_query('UPDATE card '
                          'SET balance = ? '
                          'WHERE number = ?', (transfer_balance, card_num,))

        self.change_query('UPDATE card '
                          'SET balance = ? '
                          'WHERE number = ?', (self.balance, self.card,))


        print('Success!')

    def close_account(self):
        self.change_query('DELETE FROM card WHERE number = ?', (self.card,))
        self.logout()
        print('The account has been closed!')


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


def print_menu(menu_list: list[str]):
    for number, item in enumerate(menu_list):
        print(f'{number + 1}. {item}')
    print('0. Exit')


def logon_actions(cards: Cards):
    while True:
        print_menu(LOGGED_IN_MENU)

        choice = int(input())

        if choice == 0:
            if cards.is_login:
                cards.logout()
            print('Bye!')
            return True

        if choice == 1:
            if cards.is_login:
                print()
                print(f'Balance: {cards.balance if cards.balance else 0}')
                print()
            continue

        if choice == 2:
            cards.add_income()
            continue

        if choice == 3:
            cards.do_transfer()
            continue

        if choice == 4:
            cards.close_account()
            return False

        if choice == 5:
            cards.logout()
            print()
            print('You have successfully logged out!')
            print()


def main_actions(cards: Cards):
    while True:
        print_menu(MAIN_MENU)

        choice = int(input())

        if choice == 0:
            print('Bye!')
            break

        if choice == 1:
            cards.create_account()
            continue

        if choice == 2:
            if cards.login_into_account():
                if logon_actions(cards):
                    break
            continue


if __name__ == '__main__':
    cards = Cards()
    main_actions(cards)
    # print(luhn_check('400000844943340'))

# Enter your card number:
# 4000000000000028
# Enter your PIN:
# 9676

# Your card number:
# 4000000000000010
# Your card PIN:
# 2747
