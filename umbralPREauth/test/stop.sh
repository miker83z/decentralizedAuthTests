#!/bin/bash

USERNAME="mirko.zichichi"
HOSTS=(`cat "../client/nodes.txt"`)
NUMBER_OF_NODES=$1
for (( i = 1; i < $NUMBER_OF_NODES; i++ ))
do
  echo "${HOSTS[$i]}"
  ssh -o StrictHostKeyChecking=no -l $USERNAME ${HOSTS[$i]} "killall flask"
done