# Personal Data Decentralized Access Control tests

This project was built with the purpose of assessing the feasibility of lesser-used cryptographic methods in the field of access control, with particular attention to personal information.

---

## Composition

The project is composed of two softwares used to test different methods:

- In `/openethereumSSauth` an implementation of a framework based on the [OpenEthereum Secret Store](https://openethereum.github.io/wiki/Secret-Store) can be found.
- The `/umbralPREauth` directory contains the code that allows to create a network of proxies that execute the [Umbral Proxy Re-Encryption](https://github.com/nucypher/umbral-doc/blob/master/umbral-doc.pdf) algorithm. 

The datasets containing the results of tests executed using the above softwares, together with data plots, can be found in `/benchmarks`.