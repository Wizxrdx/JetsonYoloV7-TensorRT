import serial
import pynmea2

class GPSLocation:
    def __init__(self):
        self.__gps = serial.Serial(
            port='/dev/ttyTHS1',
            baudrate=9600,
            timeout=0.5
        )

    def can_get_location(self):
        raw_data = self.__read_gps()
        parsed_data = self.__parse_data(raw_data)
        if parsed_data is not None:
            return True
        return False

    def current_location(self):
        if self.can_get_location():
            raw_data = self.__read_gps()
            parsed_data = self.__parse_data(raw_data)
            if parsed_data is not None:
                print(parsed_data)
                gga_lon = float(parsed_data['longitude'])
                gga_lon_dir = parsed_data['longitude_dir']
                gga_lat = float(parsed_data['latitude'])
                gga_lat_dir = parsed_data['latitude_dir']

                dec_lon = self.__gga_to_decimal(gga_lon, gga_lon_dir)
                dec_lat = self.__gga_to_decimal(gga_lat, gga_lat_dir)

                print(f'https://www.openstreetmap.org/search?query={dec_lon}%2C{dec_lat}')

                return dec_lat, dec_lon

    def close(self):
        self.__gps.close()

    def __read_gps(self):
        data = self.__gps.readline().decode('ascii', errors='replace').split()
        return data

    def __parse_data(self, data):
        for line in data:
            if line.find('GGA') > 0:
                msg = pynmea2.parse(line)
                return {
                    'timestamp': msg.timestamp,
                    'latitude': msg.lat,
                    'latitude_dir': msg.lat_dir,
                    'longitude': msg.lon,
                    'longitude_dir': msg.lon_dir,
                    'altitude': msg.altitude,
                    'altitude_units': msg.altitude_units
                }
        return None

    def __gga_to_decimal(self, gga_coord, direction):
        degrees = int(gga_coord / 100)
        minutes = gga_coord % 100
        decimal = degrees + (minutes / 60)

        if direction in ['S', 'W']:
            decimal *= -1

        return decimal