#!/usr/bin/expect

set USER [lindex $argv 0]
set PASSWD [lindex $argv 1]
set timeout -1;

spawn python3 manage.py changepassword $USER --settings=spb.settings.dev;
expect {
    "Password:" { exp_send "$PASSWD\r" ; exp_continue }
    "Password (again):" { exp_send "$PASSWD\r" ; exp_continue }
    eof
}
