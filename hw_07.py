from collections import UserDict
from datetime import datetime, timedelta


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Please provide both name and phone."
        except KeyError:
            return "Contact not found."
        except IndexError:
            return "Please provide a name."
    return inner


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")


class Name(Field):
    def __init__(self, value):
        if not value:
            raise ValueError("Name cannot be empty.")
        super().__init__(value)


class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone number must contain exactly 10 digits.")
        super().__init__(value)


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def __str__(self):
        birthday_str = self.birthday.value.strftime("%d.%m.%Y") if self.birthday else "N/A"
        return (f"Contact name: {self.name.value}, "
                f"phones: {'; '.join(p.value for p in self.phones)}, "
                f"birthday: {birthday_str}")

    def add_phone(self, phone: str):
        self.phones.append(Phone(phone))

    def find_phone(self, phone: str):
        return next((p for p in self.phones if p.value == phone), None)

    def edit_phone(self, old_phone: str, new_phone: str):
        phone_obj = self.find_phone(old_phone)
        if phone_obj:
            phone_obj.value = Phone(new_phone).value
        else:
            raise ValueError(f"Phone {old_phone} not found.")

    def remove_phone(self, phone: str):
        phone_obj = self.find_phone(phone)
        if phone_obj:
            self.phones.remove(phone_obj)
        else:
            raise ValueError(f"Phone {phone} not found.")

    def add_birthday(self, birthday: str):
        self.birthday = Birthday(birthday)


class AddressBook(UserDict):
    def add_record(self, record: Record):
        self.data[record.name.value] = record

    def find(self, name: str):
        return self.data.get(name)

    def delete(self, name: str):
        if self.find(name):
            self.data.pop(name)
        else:
            raise KeyError(f"Record '{name}' not found.")

    def get_upcoming_birthdays(self) -> list:
        today = datetime.today().date()
        upcoming = []

        for record in self.data.values():
            if not record.birthday:
                continue

            birthday_this_year = record.birthday.value.replace(year=today.year)

            if birthday_this_year.weekday() >= 5:
                birthday_this_year += timedelta(days=(7 - birthday_this_year.weekday()))

            if birthday_this_year < today or birthday_this_year - today > timedelta(days=7):
                continue

            upcoming.append({
                "name": record.name.value,
                "congratulation_date": birthday_this_year.strftime("%d.%m.%Y")
            })

        return upcoming


def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args


@input_error
def add_contact(args, book):
    if len(args) < 2 or not args[-1].isdigit() or len(args[-1]) != 10:
        raise ValueError

    *name_parts, phone = args
    name = " ".join(name_parts)

    record = book.find(name)
    message = "Contact updated."

    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."

    record.add_phone(phone)
    return message


@input_error
def change_contact(args, book):
    *name_parts, old_phone, new_phone = args
    name = " ".join(name_parts)

    if not name or not old_phone.isdigit() or not new_phone.isdigit():
        raise ValueError

    record = book.find(name)
    if not record:
        return "There is no such contact, please use 'add' command instead."

    record.edit_phone(old_phone, new_phone)
    return f"{name}'s phone number was successfully changed."


@input_error
def show_phone(args, book):
    name = " ".join(args)
    record = book.find(name)
    if not record:
        raise KeyError
    return f"{name}'s phones: {'; '.join(p.value for p in record.phones)}"


@input_error
def show_all(book):
    if not book.data:
        return "No contacts saved yet."
    return "\n".join(str(record) for record in book.data.values())


@input_error
def add_birthday(args, book):
    *name_parts, birthday = args
    name = " ".join(name_parts)
    record = book.find(name)
    if not record:
        raise KeyError
    record.add_birthday(birthday)
    return f"Birthday added for {name}."


@input_error
def show_birthday(args, book):
    name = " ".join(args)
    record = book.find(name)
    if not record:
        raise KeyError
    if not record.birthday:
        return f"{name} has no birthday set."
    return f"{name}'s birthday: {record.birthday.value.strftime('%d.%m.%Y')}"


@input_error
def birthdays(book):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No birthdays in the next week."
    return "\n".join(f"{b['name']}: {b['congratulation_date']}" for b in upcoming)


def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ")
        if not user_input.strip():
            continue
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
            print(show_phone(args, book))
        elif command == "all":
            print(show_all(book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(args, book))
        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()