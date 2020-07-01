from pytz import timezone, utc
import dateutil.parser


class WikiTime(object):
    pst = timezone('America/Los_Angeles')
    cet = timezone('Europe/Berlin')
    kst = timezone('Asia/Seoul')
    
    def __init__(self, timestamp: str, default_timezone: timezone = utc):
        self.timestamp = timestamp
        timestamp_parsed = dateutil.parser.parse(timestamp)
        if timestamp_parsed.tzinfo is None:
            timestamp_parsed = default_timezone.localize(timestamp_parsed)
        self.pst_object = timestamp_parsed.astimezone(self.pst)
        self.cet_object = timestamp_parsed.astimezone(self.cet)
        self.kst_object = timestamp_parsed.astimezone(self.kst)
        self.pst_date = self.pst_object.strftime('%Y-%m-%d')
        self.cet_date = self.cet_object.strftime('%Y-%m-%d')
        self.kst_date = self.kst_object.strftime('%Y-%m-%d')
        self.pst_time = self.pst_object.strftime('%H:%M')
        self.cet_time = self.cet_object.strftime('%H:%M')
        self.kst_time = self.kst_object.strftime('%H:%M')
        self.dst = self._determine_dst()
    
    def _determine_dst(self):
        is_dst_pst = self.pst_object.dst()
        is_dst_cet = self.cet_object.dst()
        if is_dst_pst and is_dst_cet:
            return 'yes'
        elif is_dst_pst:
            return 'spring'
        else:
            return 'no'
