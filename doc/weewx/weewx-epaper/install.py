# installer for weewx-epaper
# - cut/paste based on xstats 0.2

from setup import ExtensionInstaller

def loader():
    return WeewxEpaperInstaller()

class WeewxEpaperInstaller(ExtensionInstaller):
    def __init__(self):
        super(WeewxEpaperInstaller, self).__init__(
            version="0.1",
            name='weewx-epaper',
            description='skin to generate data for epaper display',
            author="Vince Skahan",
            author_email="vince@skahan.net",
            config={
                'StdReport': {
                    'weewx-epaper': {
                        'skin': 'weewx-epaper',
                        'HTML_ROOT': 'weewx-epaper'}}},
            files=[ ('skins/weewx-epaper', ['skins/weewx-epaper/skin.conf',
                                     'skins/weewx-epaper/index.html.tmpl'])]
            )
