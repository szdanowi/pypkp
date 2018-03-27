#!/usr/bin/env python3

import datetime
import json
import re
import sys
import urllib.request
import urllib.parse


class NullDisplay(object):
    @staticmethod
    def debug(*args, **kwargs):
        pass


class TerminalDisplay(object):
    RESET = 0
    RED = 31
    GRAY = 37

    def __init__(self):
        self.__debug = False

    def enable_debug(self):
        self.__debug = True

    def debug(self, *args, **kwargs):
        if self.__debug:
            self.__printf(*args, **kwargs, formats=[TerminalDisplay.GRAY])

    def print(self, *args, **kwargs):
        print(*args, **kwargs)

    def fatal(self, *args, **kwargs):
        self.__printf(*args, **kwargs, formats=[TerminalDisplay.RED])

    def __printf(self, *args, formats=None, sep=' '):
        formats = formats or dict()
        self.print(self.__format(*formats), sep.join(args), self.__format(self.RESET), sep='')

    def __format(self, *formats):
        return "" if len(formats) < 1 else \
               "\033[{0}m".format(";".join([str(f) for f in formats]))


class Website(object):
    def __init__(self, url, display=NullDisplay):
        self.__url = url
        self.__display = display

    def get(self, path):
        url = self.__url + path
        self.__display.debug("Attempts to load: {0}".format(url))
        response = urllib.request.urlopen(url)
        return response.read().decode('utf-8')


class PkpStation(object):
    def __init__(self, json_entry):
        self.name = json_entry['name']
        self.id = json_entry['value']

    def __str__(self):
        return "{1} [{0}]".format(self.id, self.name)

    def __repr__(self):
        return str(self)


class PkpJourney(object):
    def __init__(self, match):
        self.departure = match[0]
        self.arrival = match[1]
        self.trains = [t.replace(' ', '') for t in re.findall(r'<img .*?alt="(.*?)".*?>', match[2])]

    def train(self):
        return self.trains[0] if len(self.trains) > 0 else ""

    def __str__(self):
        return "{0} -> {1} , {2}".format(self.departure, self.arrival, ' '.join(self.trains))

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return self.__tuple() == other.__tuple()

    def __hash__(self):
        return hash(self.__tuple())

    def __tuple(self):
        return self.departure, self.arrival


class PkpTimetable(object):
    URL_SEARCH_STATION="station/search?term={0}&short=0"
    URL_SEARCH_CONNECTION= \
        "pl/tp?queryPageDisplayed=yes&REQ0JourneyStopsS0A=1" \
        "&REQ0JourneyStopsS0G={from_id}" \
        "&REQ0JourneyStopsS0ID=&REQ0JourneyStops1.0G=&REQ0JourneyStopover1=&REQ0JourneyStops2.0G=&REQ0JourneyStopover2=&REQ0JourneyStopsZ0A=1" \
        "&REQ0JourneyStopsZ0G={to_id}" \
        "&REQ0JourneyStopsZ0ID=" \
        "&date={date}&dateStart={date}&dateEnd={date}&REQ0JourneyDate={date}" \
        "&time={time}&REQ0JourneyTime={time}" \
        "&REQ0HafasSearchForw=1&existBikeEverywhere=yes&existHafasAttrInc=yes&existHafasAttrInc=yes&REQ0JourneyProduct_prod_section_0_0=1&REQ0JourneyProduct_prod_section_1_0=1&REQ0JourneyProduct_prod_section_2_0=1&REQ0JourneyProduct_prod_section_3_0=1&REQ0JourneyProduct_prod_section_0_1=1&REQ0JourneyProduct_prod_section_1_1=1&REQ0JourneyProduct_prod_section_2_1=1&REQ0JourneyProduct_prod_section_3_1=1&REQ0JourneyProduct_prod_section_0_2=1&REQ0JourneyProduct_prod_section_1_2=1&REQ0JourneyProduct_prod_section_2_2=1&REQ0JourneyProduct_prod_section_3_2=1&REQ0JourneyProduct_prod_section_0_3=1&REQ0JourneyProduct_prod_section_1_3=1&REQ0JourneyProduct_prod_section_2_3=1&REQ0JourneyProduct_prod_section_3_3=1&REQ0JourneyProduct_opt_section_0_list=0:000000&existOptimizePrice=1&existHafasAttrExc=yes&REQ0HafasChangeTime=0:1&existSkipLongChanges=0&REQ0HafasAttrExc=&REQ0HafasAttrExc=&REQ0HafasAttrExc=&REQ0HafasAttrExc=&REQ0HafasAttrExc=&REQ0HafasAttrExc=&REQ0HafasAttrExc=&REQ0HafasAttrExc=&REQ0HafasAttrExc=&REQ0HafasAttrExc=&REQ0HafasAttrExc=&REQ0HafasAttrExc=&existHafasAttrInc=yes&existHafasAttrExc=yes&wDayExt0=Pn|Wt|%C5%9Ar|Cz|Pt|So|Nd&start=start&existUnsharpSearch=yes&came_from_form=1#focus"

    def __init__(self, url="http://rozklad-pkp.pl/", display=NullDisplay):
        self.__site = Website(url, display)
        self.__display = display

    def stations(self, pattern):
        found_json = self.__site.get(self.URL_SEARCH_STATION.format(urllib.parse.quote(pattern)))
        return [PkpStation(s) for s in json.loads(found_json)]

    def connections(self, from_id, to_id, date, time):
        result_page = self.__site.get(self.URL_SEARCH_CONNECTION.format(from_id=from_id, to_id=to_id, date=date, time=time))

        matches = []
        for row in result_page.split("</tr"):
            for match in re.findall(r'ODJAZD</span><span>(\d+:\d+).*?PRZYJAZD</span><span>(\d+:\d+).*?class="products-column".*?(<img .*?alt=".*?".*?</td>)', result_page):
                j = PkpJourney(match)
                if j not in matches:
                    matches.append(j)

        return matches

    def connection(self, *args, **kwargs):
        connections = self.connections(*args, **kwargs)
        return connections[1] if len(connections) > 1 else None


class Application(object):
    def __init__(self, executable, arguments, display=TerminalDisplay()):
        self.__executable = executable or self.__class__.__name__
        self.__display = display

        if "--debug" in arguments:
            self.__display.enable_debug()
            arguments.remove("--debug")

        self.__operation = arguments[0] if arguments and len(arguments) > 0 else "help"
        self.__arguments = arguments[1:] if arguments and len(arguments) > 1 else list()
        self.__timetable = PkpTimetable(display=display)

        if self.__operation == "-h" or self.__operation == "--help" or "--help" in arguments or "-h" in arguments:
            self.__operation = "help"

    def run(self):
        operation = "run_" + self.__operation

        if not hasattr(self, operation):
            self.__display.fatal("Operation not supported: {0}".format(self.__operation))
            return

        try:
            getattr(self, operation)()
        except Exception as e:
            self.__display.fatal("Operation failed: {0}".format(self.__operation))
            self.__display.debug(str(e))

    def run_help(self):
        self.__help()

    def run_station(self):
        if len(self.__arguments) < 1:
            self.__display.fatal("Please provide requested station name")
            return

        self.__display.print("\n".join([str(e) for e in self.__timetable.stations(self.__arguments[0])]))

    def run_connection(self):
        if len(self.__arguments) < 2:
            self.__display.fatal("Please provide two station ids (from and to)")
            return

        now = datetime.datetime.now()
        date = now.strftime("%d.%m.%y")
        time = now.strftime("%H:%M")
        connections = self.__timetable.connections(self.__arguments[0], self.__arguments[1], date, time)

        self.__display.print("{0} {1}".format(connections[1].departure, connections[1].train()))
        self.__display.print("---")

        for c in connections:
            self.__display.print("{0} → {2}  {1}".format(c.departure, ", ".join(c.trains), c.arrival))

    def __help(self):
        self.__display.print(
                "Command line client for accessing polish railway timetable published on rozklad-pkp.pl",
                "",
                "Usage: {0} [command] [arguments]".format(self.__executable),
                "",
                "Available commands",
                "  help       : displays this help and exits",
                "  station    : looks for stations matching string given in parameter",
                "               needs one parameter: station name pattern",
                "  connection : looks for closest departure between given station ids",
                "               needs two parameters: from_id to_id",
                sep='\n')


if __name__ == '__main__':
    print("")
    app = Application(sys.argv[0], sys.argv[1:])
    app.run()
    print("")

