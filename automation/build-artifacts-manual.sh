#!/bin/bash -xe
[[ -d exported-artifacts ]] \
|| mkdir -p exported-artifacts

[[ -d tmp.repos ]] \
|| mkdir -p tmp.repos

autoreconf -ivf
./configure
yum-builddep ovirt-log-collector.spec
# Run rpmbuild, assuming the tarball is in the project's directory
rpmbuild \
    -D "_topdir $PWD/tmp.repos" \
    -ta ovirt-log-collector-*.tar.gz

mv *.tar.gz exported-artifacts
find \
    "$PWD/tmp.repos" \
    -iname \*.rpm \
    -exec mv {} exported-artifacts/ \;
