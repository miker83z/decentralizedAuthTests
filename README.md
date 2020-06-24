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

**Server**

```
$ flask run -h 0.0.0.0 -p 5022
```

**Client**
Needs nodes address in _client/nodes.txt_
Neets setting flags in _client/client.py_

```
$ cd client/
$ python client.py
```
