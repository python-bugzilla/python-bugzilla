#!/bin/bash

export PYTHONPATH="..:"$(python -c 'import sys; print ":".join(sys.path)')
bz="../bin/bugzilla --bugzilla https://partner-bugzilla.redhat.com/xmlrpc.cgi $@"
#bugid=710425

if [ -z "$bugid" ]; then
    echo "creating new bug..."
    bugid=$($bz new -p Fedora -v rawhide -c python-bugzilla --ids \
      --summary "python-bugzilla self-test bug" \
      --comment "this is a python-bugzilla self-test, please ignore")
fi

echo -e '\nattaching a file...'
echo 'Testing with some UTF8 data. Compose-C-C-C-P: ☭' > attach1.txt
$bz attach --file attach1.txt --desc "test file" $bugid

echo -e '\nattaching data from stdin...'
echo 'Testing with more UTF8 data. Compose-\-o-/: 🙌' | tee stdin.txt | \
    $bz attach --file attach2.txt --desc "test stdin" $bugid

echo -e '\nattaching a file with non-ascii filename...'
echo 'Testing with a UTF8 filename.' > ♥.txt
$bz attach --file ♥.txt --desc "♥.txt" $bugid

echo -e '\nfetching attachments...'
$bz attach --getall $bugid

echo -e '\nchecking attachments...'
for pair in "attach1.txt attach1.txt.1" "attach2.txt stdin.txt" "♥.txt ♥.txt.1"; do
    if cmp -s $pair; then
        rm $pair
    else
        echo "files not equal: $pair"
    fi
done

echo -e '\ndone.'
