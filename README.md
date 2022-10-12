# LibrarySystem
A library system that manages book loans, membership requests and more, through JSON file manipulation.

## Usage

Add the following lines to execute various functionalities:

Take out a book loan

```python
# book number, member number
a.loan('34', '2')
```

Return a book by a member

```python
# book number, member number
a.return_book('34', '2')
```

Apply for membership

```python
# first name, last name, gender, email
a.membership_apply('Gareth', 'Stoyle', 'male', 'stoyle@gmail.com')
```

Reserve a book by a member

```python
# member number, book number
a.add_reservation('40', '119')
```


## What I Learned

- Implementation of classes and class inheritance.
- Reading and writing to JSON files.
- Testing and sanity checks.
