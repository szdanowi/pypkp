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
Suggested departure:
04:39 → 04:53  R66941

Alternatives:
05:04 → 05:18  KD69900
05:47 → 06:00  R60561
```
where on each line in both sections there is the departure and arrival times of the train(s), and their respective number(s).

## Argos

The script is able to generate an output compatible with [Argos](https://github.com/p-e-w/argos) extension for GNOME Shell. To enable it use the `--argos` command line option:
```
python3 pkp.py --argos connection 5104120 5104134
```
This will produce an output as following:
```
04:39 R66941
---
04:39 → 04:53  R66941
05:04 → 05:18  KD69900
05:47 → 06:00  R60561
```

## Debug

Displaying debug logs on screen may be enabled with `--debug` command line option. The script should also try to dump debug logs to `pkp.py.log` file on each run.

