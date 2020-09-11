# Personal Data Decentralized Access Control benchmarks

We are interested in evaluating the performance of the two cryptographic schemes presented in this project. We have analysed the time needed to perform access control operations with the implementation of the system we propose.

The following results come from a series of tests executed in a network of 25 nodes, emulating real DLTs and the use cases of distributed systems.

Datasets can be found in `results`, while the python scripts used to generate the plots are in `scripts`.

---

## Plots

![Encryption and decryption latencies while varying the threshold value](dual-threshold.png 'Encryption and decryption latencies while varying the threshold value')
Encryption and decryption latencies while varying the threshold value

![Scalability of the system varying the nodes number](dual-nodes-number.png 'Scalability of the system varying the nodes number')
Scalability of the system varying the nodes number

![Latencies varying messages size](dual-message-size.png 'Latencies varying messages size')
Latencies varying messages size
