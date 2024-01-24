import caldav
from urllib.parse import urlparse
import sys, os
from webdav3.client import Client as WebdavClient
import tempfile

ical_start = 'BEGIN:VCALENDAR'
ical_end = 'END:VCALENDAR'

def print_calendars_demo(calendars):
    """
    This example prints the name and URL for every calendar on the list
    """
    if calendars:
        ## Some calendar servers will include all calendars you have
        ## access to in this list, and not only the calendars owned by
        ## this principal.
        print("your principal has %i calendars:" % len(calendars))
        for c in calendars:
            print("    Name: %-36s  URL: %s" % (c.name, c.url))
    else:
        print("your principal has no calendars")

def get_caldav():
    caldav_uri = sys.argv[1]
    output_server = sys.argv[2]
    output_dir = sys.argv[3]
    uri_obj = urlparse(caldav_uri)

    print('caldav_uri:', caldav_uri)

    with caldav.DAVClient(
            url=caldav_uri,
            username=uri_obj.username,
            password=uri_obj.password,
    ) as client:
        my_principal = client.principal()
        calendars = my_principal.calendars()

        print_calendars_demo(calendars)

        calendar = client.calendar(url=calendars[0].url)
        children = calendar.children()

        out = ""

        for child in children:
            event_url, _, event_name = child
            print('event:', event_name, event_url)

            event_item = calendar.event_by_url(event_url)
            event_item.load()
            out += event_item.data + '\n'

    out = out.replace(ical_start, '').replace(ical_end, '')
    out = '\n'.join([ical_start, out, ical_end])
    # 创建一个临时文件
    fd, path = tempfile.mkstemp()

    try:
        # 写入数据
        with os.fdopen(fd, 'w+t') as tmp:
            tmp.write(out)
            tmp.flush()
            tmp.close()

            output_path_obj = urlparse(output_server)
            options = {
                'webdav_hostname': output_server,
                'webdav_login': output_path_obj.username,
                'webdav_password': output_path_obj.password
            }
            webdav_client = WebdavClient(options)
            webdav_client.upload_sync(remote_path=output_dir, local_path=path)

    finally:
        # 手动删除文件
        os.remove(path)


if __name__ == '__main__':
    get_caldav()
