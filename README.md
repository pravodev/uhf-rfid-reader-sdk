# UHFReader18

## Simple Usage
First, Import Library to your project
```
from rfid-reader import RFIDReader

# iniate
reader = RFIDReader('socket', host="10.5.50.200", port=6000, addr="00")

#connect
reader.connect()
```

- Get Reader Information  
for get reader information such as type, max freq, etc 
```
info = reader.getInfo()
print("INFO ", info)
```
- Scan Tag
```
#scan single tag
tag = reader.scantag()
print('tag', tag)
#output: e200001b29xxx

#scan bulk tag
tags = rfid.scantags()
#output: [e200001b29xxx, e20005b29xxx]

```

# Other Method

| Command                           | Desc |
|-------------------------          |------|
| `getInfo`                         | Get reader information    |
| `getWorkMode`                     | get work mode    |
| `scantag` / `singleInventory`     |     |
| `scangs` / `inventory`            |     |
| `setFrequency`                    |     |
| `setAddress`                      |     |