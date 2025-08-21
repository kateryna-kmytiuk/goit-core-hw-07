from collections import UserDict
from datetime import datetime, date, timedelta
from functools import wraps
import re


class Field:
    def __init__(self, value):
        self.value = value
    
    def __str__(self):
        return str(self.value)


class Name(Field):
	pass


class Phone(Field):
    def __init__(self, value):
        self.validate(value)
        super().__init__(value)

    def validate(self, value):
        if not (value.isdigit() and len(value) == 10):
            raise ValueError("The number must contain 10 digits.")


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        ph = self.find_phone(phone)
        if ph:
            self.phones.remove(ph)
    
    def edit_phone(self, old_phone, new_phone):
        for ind, phone in enumerate(self.phones):
            if phone.value == old_phone:
                self.phones[ind] = Phone(new_phone)
                return
        raise ValueError(f"Number {old_phone} does not exist.")

    def find_phone(self, phone):
        for ph in self.phones:
            if ph.value == phone:
                return ph
        return None
    
    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def show_birthday(self):
        if self.birthday:
            return self.birthday.value
        return "Birthday not set"

    def __str__(self):
        phones = ', '.join(p.value for p in self.phones)
        birthday = self.show_birthday() if self.birthday else "Not set"
        return f"Contact name: {self.name.value}; phones: {phones}; birthday: {birthday}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]


    def __find_next_weekday(self, start_date, weekday):
        days_ahead = weekday - start_date.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        return start_date + timedelta(days=days_ahead)


    def __adjust_for_weekend(self, birthday):
        if birthday.weekday() >= 5:
            return self.__find_next_weekday(birthday, 0)
        return birthday
    
    def get_upcoming_birthdays(self, days=7):
        upcoming_birthdays = []
        today = date.today()

        for record in self.data.values():
            if record.birthday:
                birthday_date = datetime.strptime(record.birthday.value, "%d.%m.%Y").date()
                birthday_this_year = birthday_date.replace(year=today.year)
                if birthday_this_year < today:
                    birthday_this_year = birthday_date.replace(year=today.year + 1)
                birthday_this_year = self.__adjust_for_weekend(birthday_this_year)
                if 0 <= (birthday_this_year - today).days <= days:
                    upcoming_birthdays.append({
                        "name": record.name.value,
                        "congratulation_date": birthday_this_year.strftime("%d.%m.%Y")
                    })
        return upcoming_birthdays

    def __str__(self):
        return "\n".join(str(record) for record in self.data.values())  


class Birthday(Field):
    def __init__(self, value):
        try:
            datetime.strptime(value, '%d.%m.%Y')
            super().__init__(value)
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        

def input_error(func):
    @wraps(func)
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            if "unpack" in str(e):
                return "Give me name and phone please."
            return str(e)
        except KeyError:
            return "Contact doesn't exist."
        except IndexError:
            return "Enter user name."
    return inner


@input_error
def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args


@input_error
def add_contact(args, book):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message


@input_error
def change_contact(args, book):
    name, old_phone, new_phone, *_ = args
    record = book.find(name)
    if record is None:
        return "Contact doesn't exist."
    record.edit_phone(old_phone, new_phone)
    return "Contact updated."
    

@input_error
def phone_contact(args, book):
    name, *_ = args
    record = book.find(name)
    if record is None:
        return "Contact doesn't exist."
    return ", ".join(phone.value for phone in record.phones)


@input_error
def all_contact(book):
    return str(book)


@input_error
def add_birthday(args, book):
    name, birthday, *_ = args
    record = book.find(name)
    if record is None:
        return "Contact doesn't exist."
    record.add_birthday(birthday)
    return "Birthday added."


@input_error
def show_birthday(args, book):
    name, *_ = args
    record = book.find(name)
    if record is None:
        return "Birthday not set for this contact."
    return record.show_birthday()


@input_error
def birthdays(book):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No birthdays in the next 7 days."
    return "\n".join(f"{user['name']}: {user['congratulation_date']}" for user in upcoming)



def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(phone_contact(args, book))

        elif command == "all":
            print(all_contact(book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(book))

        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()