#!/bin/bash

USERNAME="mirko.zichichi"
HOSTS=(`cat "nodes.txt"`)

NUMBER_OF_NODES=`cat test_network/size`
echo "Stopping $NUMBER_OF_NODES nodes"

for (( i = 2; i <= $NUMBER_OF_NODES; i++ )) ; do
  ssh -f -o StrictHostKeyChecking=no -l $USERNAME ${HOSTS[$i]} "killall parity"
done

