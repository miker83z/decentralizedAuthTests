# umbralPre

Umbral Proxy Re-Encryption network test

---

## Installing

**(virtual environment, >= python3.6)**

```
$ git clone https://github.com/miker83z/umbralPre/
$ cd umbralPre
$ virtualenv -p python3 venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

## Running

### Server

```
$ flask run -h 0.0.0.0 -p 5022
```

### Client

Needs nodes address in _client/nodes.txt_ and setting flags in _client/client.py_

```
$ cd client/
$ python client.py
```

### Complete Test

First teminal:

```
$ cd test/
$ ./start.sh
```

Second terminal:

```
$ cd client/
$ python client.py
```

#### Flags (client)

- _-m --message_ : varying on message size
- _-x --fixed_ : varying on message sizes -> [10, 50, 100, ..., 500000, 1000000]
- _-l --latency_ : show each latency
- _-d --debug_ : show debugging messages
- _-t --threshold \<value>_ : assign this threshold value (only if varying message)
- _-s --step \<value>_ : start from this value and increment with step of this value (treshold and message size)
- _-f --final \<value>_ : final iteration value (threshold and message size)
