# PKP terminal

This project, for now, is a proof of concept aimed at delivering basic access to [polish railway timetable](http://rozklad-pkp.pl/) in unix terminal.

## Usage

Provided you've got a Python3 installed on your machine:
```
# to find out the identifiers of the train stations:
python3 pkp.py station Wrocław\ P
```
you'll get something like the following:

```
Wrocław Pawłowice [5104137]
Wrocław Popowice [5104142]
Wrocław Pracze [5104193]
Wrocław Psie Pole [5104120]
```
now to find out next connections:
```
python3 pkp.py connection 5104120 5104134
```
which should result in:
```
04:39 R66941
---
22:28 → 22:42  KD69930
04:39 → 04:53  R66941
05:04 → 05:18  KD69900
05:47 → 06:00  R60561
```
where the first line is the next departure from the chosen station and number of the train.

