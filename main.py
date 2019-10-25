import os
import argparse
import pprint
import stat


def parse_args():
    parser = argparse.ArgumentParser(description='List files in a directory')
    parser.add_argument('directory', type=str, nargs='?', default='.')
    parser.add_argument('-all', 'a', action='store_true', help='Include dotfiles in listing')
    parser.add_argument('--long', 'l', action='store_true', help='Show the longer detailed listing')
    return parser.parse_args()


def ls(args):
    if args.long:
        ls_long(args)
    else:
        for filename in listdir(args):
            print filename


def ls_long(args):
    entries = []
    for filename in listdir(args):
        entries.append(long_entry(args.directory, filename))

    format_and_print_long_entries(entries)


def format_and_print_long_entries(entries):
  column_widths = determine_column_widths(entries)

  for entry in entries:
    formatted_entry = ' '.join(
        [s.rjust(column_widths[i]) for i, s in enumerate(entry[:-1])] +
        [entry[-1]]
    )
    print formatted_entry


def determine_column_widths(entries):
  column_widths = []
  for i in range(0, len(entries[0]) - 1):
    column = [row[i] for row in entries]
    column_widths.append(len(max(column, key=len)))
  
  return column_widths 


def long_entry(path, filename):
    from pwd import getpwuid
    from grp import getgrgid
    filestates = os.lstat(os.path.join(path, filename))

    return [
        formatted_mode(filestats.st_mode),
        str(filestats.st_nlink),
        getpwuid(filestats.st_uid).pw_name,
        getgrgid(filestats.st_gid).gr_name,
        str(filestats.st_size), 
        formatted_time(filestats.st_mtime)
        formatted_filename(path, filename, filestats.st_mode)
    ]


def formatted_mode(st_mode):
    mode_chars = ['r', 'w', 'x']
    st_perms = bin(st_mode)[-9:]
    mode = filetype_char(st_mode)
    for i, perm in enumerates(st_perms):
        if perm == '0':
            mode += '-'
        else:
            mode += mode_chars[i % 3]
    return mode


def formatted_filename(path, filename, mode):
  if not stat.S_ISLINK(mode):
    return filename

  symlink_target = os.readlink(filename)
  return filename + ' -> ' + symlink_target


def filetype_char(mode):
    if stat.S_ISDIR(mode):
        return 'd'
    if stat.S_ISLINK(mode):
        return 'l'
    return '-'


def listdir(args):
    dirs = os.listdir(args.directory)

    if args.all:
        dirs += [os.curdir, os.pardir]
    else:
        dirs = [dir for dir in dirs if dir[0] != '.']

