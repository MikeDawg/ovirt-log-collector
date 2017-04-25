#!/bin/bash -e
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

function usage() {
cat << __EOF__
Usage: $0 <tar-file> <analyzer-working-dir>

Script unpacks sosreport and prepares pg_dump for import.
__EOF__
exit 1;

}

if [ $# -ne 2 ]; then
    usage;

fi

SOS_REPORT=$1
TMP_ROOT=$2

if [[ "$TMP_ROOT" != /* ]]; then
    usage;
fi

UNPACKED_SOSREPORT="$TMP_ROOT/unpacked_sosreport"
PG_DUMP_DIR="$TMP_ROOT/pg_dump_dir"

mkdir -p $UNPACKED_SOSREPORT $PG_DUMP_DIR

echo "Unpacking postgress data. This can take up to several minutes."

tar -C "$UNPACKED_SOSREPORT" -xf "$SOS_REPORT"
TAR_WITH_POSTGRES_SOSREPORT=$(find "$UNPACKED_SOSREPORT" -name "*postgresql-sosreport*tar.xz")

tar -C "$(dirname $TAR_WITH_POSTGRES_SOSREPORT)" -Jxf "$TAR_WITH_POSTGRES_SOSREPORT"

PG_DUMP_TAR=$(tar tf "$TAR_WITH_POSTGRES_SOSREPORT" | grep "sos_pgdump.tar")

tar -Oxf "$TAR_WITH_POSTGRES_SOSREPORT" "$PG_DUMP_TAR" | tar -C "$PG_DUMP_DIR" -x

cd "$PG_DUMP_DIR"
sed -i "s#\\\$\\\$PATH\\\$\\\$#$PWD#g" restore.sql
chmod o+r *
chmod o+rx ./


echo "sos-report extracted into: $UNPACKED_SOSREPORT";
echo "pgdump extracted into: $PG_DUMP_DIR";