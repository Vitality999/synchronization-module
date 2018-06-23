# -*- coding: utf-8 -*-
import logging
import sys
import subprocess

import sync_constants

logging.getLogger().setLevel(logging.INFO)


def svn_command(command):
    p = subprocess.Popen(command,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         shell=True)
    (output, err) = p.communicate()

    if err:
        logging.error(err.decode('cp866'))
        sys.exit('EXIT. Problem when running svn.')
    else:
        logging.info(output.decode('cp866'))
        logging.info('Svn complete! command: %s' % (command))


def commit(working_copy_path, msg):
    svn_commit = 'svn commit -m "{msg}" "{working_copy_path}"'.format(msg=msg, working_copy_path=working_copy_path)
    svn_command(svn_commit)


def add(working_copy_path):
    svn_add = 'svn add "{working_copy_path}"'.format(working_copy_path=working_copy_path)
    svn_command(svn_add)


def update(working_copy_path):
    svn_up = 'svn update "{working_copy_path}"'.format(working_copy_path=working_copy_path)
    svn_command(svn_up)


def copy(path_from, path_to, parameter=''):
    svn_up = 'svn copy "{path_from}" "{path_to}" {parameter}'.format(path_from=path_from,
                                                                     path_to=path_to,
                                                                     parameter=parameter)
    svn_command(svn_up)


if __name__ == '__main__':
    working_copy_path = sync_constants.working_copy_path
    test_file = sync_constants.test_file
    update(working_copy_path)
    copy(sync_constants.test_file, working_copy_path)