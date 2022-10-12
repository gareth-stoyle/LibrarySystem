import csv
import json
import time
from datetime import date


class Notification(object):
    """Class represents the notification system"""

    def sendEmail(self, msg):
        '''
        Dummy function to notify a subject.

        Arguments:
            msg: the notificaiton message (string)
        '''
        print(msg)

    def notify_fine(self, member_id, book_id, amount):
        '''
        Notifies a member of a fine due.

        Arguments:
            member_id: member's ID (string)
            book_id: book's ID (string)
            amount: the notificaiton message (int)
        '''
        msg = ('Member:', member_id, 'owes £', amount, 'for overdue book ID:', book_id)
        self.sendEmail(msg)

    def notify_reserver(self, member_id, book_id):
        '''
        Notifies a member of a reservation available.

        Arguments:
            member_id: member's ID (string)
            book_id: book's ID (string)
        '''
        msg = ('book:', book_id, 'available now for:', member_id)
        self.sendEmail(msg)

    def notify_book_order(self, member_id, book_id):
        '''
        Notifies a member of a requested books availability.

        Arguments:
            member_id: member's ID (string)
            book_id: book's ID (string)
        '''
        msg = ('book:', book_id, 'requested by:',
               member_id, 'is now stocked in the library')
        self.sendEmail(msg)


class Library(Notification):
    """
    Class represents the library system
    Inherits from notification system.
    """

    def __init__(self):
        """
        Initialise library object by opening all json files
        and extracting data to variables
        """
        f = open('members.json')
        self.members = json.load(f)
        f.close()
        f = open('books.json')
        self.books = json.load(f)
        f.close()
        f = open('bookloans.json')
        self.bookloans = json.load(f)
        f.close()
        f = open('reservations.json')
        self.reservations = json.load(f)
        f.close()
        f = open('membership_requests.json')
        self.membership_requests = json.load(f)
        f.close()

    def json_add(self, file, data):
        '''
        Creates a json file and adds data to it
        Arguments:
            file: a .json file (string)
            data: the data to be dumped into the file (data structure)
        '''
        with open(file, 'w') as f:
            json.dump(data, f)

    def epoch_converter():
        '''
        Returns the days since the excel epoch as per the case study guidelines
        Returns:
            days_since: number of days since the excel epoch (string)
        '''
        unix_epoch = date(1900, 1, 1)
        xl_epoch = date(1970, 1, 1)
        # get the difference between the xl and unix epoch
        epoch_diff = xl_epoch - unix_epoch
        # add this difference to the number of days since the unix epoch
        days_since = str((int(time.time()) // (60 * 60 * 24)) + epoch_diff.days)
        return days_since

    def fine_check(self, book_id, member_id):
        for line in self.bookloans:
            # check if book was returned today
            if line[3] == Library.epoch_converter():
                # check if it was the given book_id
                if line[0] == book_id:
                    # check if it was the given member_id
                    if line[1] == member_id:
                        # check if it was loaned greater than 14 days ago
                        if int(line[3]) - int(line[2]) > 14:
                            # fine amount is £1 so no. of days late will be passed
                            # as the amount argument
                            amount = ((int(line[3]) - int(line[2])) - 14)
                            # notify member with appropriate arguments
                            self.notify_fine(member_id, book_id, amount)

    def loan(self, book_id, member_id):
        '''
        Takes out a loan of a book for a member
        Arguments:
            book_id: a book id (string)
            member_id: a member id (string)
        '''
        # create objects to represent the given member and book id's
        member = Member(member_id)
        book = Book(book_id)
        # check book availability
        available = book.get_availability()
        if available == False:
            print("Error: book is on loan")
            return
        # check books reserved status
        reserved = book.get_reserve_status()
        if reserved != '0':
            if reserved != member.id:
                print("Error: book reserved by another member")
                return
        # check members book loans is not >= 5
        book_loans = member.get_books_loaned()
        if book_loans >= 5:
            print("Error: too many books on loan")
            return
        # get days since excel epoch
        loan_date = Library.epoch_converter()
        # add new bookloan to bookloans list & save to json
        self.bookloans.append([book_id, member_id, loan_date, '0'])
        self.json_add('bookloans.json', self.bookloans)
        # delete book reservation if it exists in reservations.json and save file
        self.reservations = book.del_reservation()
        self.json_add('reservations.json', self.reservations)
        # confirm loan
        print("Book: ", book.title, " loaned to: ", member.fname, member.lname)

    def return_book(self, book_id, member_id):
        '''
        Returns a book for a given member
        Arguments:
            book_id: a book id (string)
            member_id: a member id (string)
        '''
        # create objects to represent the given member and book id's
        member = Member(member_id)
        book = Book(book_id)
        # check book exists
        exists = book.book_check()
        if exists == False:
            print("Error: book doesn't exist, contact librarian!")
            return
        # check book is on loan
        on_loan = book.get_availability()
        if on_loan == True:
            print("Error: book is not on loan, contact Librarian!")
            return
        # edit bookloans list with new return date & save to json
        self.bookloans = book.add_return_date()
        self.json_add('bookloans.json', self.bookloans)
        # check if fine is necessary
        self.fine_check(book_id, member_id)
        # check for book reservation
        reserver = book.get_reserve_status()
        if reserver != '0':
            self.notify_reserver(reserver, book_id)
        # confirm return
        print("Book: ", book.title, " returned by: ", member.fname, member.lname)

    def get_card_no(self, email):
        '''
        Returns the appropriate card number
        for the new or current member.

        Arguments:
        email: email (string)
        Returns:
            key: the membership id (string)
        '''
        for k in self.members:  # perform reverse lookup to find member
            if self.members[k][3] == email:  # search for member id
                cardno = int(self.members[k][4][-1])
                new_cardno = str(cardno + 1)  # increment cardno by 1
                k = k + new_cardno  # rejoin the string with id + new_cardno
                return k
        keys_list = list(self.members.keys())  # otherwise return a new id that
        id = str(int(max(keys_list[1:], key=int)) + 1)
        k = id + '1'
        return k

    def membership_apply(self, fname, lname, gender, email):
        '''
        Adds a membership application to the
        applications list for processing.

        Arguments:
        fname: first name (string)
        lname: last name (string)
        gender: gender (string)
        email: email (string)

        Returns:
            confirmation message.
        '''
        card_no = self.get_card_no(email)  # get appropriate card number
        member_id = card_no[0:-1]  # get member's id from card_no
        self.membership_requests[member_id] = [  # add member to requests dict
            fname, lname, gender, email, card_no
        ]
        self.members[member_id] = [  # add member to members dict
            fname, lname, gender, email, '0'  # cardno set to 0 while waiting
        ]
        # save both to json
        self.json_add('membership_requests.json', self.membership_requests)
        self.json_add('members.json', self.members)
        print('Membership request made on behalf of: ', email, ' with member id: ', member_id)

    def issue_card(self, member_id):
        '''
        Adds new members to members file once
        their card is available.

        Arguments:
        member_id: member's id (string)
        Returns:
            confirmation message.
        '''
        try:
            new_mem = self.membership_requests.pop(member_id)  # pop member from requests list
        except:
            print("Invalid ID")
            return
        self.members[member_id] = new_mem  # add new member to members
        # dict with correct card no
        # save both updated dicts to json
        self.json_add('membership_requests.json', self.membership_requests)
        self.json_add('members.json', self.members)
        print('Card issued to: ', new_mem[3], ' with card_ number: ', new_mem[4])

    def add_reservation(self, member_id, book_id):
        '''
        Adds a reservation to the reservations list.

        Returns:
            confirmation message.
        '''
        member = Member(member_id)
        book = Book(book_id)
        r_status = book.get_reserve_status()  # check if book is reserved
        if r_status == member_id:  # error if reserved by this member
            print("Error: You have already reserved this book.")
            return
        elif r_status != '0':  # error if reserved by other member
            print("Error: Book reserved by another member.")
            return
        self.reservations.append([member_id, book_id, Library.epoch_converter()])
        self.json_add('reservations.json', self.reservations)
        available = book.get_availability()
        if available == True:
            print(book.title, 'reserved for',
                  member.fname, member.lname,
                  'and is available for loan now.')
        else:
            print(book.title, 'reserved for',
                  member.fname, member.lname,
                  'and an email will be sent on availability.')


class Member(Library):
    """Represents a member, inheriting from library class"""

    def __init__(self, member_id):
        """
        Initialise Member object by inheriting from library,
        to use json extracted data structures, and defining attributes.

        Attributes:
        fname: first name (string)
        lname: last name (string)
        gender: gender (string)
        email: email (string)
        cardno: member card number (string)
        """
        Library.__init__(self)
        self.id = member_id

        # retrieve these variables from given dict
        self.fname = self.members[member_id][0]
        self.lname = self.members[member_id][1]
        self.gender = self.members[member_id][2]
        self.email = self.members[member_id][3]
        self.cardno = self.members[member_id][4]

    def __str__(self):
        """
        String method to print object for testing purposes.
        """
        return '''%s is a member with
        id: %s, last name: %s, gender: %s, 
        email: %s & card number: %s''' % (self.fname, self.id, self.lname,
                                          self.gender, self.email, self.cardno)

    def scan():
        """
        Returns the member id.

        Returns:
            member_id: member id (string)
        """
        return member_id

    def get_books_loaned(self):
        '''
        Returns the number of book loans a member currently has.

        Returns:
            count: number of current member bookloans (int)
        '''
        count = 0
        for line in self.bookloans:
            # increase count if it finds the member id and the loan return == '0'
            if line[1] == self.id and line[3] == '0':
                count += 1
        return count


class Book(Library):
    def __init__(self, book_id):
        """
        Initialise Book object by inheriting from library,
        to use json extracted data structures, and defining attributes.

        Attributes:
        book_id, title, author, genre, subgenre, pub
        """
        Library.__init__(self)
        self.book_id = book_id

        # retrieve these variables from given dict
        self.title = self.books[book_id][0]
        self.author = self.books[book_id][1]
        self.genre = self.books[book_id][2]
        self.subgenre = self.books[book_id][3]
        self.pub = self.books[book_id][4]

    def __str__(self):
        """
        String method to print object for testing purposes.
        """
        return '''%s is a book with
        number: %s, author: %s, genre: %s, 
        subgenre: %s & publisher: %s''' % (self.title, self.book_id, self.author,
                                           self.genre, self.subgenre, self.pub)

    def scan():
        """
        Returns the book id.

        Returns:
            book_id: book id (string)
        """
        return book_id

    def get_availability(self):
        '''
        Returns the availability of a book based on the last instance
        of the book in the book loans data.

        Returns:
            availability: the availability of the book (boolean)
        '''
        # traverse bookloans data
        for line in self.bookloans:
            # check if book id matches this object
            if line[0] == self.book_id:
                # check if this instance of this book id's loan is still on loan
                if line[3] == '0':
                    # set availability to false
                    self.availability = False
                else:
                    # otherwise, availbility is true
                    self.availability = True
        return self.availability

    def get_reserve_status(self):
        '''
        Returns the reserve status of the book object.

        Returns:
            reserve_status: the id of the reserving member,
            or '0' if not reserved (string)
        '''
        self.reserve_status = '0'
        for line in self.reservations:
            # traverse the reservations list, looking for the book id.
            if line[1] == self.book_id:
                # change the reserve status to the member's id
                self.reserve_status = line[0]
        return self.reserve_status

    def del_reservation(self):
        '''
        Deletes a reservation from the reservations list.

        Returns:
            the reservations list without the deleted list item (data structure)
        '''
        # traverse the reservations list
        for line in self.reservations:
            # if book id exists in the list
            if line[1] == self.book_id:
                # delete the reservation list
                del self.reservations[self.reservations.index(line)]
                return self.reservations
            return self.reservations

    def book_check(self):
        '''
        Checks for the existence of a book in the system

        Returns:
            exists: whether or not the book exists (boolean)
        '''
        if self.book_id in self.books:
            return True
        else:
            return False

    def add_return_date(self):
        '''
        Changes the bookloan item's return date to a given date

        Returns:
            bookloans: the updated bookloans list (data structure)
        '''
        return_date = Library.epoch_converter()
        # traverse bookloans data
        for line in self.bookloans:
            # check if book id matches this object
            if line[0] == self.book_id:
                # check if this instance of this book id's loan is still on loan
                if line[3] == '0':
                    # change return date
                    self.bookloans[self.bookloans.index(line)][3] = return_date
        return self.bookloans


a = Library()
