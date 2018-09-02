#!/usr/bin/env python3
import os

LN_MAP = {
    '~/.Xresources': 'Xresources',
    '~/.config/i3/config': 'i3/config',
    '~/.config/i3status/config': 'i3/i3status.conf',
    '~/.config/redshift.conf': 'redshift/redshift.conf',
    '~/.config/nvim/init.vim': 'vim/init.vim',
}
def main():
    dotfiles_dir = os.path.dirname(__file__)
    for r_dest, r_src in LN_MAP.items():
        a_dest = os.path.abspath(os.path.expanduser(r_dest))
        a_src = os.path.abspath(os.path.join(dotfiles_dir, r_src))
        src_exists = os.path.exists(a_src)
        dest_exists = os.path.exists(a_dest)
        if dest_exists and os.path.samefile(a_dest, a_src):
            print(f'{a_dest} EXISTS')
        else:
            dest_dir = os.path.dirname(a_dest)
            if os.path.exists(dest_dir):
                if os.path.isfile(dest_dir):
                    print(f'Error: {dest_dir} is not directory')
                    return
            else:
                os.makedirs(dest_dir)
            os.symlink(a_src, a_dest)
            print(f'{a_dest} DONE')

if __name__ == '__main__':
    main()

