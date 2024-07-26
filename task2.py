from datetime import datetime, timedelta
import re
from collections import UserDict

# Класи для полів і записів


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    def __init__(self, value):
        super().__init__(value)


class Phone(Field):
    def __init__(self, value):
        if not re.match(r"^\d{10}$", value):
            raise ValueError("Phone number must contain exactly 10 digits.")
        super().__init__(value)


class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, '%d.%m.%Y').date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                self.phones.remove(p)
                return True
        return False

    def edit_phone(self, old_phone, new_phone):
        for p in self.phones:
            if p.value == old_phone:
                self.phones.remove(p)
                self.phones.append(Phone(new_phone))
                return True
        return False

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def days_to_birthday(self):
        if self.birthday:
            today = datetime.now().date()
            next_birthday = self.birthday.value.replace(year=today.year)
            if next_birthday < today:
                next_birthday = self.birthday.value.replace(
                    year=today.year + 1)
            return (next_birthday - today).days
        return None

    def __str__(self):
        phones = '; '.join(p.value for p in self.phones)
        birthday = self.birthday.value.strftime(
            '%d.%m.%Y') if self.birthday else "N/A"
        return f"Contact name: {self.name.value}, phones: {phones}, birthday: {birthday}"


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name, None)

    def delete(self, name):
        if name in self.data:
            del self.data[name]
            return True
        return False

    def get_upcoming_birthdays(self, days=7):
        today = datetime.now().date()
        end_date = today + timedelta(days=days)
        upcoming_birthdays = []
        for record in self.data.values():
            if record.birthday:
                next_birthday = record.birthday.value.replace(year=today.year)
                if today <= next_birthday <= end_date:
                    upcoming_birthdays.append(record)
                elif today > next_birthday:
                    next_birthday = record.birthday.value.replace(
                        year=today.year + 1)
                    if today <= next_birthday <= end_date:
                        upcoming_birthdays.append(record)
        return upcoming_birthdays

# Функції обробники


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return str(e)
        except IndexError:
            return "Not enough arguments, try again."
        except KeyError:
            return "Contact not found."
    return inner


@input_error
def add_contact(args, book):
    if len(args) < 2:
        raise ValueError("Not enough arguments. Use: add <name> <phone>")
    name = args[0]
    phones = args[1:]
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    for phone in phones:
        record.add_phone(phone)
    return message


@input_error
def change_contact(args, book):
    if len(args) != 3:
        raise ValueError("Use: change <name> <old phone> <new phone>")
    name, old_phone, new_phone = args
    record = book.find(name)
    if not record:
        raise KeyError
    record.edit_phone(old_phone, new_phone)
    return "Contact updated."


@input_error
def get_phone(args, book):
    if len(args) != 1:
        raise ValueError("Use: phone <name>")
    name = args[0]
    record = book.find(name)
    if not record:
        raise KeyError
    return "; ".join(phone.value for phone in record.phones)


@input_error
def list_contacts(args, book):
    if args:
        raise ValueError("Use: all")
    if not book.data:
        return 'Contacts are empty.'
    result = ''
    for name, record in book.data.items():
        result += f'{record}\n'
    return result.strip()


@input_error
def add_birthday(args, book):
    if len(args) != 2:
        raise ValueError("Use: add-birthday <name> <DD.MM.YYYY>")
    name, birthday = args
    record = book.find(name)
    if not record:
        raise KeyError
    record.add_birthday(birthday)
    return "Birthday added."


@input_error
def show_birthday(args, book):
    if len(args) != 1:
        raise ValueError("Use: show-birthday <name>")
    name = args[0]
    record = book.find(name)
    if not record:
        raise KeyError
    if record.birthday:
        return f"{record.name.value}'s birthday is on {record.birthday.value.strftime('%d.%m.%Y')}"
    return "Birthday not set."


@input_error
def birthdays(args, book):
    if args:
        raise ValueError("Use: birthdays")
    upcoming = book.get_upcoming_birthdays(7)
    if not upcoming:
        return "No upcoming birthdays."
    result = ''
    for record in upcoming:
        result += f'{record}\n'
    return result.strip()

# Головна функція


def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, args


def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

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
            print(get_phone(args, book))

        elif command == "all":
            print(list_contacts(args, book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        else:
            print("Invalid command. Available commands: add (name phone), phone (name), change (name old_phone new_phone), add-birthday (name DD.MM.YYYY), show-birthday (name), birthdays, all, hello, exit, close.")


if __name__ == '__main__':
    main()
