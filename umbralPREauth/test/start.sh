#!/bin/bash

USERNAME="mirko.zichichi"
NODES_FILE="../client/nodes.txt" 
HOSTS=(`cat available-nodes.txt`)
NUMBER_OF_NODES=$1

function finish {
  sleep 0
}

trap finish SIGINT

if [ "$1" = "" ] ; then
  NUMBER_OF_NODES=25
fi

rm $NODES_FILE
echo "127.0.0.1" >> $NODES_FILE
for (( i = 1; i < $NUMBER_OF_NODES; i++ ))
do
  echo "Starting ${HOSTS[$i]}"
  echo "${HOSTS[$i]}" >> $NODES_FILE
  ssh -o StrictHostKeyChecking=no -l $USERNAME ${HOSTS[$i]} "./netest.sh"
done

cd ..
source venv/bin/activate
cd server
flask run -h 0.0.0.0 -p 5022

for (( i = 1; i < $NUMBER_OF_NODES; i++ ))
do
  echo "Closing ${HOSTS[$i]}"
  ssh -o StrictHostKeyChecking=no -l $USERNAME ${HOSTS[$i]} "killall flask"
done
