import random
import sqlite3


def get_checksum_by_luhn_algorithm(num_card):
    all_sum = 0
    for i, d in enumerate(num_card, 1):
        val = int(d) * (2 ** (i % 2))
        if val > 9:
            val -= 9
        all_sum += val

    ost_10 = all_sum % 10
    last_dig = 0 if not ost_10 else (10 - ost_10)
    return str(last_dig)


class MyBank:

    def __init__(self):
        self.bin_part = "400000"

        self.transfer_card_num = None
        self.current_card = None
        self.status = "main_menu"

        self.conn = None
        self.make_base()

    def make_base(self):
        conn = sqlite3.connect("card.s3db")
        conn.row_factory = sqlite3.Row

        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE if not exists card (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        number TEXT,
        pin TEXT,
        balance INTEGER DEFAULT 0)""")

        self.conn = conn

    def get_menu_text(self):

        menu_text = ""
        if self.status == "main_menu":

            menu_text = "1. Create an account\n" \
                        "2. Log into account\n" \
                        "0. Exit\n"

        elif self.status == "card_info":

            menu_text = "1. Balance\n" \
                        "2. Add income\n" \
                        "3. Do transfer\n" \
                        "4. Close account\n" \
                        "5. Log out\n" \
                        "0. Exit\n"

        elif self.status == "add_income":

            menu_text = "Enter income:\n"

        elif self.status == "transfer":

            menu_text = "Transfer\n" \
                        "Enter card number:\n"

            self.status = "transfer_card"

        elif self.status == "transfer_sum":

            menu_text = "Enter how much money you want to transfer:\n"

        return menu_text

    def menu_operations(self, user_input: str):

        print()

        if self.status == "main_menu":

            if user_input == "1":
                self.create_account()
            elif user_input == "2":
                self.log_in_acc()
            else:
                self.exit_bank()

        elif self.status == "card_info":

            if user_input == "1":
                print(f"Balance: {self.current_card['balance']}")
            elif user_input == "2":
                self.status = "add_income"
            elif user_input == "3":
                self.status = "transfer"
            elif user_input == "4":
                self.close_acc()
                self.status = "main_menu"
            elif user_input == "5":
                print("You have successfully logged out!")
                self.status = "main_menu"
            else:
                self.exit_bank()

        elif self.status == "add_income":

            self.add_income(user_input)
            self.status = "card_info"

        elif self.status == "transfer_card":

            if self.check_transfer_card(user_input):
                self.status = "transfer_sum"
            else:
                self.status = "card_info"

        elif self.status == "transfer_sum":

            self.make_transfer(int(user_input))
            self.status = "card_info"

    def exit_bank(self):
        print("Bye!")
        self.status = "Exit"
        self.conn.close()

    def create_account(self):

        account_part = f"{random.randint(1, 999999999):09d}"
        pin = f"{random.randint(1, 9999):04d}"

        card_num = self.bin_part + account_part
        card_num += get_checksum_by_luhn_algorithm(card_num)

        cursor = self.conn.cursor()
        sql = "INSERT INTO card (number, pin) VALUES (:number, :pin)"
        cursor.execute(sql, {"number": card_num, "pin": pin})
        self.conn.commit()

        print("Your card has been created")
        print("Your card number:", card_num, sep="\n")
        print("Your card PIN:", pin, sep="\n")

    def log_in_acc(self):
        card_num = input("Enter your card number:\n")
        pin = input("Enter your PIN:\n")
        print()

        result = self.find_acc(card_num)
        if result is None or pin != result["pin"]:
            print("Wrong card number or PIN!\n")
        else:
            print("You have successfully logged in!\n")
            self.status = "card_info"
            self.current_card = dict(result)

    def find_acc(self, card_num):
        cursor = self.conn.cursor()
        cursor.execute("SELECT number, pin, balance FROM card where number=:number", {"number": card_num})
        result = cursor.fetchone()
        return result

    def add_income(self, income_sum):
        new_balance = self.current_card["balance"] + int(income_sum)
        self.current_card["balance"] = new_balance

        cursor = self.conn.cursor()
        cursor.execute("UPDATE card SET balance = :balance where number=:number",
                       {"number": self.current_card["number"],
                        "balance": new_balance})
        self.conn.commit()

    def close_acc(self):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM card where number=:number", {"number": self.current_card["number"]})
        self.conn.commit()

        print("The account has been closed!\n")

    def check_transfer_card(self, card_num):

        check_result = True

        if len(card_num) != 16 or card_num[-1] != get_checksum_by_luhn_algorithm(card_num[:-1]):

            print("Probably you made mistake in the card number. Please try again!\n")
            check_result = False

        elif card_num == self.current_card["number"]:

            print("You can't transfer money to the same account!\n")
            check_result = False

        else:

            result = self.find_acc(card_num)
            if result is None:
                print("Such a card does not exist.\n")
                check_result = False
            else:
                self.transfer_card_num = result["number"]

        return check_result

    def make_transfer(self, transfer_sum):

        if transfer_sum > self.current_card["balance"]:
            print("Not enough money!")
        else:
            cursor = self.conn.cursor()
            cursor.execute("UPDATE card SET balance = balance + :balance where number=:number",
                           {"number": self.transfer_card_num,
                            "balance": transfer_sum})
            cursor.execute("UPDATE card SET balance = balance - :balance where number=:number",
                           {"number": self.current_card["number"],
                            "balance": transfer_sum})
            self.conn.commit()
            print("Success!")


bank = MyBank()

while True:

    inp = input(bank.get_menu_text())

    bank.menu_operations(inp)

    if bank.status == "Exit":
        break
