"""
Code retrieved from https://www.youtube.com/watch?v=ve2pmm5JqmI&list=PL-osiE80TeTskrapNbzXhwoFUiLCjGgY7&index=14
"""
import os

os.chdir('/path/to/files/')

# Am I in the correct directory?
# print(os.getcwd())

# print(dir(os))

# Print all the current file names
for f in os.listdir():
    # If .DS_Store file is created, ignore it
    if f == '.DS_Store':
        continue

    f_name, f_ext = os.path.splitext(f)
    # print(f_name)

    # One way to do this
    f_title, f_course, f_number = f_name.split('-')

    # Need to remove whitespace
    f_title = f_title.strip()
    f_course = f_course.strip()

    # Want to remove the number sign?
    # f_number = f_number.strip()[1:]

    # One thing I noticed about this output is that if it was sorted by filename
    # then the 1 and 10 would be next to each other. How do we fix this? One way we can fix this is to pad
    # the numbers. So instead of 1, we'll make it 01. If we had hundreds of files then this would maybe need to be 001.
    # We can do this in Python with zfill
    f_number = f_number.strip()[1:].zfill(2)

    # print('{}-{}-{}{}'.format(f_number, f_course, f_title, f_ext))


    new_name = '{}-{}{}'.format(f_number, f_title, f_ext)

    os.rename(f, new_name)


# print(len(os.listdir()))